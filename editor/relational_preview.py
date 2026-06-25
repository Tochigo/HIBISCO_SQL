import html
from collections import defaultdict, deque

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

from django.db import connection, transaction

from editor.relational_tree import build_relational_tree


PREVIEW_LIMIT = 5


def _clean_query(sql: str) -> str:
    return sql.strip().rstrip(';').strip()


def _fetch_preview(sql: str, schema_name: str, limit: int = PREVIEW_LIMIT) -> dict:
    """
    Ejecuta una consulta parcial en modo solo lectura y devuelve un máximo de filas.
    La consulta parcial se envuelve como subconsulta para no depender de si ya trae LIMIT.
    """
    cleaned_sql = _clean_query(sql)
    quoted_schema = connection.ops.quote_name(schema_name)

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL TRANSACTION READ ONLY;")
            cursor.execute(f"SET LOCAL search_path TO {quoted_schema};")
            cursor.execute(
                f"SELECT * FROM ({cleaned_sql}) AS hibisco_preview_node LIMIT %s;",
                [limit],
            )

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

    return {
        "columns": columns,
        "rows": rows,
    }


def _join_type(join: exp.Join) -> str:
    side = join.args.get("side")
    kind = join.args.get("kind")

    parts = []

    if side:
        parts.append(str(side).lower())

    if kind:
        kind_text = str(kind).lower()

        if kind_text not in ("join", "inner"):
            parts.append(kind_text)

    join_type = " ".join(parts).strip()

    if join_type in ("", "inner"):
        return ""

    return join_type


def _join_label(join: exp.Join) -> str:
    on_expr = join.args.get("on")
    using_exprs = join.args.get("using")
    join_type = _join_type(join)

    if on_expr:
        condition = on_expr.sql(dialect="postgres")
        return f"{join_type} join[{condition}]" if join_type else f"⨝[{condition}]"

    if using_exprs:
        using_cols = ", ".join(expr.sql(dialect="postgres") for expr in using_exprs)
        return f"{join_type} join[using {using_cols}]" if join_type else f"⨝[using {using_cols}]"

    return f"{join_type} join" if join_type else "⨝"


def _aggregate_expressions(select: exp.Select) -> list:
    aggregate_exprs = []
    search_roots = []

    search_roots.extend(select.args.get("expressions") or [])

    having = select.args.get("having")
    if having and having.this:
        search_roots.append(having.this)

    seen = set()
    for root in search_roots:
        for aggregate in root.find_all(exp.AggFunc):
            sql = aggregate.sql(dialect="postgres")
            if sql not in seen:
                seen.add(sql)
                aggregate_exprs.append(aggregate)

    return aggregate_exprs


def _register_source_preview(source: exp.Expression, specs: list[dict]) -> None:
    """Registra previews para tablas y alias usados como fuentes."""
    if isinstance(source, exp.Table):
        table_name = source.name
        alias = source.alias_or_name
        source_sql = source.sql(dialect="postgres")

        if alias and alias != table_name:
            specs.append({
                "label": f"ρ[{alias}]",
                "sql": f"SELECT * FROM {source_sql}",
                "kind": "alias",
            })

        specs.append({
            "label": table_name,
            "sql": f"SELECT * FROM {source_sql}",
            "kind": "table",
        })
        return

    if isinstance(source, exp.Subquery):
        alias = source.alias_or_name
        if alias:
            specs.append({
                "label": f"ρ[{alias}]",
                "sql": f"SELECT * FROM {source.sql(dialect='postgres')}",
                "kind": "subquery_alias",
            })


def _build_select_sql(
    select_items: str,
    from_sql: str,
    where_sql: str | None = None,
    group_items: str | None = None,
    having_sql: str | None = None,
    distinct: bool = False,
    order_items: str | None = None,
    limit_sql: str | None = None,
    offset_sql: str | None = None,
) -> str:
    distinct_sql = "DISTINCT " if distinct else ""
    sql = f"SELECT {distinct_sql}{select_items} FROM {from_sql}"

    if where_sql:
        sql += f" WHERE {where_sql}"

    if group_items:
        sql += f" GROUP BY {group_items}"

    if having_sql:
        sql += f" HAVING {having_sql}"

    if order_items:
        sql += f" ORDER BY {order_items}"

    if limit_sql:
        sql += f" LIMIT {limit_sql}"

    if offset_sql:
        sql += f" OFFSET {offset_sql}"

    return sql

