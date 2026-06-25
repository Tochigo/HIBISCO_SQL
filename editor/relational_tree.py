import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


def make_node(label: str, children=None) -> dict:
    return {
        "label": label,
        "children": children or []
    }


def build_relational_tree(query: str) -> dict:
    ast = sqlglot.parse_one(query)
    return _build_from_expression(ast)


def _build_from_expression(node: exp.Expression) -> dict:
    """
    Construye un árbol relacional aproximado desde cualquier expresión SQL soportada.
    La idea no es representar álgebra relacional pura perfecta, sino una versión
    pedagógica y robusta para la mayor cantidad posible de consultas SELECT.
    """

    if isinstance(node, exp.Select):
        return _build_from_select(node)

    if isinstance(node, exp.Subquery):
        inner_tree = _build_from_expression(node.this)
        alias = node.alias_or_name

        if alias:
            return make_node(f"ρ[{alias}]", [inner_tree])

        return inner_tree

    if isinstance(node, exp.Union):
        left = _build_from_expression(node.args["this"])
        right = _build_from_expression(node.args["expression"])
        return make_node("∪", [left, right])

    if isinstance(node, exp.Intersect):
        left = _build_from_expression(node.args["this"])
        right = _build_from_expression(node.args["expression"])
        return make_node("∩", [left, right])

    if isinstance(node, exp.Except):
        left = _build_from_expression(node.args["this"])
        right = _build_from_expression(node.args["expression"])
        return make_node("−", [left, right])

    if isinstance(node, exp.Table):
        alias = node.alias_or_name
        table_name = node.name

        if alias and alias != table_name:
            return make_node(f"ρ[{alias}]", [make_node(table_name)])

        return make_node(table_name)

    if isinstance(node, exp.CTE):
        alias = node.alias_or_name
        inner_tree = _build_from_expression(node.this)
        return make_node(f"cte[{alias}]", [inner_tree])

    return make_node(node.sql())


def _build_from_select(select: exp.Select) -> dict:
    """
    Orden lógico aproximado:

    WITH
    FROM / JOIN
    WHERE
    GROUP BY / AGGREGATION
    HAVING
    PROJECTION
    DISTINCT
    ORDER BY
    LIMIT
    OFFSET

    Esto permite representar consultas más complejas sin perder los símbolos
    relacionales que ya se estaban usando.
    """

    current = _build_from_from_and_joins(select)

    current = _apply_where(select, current)
    current = _apply_group_by_or_aggregation(select, current)
    current = _apply_having(select, current)
    current = _apply_projection(select, current)
    current = _apply_distinct(select, current)
    current = _apply_order_by(select, current)
    current = _apply_limit(select, current)
    current = _apply_offset(select, current)
    current = _apply_with(select, current)

    return current


def _build_from_from_and_joins(select: exp.Select) -> dict:
    from_clause = select.args.get("from_")

    if from_clause and from_clause.this:
        current = _build_from_expression(from_clause.this)
    else:
        current = make_node("UNKNOWN_SOURCE")

    joins = select.args.get("joins") or []

    for join in joins:
        right = _build_from_expression(join.this)

        on_expr = join.args.get("on")
        using_exprs = join.args.get("using")

        join_type = _get_join_type(join)

        if on_expr:
            condition = on_expr.sql()
            if join_type:
                join_label = f"{join_type} join[{condition}]"
            else:
                join_label = f"⨝[{condition}]"

        elif using_exprs:
            using_cols = ", ".join(expr.sql() for expr in using_exprs)
            if join_type:
                join_label = f"{join_type} join[using {using_cols}]"
            else:
                join_label = f"⨝[using {using_cols}]"

        else:
            if join_type:
                join_label = f"{join_type} join"
            else:
                join_label = "⨝"

        current = make_node(join_label, [current, right])

    return current


def _get_join_type(join: exp.Join) -> str:
    """
    Devuelve un nombre textual para joins que no son inner join simple.
    Así evitamos inventar símbolos nuevos.
    """

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


def _apply_where(select: exp.Select, child: dict) -> dict:
    where = select.args.get("where")

    if not where or not where.this:
        return child

    predicate = where.this.sql()
    subqueries = _extract_subquery_nodes(where.this)

    children = [child] + subqueries

    return make_node(f"σ[{predicate}]", children)


