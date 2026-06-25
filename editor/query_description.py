import sys
import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


def _indent(level: int) -> str:
    return "  " * level


def _join_type(join: exp.Join) -> str:
    side = join.args.get("side")
    kind = join.args.get("kind")

    parts = []
    if side:
        parts.append(str(side).upper())
    if kind:
        parts.append(str(kind).upper())

    if not parts:
        return "JOIN"

    return " ".join(parts) + " JOIN"


def _source_name(source: exp.Expression) -> str:
    if isinstance(source, exp.Table):
        return source.sql()

    if isinstance(source, exp.Subquery):
        alias = source.alias_or_name
        return f"subconsulta '{alias}'" if alias else "subconsulta"

    if isinstance(source, exp.Select):
        return "subconsulta"

    return source.sql()


def _iter_child_expressions(value):
    if isinstance(value, exp.Expression):
        yield value
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, exp.Expression):
                yield item


def _unwrap_expression(expr_item: exp.Expression) -> exp.Expression:
    return expr_item.this if isinstance(expr_item, exp.Alias) else expr_item


def _is_aggregate_expression(expr_item: exp.Expression) -> bool:
    target = _unwrap_expression(expr_item)
    return isinstance(target, (exp.Avg, exp.Sum, exp.Count, exp.Min, exp.Max))


def _describe_like(left: str, pattern: str, case_insensitive: bool = False) -> str:
    suffix = " (sin distinguir mayúsculas/minúsculas)" if case_insensitive else ""

    if pattern.startswith("%") and pattern.endswith("%") and len(pattern) >= 3:
        term = pattern[1:-1]
        return f"{left} contiene '{term}'{suffix}"

    if pattern.startswith("%") and len(pattern) >= 2:
        term = pattern[1:]
        return f"{left} termina con '{term}'{suffix}"

    if pattern.endswith("%") and len(pattern) >= 2:
        term = pattern[:-1]
        return f"{left} comienza con '{term}'{suffix}"

    if "_" in pattern or "%" in pattern:
        return f"{left} coincide con el patrón '{pattern}'{suffix}"

    return f"{left} es igual a '{pattern}'{suffix}"


def _describe_condition(expr: exp.Expression) -> str:
    if isinstance(expr, exp.And):
        return f"({_describe_condition(expr.this)}) y ({_describe_condition(expr.expression)})"

    if isinstance(expr, exp.Or):
        return f"({_describe_condition(expr.this)}) o ({_describe_condition(expr.expression)})"

    if isinstance(expr, exp.Not):
        return f"no ({_describe_condition(expr.this)})"

    if isinstance(expr, exp.Like):
        left = expr.this.sql()
        right = expr.expression
        if isinstance(right, exp.Literal) and right.is_string:
            return _describe_like(left, right.this, case_insensitive=False)
        return expr.sql()

    if isinstance(expr, exp.ILike):
        left = expr.this.sql()
        right = expr.expression
        if isinstance(right, exp.Literal) and right.is_string:
            return _describe_like(left, right.this, case_insensitive=True)
        return expr.sql()

    if isinstance(expr, exp.Between):
        target = expr.this.sql()
        low = expr.args.get("low")
        high = expr.args.get("high")
        if low and high:
            return f"{target} está entre {low.sql()} y {high.sql()}"
        return expr.sql()

    if isinstance(expr, exp.In):
        target = expr.this.sql()
        values = expr.expression

        if isinstance(values, exp.Tuple):
            opciones = ", ".join(v.sql() for v in values.expressions)
            return f"{target} está en ({opciones})"

        if isinstance(values, exp.Subquery):
            return f"{target} pertenece al resultado de una subconsulta"

        if values:
            return f"{target} está en {values.sql()}"

        return expr.sql()

    if isinstance(expr, exp.Is):
        left = expr.this.sql()
        right = expr.expression
        if isinstance(right, exp.Null):
            return f"{left} es NULL"
        return f"{left} es {right.sql()}"

    if isinstance(expr, exp.EQ):
        return f"{expr.this.sql()} es igual a {expr.expression.sql()}"

    if isinstance(expr, exp.NEQ):
        return f"{expr.this.sql()} es distinto de {expr.expression.sql()}"

    if isinstance(expr, exp.GT):
        return f"{expr.this.sql()} es mayor que {expr.expression.sql()}"

    if isinstance(expr, exp.GTE):
        return f"{expr.this.sql()} es mayor o igual que {expr.expression.sql()}"

    if isinstance(expr, exp.LT):
        return f"{expr.this.sql()} es menor que {expr.expression.sql()}"

    if isinstance(expr, exp.LTE):
        return f"{expr.this.sql()} es menor o igual que {expr.expression.sql()}"

    return expr.sql()