def _source_sql_for_from(source: exp.Expression, fallback_alias: str = "hibisco_subquery") -> str:
    source_sql = source.sql(dialect="postgres")

    if isinstance(source, exp.Subquery) and not source.alias_or_name:
        return f"{source_sql} AS {fallback_alias}"

    return source_sql

def _collect_select_specs(select: exp.Select) -> list[dict]:
    specs = []

    from_clause = select.args.get("from_")
    if not from_clause or not from_clause.this:
        return specs

    base_source = from_clause.this
    _register_source_preview(base_source, specs)

    current_from_sql = _source_sql_for_from(base_source, fallback_alias="hibisco_subquery")

    joins = select.args.get("joins") or []
    for join in joins:
        right_source = join.this
        _register_source_preview(right_source, specs)

        current_from_sql = f"{current_from_sql} {join.sql(dialect='postgres')}"
        specs.append({
            "label": _join_label(join),
            "sql": f"SELECT * FROM {current_from_sql}",
            "kind": "join",
        })

    where = select.args.get("where")
    where_sql = where.this.sql(dialect="postgres") if where and where.this else None

    if where_sql:
        specs.append({
            "label": f"σ[{where_sql}]",
            "sql": _build_select_sql("*", current_from_sql, where_sql=where_sql),
            "kind": "where",
        })

    group = select.args.get("group")
    aggregate_exprs = _aggregate_expressions(select)
    group_items = None
    grouped_sql = None

    if group and group.expressions:
        group_items = ", ".join(expr.sql(dialect="postgres") for expr in group.expressions)
        aggregate_items = ", ".join(expr.sql(dialect="postgres") for expr in aggregate_exprs)

        if aggregate_items:
            label = f"group by[{group_items}; aggregation[{aggregate_items}]]"
            select_items = f"{group_items}, {aggregate_items}"
        else:
            label = f"group by[{group_items}]"
            select_items = group_items

        grouped_sql = _build_select_sql(
            select_items,
            current_from_sql,
            where_sql=where_sql,
            group_items=group_items,
        )
        specs.append({
            "label": label,
            "sql": grouped_sql,
            "kind": "group",
        })

    elif aggregate_exprs:
        aggregate_items = ", ".join(expr.sql(dialect="postgres") for expr in aggregate_exprs)
        grouped_sql = _build_select_sql(
            aggregate_items,
            current_from_sql,
            where_sql=where_sql,
        )
        specs.append({
            "label": f"aggregation[{aggregate_items}]",
            "sql": grouped_sql,
            "kind": "aggregation",
        })

    having = select.args.get("having")
    having_sql = having.this.sql(dialect="postgres") if having and having.this else None

    if having_sql:
        # HAVING requiere que la consulta ya esté agrupada o agregada.
        if grouped_sql and group_items:
            having_preview_sql = _build_select_sql(
                "*",
                f"({grouped_sql}) AS grouped_preview",
                where_sql=None,
            )
            # Mejor preview pedagógico: ejecutar la consulta agrupada con HAVING directo.
            select_items = ", ".join(expr.sql(dialect="postgres") for expr in (select.args.get("expressions") or [])) or "*"
            having_preview_sql = _build_select_sql(
                select_items,
                current_from_sql,
                where_sql=where_sql,
                group_items=group_items,
                having_sql=having_sql,
            )
        else:
            select_items = ", ".join(expr.sql(dialect="postgres") for expr in aggregate_exprs) or "*"
            having_preview_sql = _build_select_sql(
                select_items,
                current_from_sql,
                where_sql=where_sql,
                having_sql=having_sql,
            )

        specs.append({
            "label": f"having[{having_sql}]",
            "sql": having_preview_sql,
            "kind": "having",
        })

    select_exprs = select.args.get("expressions") or []
    projection_items = ", ".join(expr.sql(dialect="postgres") for expr in select_exprs) or "*"

    projection_sql = _build_select_sql(
        projection_items,
        current_from_sql,
        where_sql=where_sql,
        group_items=group_items,
        having_sql=having_sql,
    )

    specs.append({
        "label": f"π[{projection_items}]",
        "sql": projection_sql,
        "kind": "projection",
    })

    distinct = select.args.get("distinct")
    current_sql = projection_sql

    if distinct:
        current_sql = _build_select_sql(
            projection_items,
            current_from_sql,
            where_sql=where_sql,
            group_items=group_items,
            having_sql=having_sql,
            distinct=True,
        )
        specs.append({
            "label": "distinct",
            "sql": current_sql,
            "kind": "distinct",
        })

    order = select.args.get("order")
    if order and order.expressions:
        order_items = ", ".join(expr.sql(dialect="postgres") for expr in order.expressions)
        current_sql = f"{current_sql} ORDER BY {order_items}"
        specs.append({
            "label": f"order by[{order_items}]",
            "sql": current_sql,
            "kind": "order",
        })

    limit = select.args.get("limit")
    if limit and limit.expression:
        limit_sql = limit.expression.sql(dialect="postgres")
        current_sql = f"{current_sql} LIMIT {limit_sql}"
        specs.append({
            "label": f"limit[{limit_sql}]",
            "sql": current_sql,
            "kind": "limit",
        })

    offset = select.args.get("offset")
    if offset and offset.expression:
        offset_sql = offset.expression.sql(dialect="postgres")
        current_sql = f"{current_sql} OFFSET {offset_sql}"
        specs.append({
            "label": f"offset[{offset_sql}]",
            "sql": current_sql,
            "kind": "offset",
        })

    return specs