def _apply_group_by_or_aggregation(select: exp.Select, child: dict) -> dict:
    group = select.args.get("group")
    aggregate_exprs = _extract_aggregate_expressions(select)

    if group and group.expressions:
        group_items = ", ".join(expr.sql() for expr in group.expressions)

        if aggregate_exprs:
            aggregate_items = ", ".join(expr.sql() for expr in aggregate_exprs)
            return make_node(
                f"group by[{group_items}; aggregation[{aggregate_items}]]",
                [child]
            )

        return make_node(f"group by[{group_items}]", [child])

    if aggregate_exprs:
        aggregate_items = ", ".join(expr.sql() for expr in aggregate_exprs)
        return make_node(f"aggregation[{aggregate_items}]", [child])

    return child


def _apply_having(select: exp.Select, child: dict) -> dict:
    having = select.args.get("having")

    if not having or not having.this:
        return child

    predicate = having.this.sql()
    subqueries = _extract_subquery_nodes(having.this)

    children = [child] + subqueries

    return make_node(f"having[{predicate}]", children)


def _apply_projection(select: exp.Select, child: dict) -> dict:
    select_exprs = select.args.get("expressions") or []

    if not select_exprs:
        return child

    projection_items = ", ".join(expr.sql() for expr in select_exprs)

    return make_node(f"π[{projection_items}]", [child])


def _apply_distinct(select: exp.Select, child: dict) -> dict:
    distinct = select.args.get("distinct")

    if not distinct:
        return child

    return make_node("distinct", [child])


def _apply_order_by(select: exp.Select, child: dict) -> dict:
    order = select.args.get("order")

    if not order or not order.expressions:
        return child

    order_items = ", ".join(expr.sql() for expr in order.expressions)

    return make_node(f"order by[{order_items}]", [child])


def _apply_limit(select: exp.Select, child: dict) -> dict:
    limit = select.args.get("limit")

    if not limit:
        return child

    return make_node(f"limit[{limit.expression.sql()}]", [child])


def _apply_offset(select: exp.Select, child: dict) -> dict:
    offset = select.args.get("offset")

    if not offset:
        return child

    return make_node(f"offset[{offset.expression.sql()}]", [child])


def _apply_with(select: exp.Select, child: dict) -> dict:
    with_clause = select.args.get("with")

    if not with_clause:
        with_clause = select.args.get("with_")

    if not with_clause:
        return child

    cte_nodes = []

    for cte in with_clause.expressions:
        cte_nodes.append(_build_from_expression(cte))

    return make_node("with", cte_nodes + [child])


def _extract_aggregate_expressions(select: exp.Select) -> list:
    """
    Busca funciones de agregación en SELECT y HAVING.

    Ejemplos:
    COUNT(*)
    AVG(nota_final)
    SUM(monto)
    MIN(edad)
    MAX(edad)
    """

    aggregate_exprs = []

    search_roots = []

    search_roots.extend(select.args.get("expressions") or [])

    having = select.args.get("having")
    if having and having.this:
        search_roots.append(having.this)

    for root in search_roots:
        for aggregate in root.find_all(exp.AggFunc):
            aggregate_exprs.append(aggregate)

    return _unique_expressions(aggregate_exprs)


def _extract_subquery_nodes(expression: exp.Expression) -> list:
    """
    Extrae subconsultas desde predicados WHERE o HAVING.

    Ejemplo:
    WHERE edad > (SELECT AVG(edad) FROM estudiantes)

    Se representa como:
    σ[edad > (...)]
    ├── estudiantes
    └── subquery
        └── ...
    """

    subquery_nodes = []

    for subquery in expression.find_all(exp.Subquery):
        subquery_nodes.append(make_node("subquery", [_build_from_expression(subquery)]))

    return subquery_nodes


def _unique_expressions(expressions: list) -> list:
    seen = set()
    unique = []

    for expr in expressions:
        sql = expr.sql()

        if sql not in seen:
            seen.add(sql)
            unique.append(expr)

    return unique


def render_tree(node: dict, prefix: str = "", is_last: bool = True) -> str:
    connector = "└── " if is_last else "├── "
    lines = [prefix + connector + node["label"]]

    children = node.get("children", [])
    next_prefix = prefix + ("    " if is_last else "│   ")

    for i, child in enumerate(children):
        child_is_last = i == len(children) - 1
        lines.append(render_tree(child, next_prefix, child_is_last))

    return "\n".join(lines)


def relational_tree_to_text(query: str) -> str:
    tree = build_relational_tree(query)
    return render_tree(tree)


if __name__ == "__main__":
    import sys


    query = sys.argv[1]

    try:
        print(relational_tree_to_text(query))
    except ParseError as e:
        print("Error de sintaxis SQL:")
        print(str(e))
    except Exception as e:
        print("Error al construir el árbol relacional:")
        print(str(e))