def _validate_group_by(select: exp.Select):
    group = select.args.get("group")
    if not group:
        return

    group_cols = {expr.sql() for expr in group.expressions}
    select_exprs = select.args.get("expressions") or []

    for expr_item in select_exprs:
        target = _unwrap_expression(expr_item)

        if _is_aggregate_expression(expr_item):
            continue

        if isinstance(target, exp.Column) and target.sql() not in group_cols:
            raise ValueError(
                f"La columna '{target.sql()}' debe estar en GROUP BY o ser agregada."
            )


def _process_expression(node: exp.Expression, steps: list[str], level: int, visited: set[int]) -> None:
    node_id = id(node)
    if node_id in visited:
        return
    visited.add(node_id)

    if isinstance(node, exp.Subquery):
        alias = node.alias_or_name
        steps.append(
            f"{_indent(level)}- Evaluar la subconsulta '{alias}'."
            if alias else
            f"{_indent(level)}- Evaluar una subconsulta."
        )
        _process_expression(node.this, steps, level + 1, visited)
        return

    if isinstance(node, exp.Select):
        _process_select(node, steps, level, visited)
        return

    if isinstance(node, exp.Except):
        steps.append(f"{_indent(level)}- Resolver operación compuesta EXCEPT.")
        steps.append(f"{_indent(level)}- Devolver las filas presentes en la consulta izquierda y no en la derecha.")
        if node.args.get("this"):
            steps.append(f"{_indent(level + 1)}- Procesar conjunto izquierdo.")
            _process_expression(node.args["this"], steps, level + 2, visited)
        if node.args.get("expression"):
            steps.append(f"{_indent(level + 1)}- Procesar conjunto derecho.")
            _process_expression(node.args["expression"], steps, level + 2, visited)
        return

    if isinstance(node, exp.Intersect):
        steps.append(f"{_indent(level)}- Resolver operación compuesta INTERSECT.")
        steps.append(f"{_indent(level)}- Devolver solo las filas comunes entre ambas consultas.")
        if node.args.get("this"):
            steps.append(f"{_indent(level + 1)}- Procesar conjunto izquierdo.")
            _process_expression(node.args["this"], steps, level + 2, visited)
        if node.args.get("expression"):
            steps.append(f"{_indent(level + 1)}- Procesar conjunto derecho.")
            _process_expression(node.args["expression"], steps, level + 2, visited)
        return

    if isinstance(node, exp.Union):
        steps.append(f"{_indent(level)}- Resolver operación compuesta UNION.")
        steps.append(f"{_indent(level)}- Combinar los resultados de ambas consultas.")
        if node.args.get("this"):
            steps.append(f"{_indent(level + 1)}- Procesar conjunto izquierdo.")
            _process_expression(node.args["this"], steps, level + 2, visited)
        if node.args.get("expression"):
            steps.append(f"{_indent(level + 1)}- Procesar conjunto derecho.")
            _process_expression(node.args["expression"], steps, level + 2, visited)
        return