def _collect_preview_specs(expression: exp.Expression, original_query: str) -> list[dict]:
    specs = []

    if isinstance(expression, exp.Select):
        specs.extend(_collect_select_specs(expression))

        # Recolecta previews de subconsultas internas.
        for subquery in expression.find_all(exp.Subquery):
            inner = subquery.this

            if isinstance(inner, exp.Select):
                specs.extend(_collect_select_specs(inner))

                alias = subquery.alias_or_name
                if alias:
                    specs.append({
                        "label": f"ρ[{alias}]",
                        "sql": f"SELECT * FROM {subquery.sql(dialect='postgres')}",
                        "kind": "subquery_alias",
                    })

        return specs

    if isinstance(expression, exp.Union):
        return [{"label": "∪", "sql": original_query, "kind": "set_operation"}]

    if isinstance(expression, exp.Intersect):
        return [{"label": "∩", "sql": original_query, "kind": "set_operation"}]

    if isinstance(expression, exp.Except):
        return [{"label": "−", "sql": original_query, "kind": "set_operation"}]

    return specs

def _render_tree_html(node: dict, preview_by_label: dict[str, deque], prefix: str = "", is_last: bool = True, counter=None) -> str:
    if counter is None:
        counter = {"value": 0}

    counter["value"] += 1
    fallback_node_id = f"tree_node_{counter['value']}"

    label = node.get("label", "")
    preview_queue = preview_by_label.get(label)
    preview = preview_queue.popleft() if preview_queue else None
    node_id = preview["node_id"] if preview else fallback_node_id

    connector = "└── " if is_last else "├── "
    escaped_prefix = html.escape(prefix + connector)
    escaped_label = html.escape(label)

    line = (
        f'{escaped_prefix}<span class="tree-node" data-node-id="{html.escape(node_id)}">'
        f'{escaped_label}</span>'
    )

    lines = [line]
    children = node.get("children", [])
    next_prefix = prefix + ("    " if is_last else "│   ")

    for i, child in enumerate(children):
        child_is_last = i == len(children) - 1
        lines.append(_render_tree_html(child, preview_by_label, next_prefix, child_is_last, counter))

    return "\n".join(lines)


def build_tree_preview_result(query: str, schema_name: str, limit: int = PREVIEW_LIMIT) -> dict:
    """
    Construye el árbol HTML y las vistas previas por nodo.
    Si un preview falla, no rompe la consulta principal: el nodo queda con mensaje de error.
    """
    cleaned_query = _clean_query(query)
    tree = build_relational_tree(cleaned_query)

    try:
        parsed = sqlglot.parse_one(cleaned_query, read="postgres")
        specs = _collect_preview_specs(parsed, cleaned_query)
    except ParseError:
        specs = []

    previews = {}
    preview_by_label: dict[str, deque] = defaultdict(deque)

    for index, spec in enumerate(specs, start=1):
        node_id = f"preview_node_{index}"
        label = spec["label"]

        preview_data = {
            "node_id": node_id,
            "label": label,
            "kind": spec.get("kind", "operator"),
            "sql": spec.get("sql", ""),
            "columns": [],
            "rows": [],
            "error": None,
        }

        try:
            fetched = _fetch_preview(spec["sql"], schema_name, limit=limit)
            preview_data["columns"] = fetched["columns"]
            preview_data["rows"] = fetched["rows"]
        except Exception as e:
            preview_data["error"] = str(e)

        previews[node_id] = preview_data
        preview_by_label[label].append(preview_data)

    tree_html = _render_tree_html(tree, preview_by_label)

    return {
        "tree_html": tree_html,
        "tree_previews": previews,
    }
