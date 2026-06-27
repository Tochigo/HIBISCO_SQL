import re

import sqlglot
from sqlglot import exp
from django.core.exceptions import ValidationError


SYSTEM_SCHEMAS = {
    "information_schema",
    "pg_catalog",
    "pg_toast",
    "public",
}


FORBIDDEN_FUNCTIONS = {
    "pg_sleep",
    "pg_read_file",
    "pg_ls_dir",
    "pg_stat_file",
    "lo_import",
    "lo_export",
    "dblink",
    "version",
    "current_setting",
    "current_user",
    "session_user",
    "inet_server_addr",
    "inet_server_port",
}


def is_blocked_schema(schema_name: str | None) -> bool:
    if not schema_name:
        return False

    normalized = schema_name.lower()

    return (
        normalized in SYSTEM_SCHEMAS
        or normalized.startswith("pg_")
    )


def is_user_schema(schema_name: str | None) -> bool:
    return bool(schema_name) and not is_blocked_schema(schema_name)


def validate_user_schema(schema_name: str | None) -> None:
    if not is_user_schema(schema_name):
        raise ValidationError("Schema inválido o no permitido.")


def _is_read_only_expression(expression: exp.Expression) -> bool:
    return isinstance(expression, (
        exp.Select,
        exp.Union,
        exp.Intersect,
        exp.Except,
    ))


def validate_safe_select_query(query: str, selected_schema: str) -> None:
    validate_user_schema(selected_schema)

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValidationError("No se recibió ninguna consulta SQL.")

    try:
        statements = sqlglot.parse(cleaned_query, read="postgres")
    except Exception:
        raise ValidationError("No se pudo analizar la consulta SQL.")

    if len(statements) != 1:
        raise ValidationError("Solo se permite una consulta SQL a la vez.")

    expression = statements[0]

    if not _is_read_only_expression(expression):
        raise ValidationError("Por seguridad, solo se permiten consultas SELECT.")

    normalized_query = cleaned_query.rstrip().rstrip(";").strip()

    if ";" in normalized_query:
        raise ValidationError("Por seguridad, solo se permite una consulta SELECT a la vez.")

    for table in expression.find_all(exp.Table):
        schema_name = table.db

        if schema_name and is_blocked_schema(schema_name):
            raise ValidationError(f"No se permite consultar el esquema {schema_name}.")

    for func in expression.find_all(exp.Func):
        func_name = func.sql_name().lower()

        if func_name in FORBIDDEN_FUNCTIONS:
            raise ValidationError(f"No se permite usar la función {func_name}.")

    lowered = cleaned_query.lower()

    if re.search(r"\b(information_schema|pg_catalog|pg_toast|public)\b", lowered):
        raise ValidationError("La consulta intenta acceder a un esquema no permitido.")

    if re.search(r"\bpg_[a-zA-Z0-9_]*\b", lowered):
        raise ValidationError("La consulta intenta acceder a objetos internos de PostgreSQL.")