def _process_select(select: exp.Select, steps: list[str], level: int, visited: set[int]) -> None:
    _validate_group_by(select)

    steps.append(f"{_indent(level)}- Analizar bloque SELECT.")

    with_clause = select.args.get("with")
    if with_clause:
        for cte in with_clause.expressions or []:
            alias = cte.alias_or_name or cte.sql()
            steps.append(f"{_indent(level + 1)}- Definir CTE '{alias}'.")
            if cte.this:
                _process_expression(cte.this, steps, level + 2, visited)

    from_clause = select.args.get("from_")
    if from_clause and from_clause.this:
        source = from_clause.this
        steps.append(f"{_indent(level + 1)}- Leer datos desde {_source_name(source)}.")
        if isinstance(source, (exp.Subquery, exp.Select, exp.Union, exp.Intersect, exp.Except)):
            _process_expression(source, steps, level + 2, visited)

    joins = select.args.get("joins") or []
    for join in joins:
        source = join.this
        text = f"{_indent(level + 1)}- Aplicar {_join_type(join)} con {_source_name(source)}"
        on_expr = join.args.get("on")
        if on_expr:
            text += f" usando la condición {on_expr.sql()}"
        text += "."
        steps.append(text)

        if isinstance(source, (exp.Subquery, exp.Select, exp.Union, exp.Intersect, exp.Except)):
            _process_expression(source, steps, level + 2, visited)

    where = select.args.get("where")
    if where and where.this:
        steps.append(f"{_indent(level + 1)}- Aplicar filtro WHERE: {_describe_condition(where.this)}.")

    group = select.args.get("group")
    if group and group.expressions:
        group_cols = ", ".join(expr.sql() for expr in group.expressions)
        steps.append(f"{_indent(level + 1)}- Agrupar por: {group_cols}.")

    having = select.args.get("having")
    if having and having.this:
        steps.append(f"{_indent(level + 1)}- Aplicar filtro HAVING: {_describe_condition(having.this)}.")

    order = select.args.get("order")
    if order and order.expressions:
        order_cols = ", ".join(expr.sql() for expr in order.expressions)
        steps.append(f"{_indent(level + 1)}- Ordenar por: {order_cols}.")

    limit = select.args.get("limit")
    if limit and limit.expression:
        steps.append(f"{_indent(level + 1)}- Limitar resultado a {limit.expression.sql()} filas.")

    select_exprs = select.args.get("expressions") or []

    if any(isinstance(expr_item, exp.Star) for expr_item in select_exprs):
        steps.append(f"{_indent(level + 1)}- Proyectar todas las columnas.")
    elif select_exprs:
        columnas = []
        agregaciones = []

        for expr_item in select_exprs:
            if _is_aggregate_expression(expr_item):
                agregaciones.append(expr_item.sql())
            else:
                columnas.append(expr_item.sql())

        if agregaciones:
            steps.append(f"{_indent(level + 1)}- Calcular agregaciones: {', '.join(agregaciones)}.")

        if columnas or agregaciones:
            projections = columnas + agregaciones
            steps.append(f"{_indent(level + 1)}- Proyectar resultado: {', '.join(projections)}.")

    for key, value in select.args.items():
        if key in {"from_", "joins", "with"}:
            continue

        for child in _iter_child_expressions(value):
            for sub in child.find_all(exp.Subquery):
                _process_expression(sub, steps, level + 2, visited)


def analizar_query(query: str) -> dict:
    try:
        ast = sqlglot.parse_one(query)
        steps: list[str] = []
        visited: set[int] = set()

        if isinstance(ast, exp.Select):
            select_exprs = ast.args.get("expressions") or []
            if not select_exprs:
                query_line = query
                pointer = " " * query.upper().find("FROM") + "^"
                return {
                    "valid": False,
                    "error": f"Error de sintaxis SQL:\n{query_line}\n{pointer}",
                    "steps": [],
                }

        _process_expression(ast, steps, 0, visited)

        return {
            "valid": True,
            "error": None,
            "steps": steps,
        }

    except ParseError as e:
        details = e.errors[0] if e.errors else {}
        start = details.get("start_context", "")
        highlight = details.get("highlight", "") or "?"
        end = details.get("end_context", "")
        query_line = f"{start}{highlight}{end}"
        pointer = " " * len(start) + "^" * max(len(highlight), 1)

        return {
            "valid": False,
            "error": f"Error de sintaxis SQL:\n{query_line}\n{pointer}",
            "steps": [],
        }

    except Exception as e:
        return {
            "valid": False,
            "error": f"Error al analizar la consulta: {e}",
            "steps": [],
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Uso: python sql_test.py "SELECT * FROM users WHERE age > 18"')
        sys.exit(1)

    query = sys.argv[1]
    result = analizar_query(query)

    if result["valid"]:
        print("Consulta válida.\n")
        for step in result["steps"]:
            print(step)
    else:
        print("Consulta inválida.\n")
        print(result["error"])