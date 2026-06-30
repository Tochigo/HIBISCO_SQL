import json

from django.db import connection, transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from django.core.exceptions import ValidationError

from .query_description import analizar_query
from .relational_tree import relational_tree_to_text
from .relational_preview import build_tree_preview_result
from .sql_security import (
    is_user_schema,
    validate_safe_select_query,
)

def sql_editor(request):
    return render(request, "sql_editor.html")

def _table_exists(schema_name: str, table_name: str) -> bool:
    if not is_user_schema(schema_name) or not table_name:
        return False

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_name = %s
              AND table_type = 'BASE TABLE'
            LIMIT 1;
            """,
            [schema_name, table_name],
        )
        return cursor.fetchone() is not None
    
def _get_table_key_metadata(schema_name: str, table_name: str) -> dict:
    """
    Devuelve metadatos de llaves por columna:
    {
      "id": {"primary": True, "foreign": False},
      "curso_id": {"primary": False, "foreign": True}
    }

    Se usa pg_catalog en vez de information_schema porque un usuario
    de solo lectura puede no ver correctamente las restricciones desde
    information_schema.
    """
    column_keys = {}

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                a.attname AS column_name,
                COALESCE(bool_or(c.contype = 'p'), false) AS is_primary_key,
                COALESCE(bool_or(c.contype = 'f'), false) AS is_foreign_key
            FROM pg_class t
            JOIN pg_namespace n
                ON n.oid = t.relnamespace
            JOIN pg_attribute a
                ON a.attrelid = t.oid
            LEFT JOIN pg_constraint c
                ON c.conrelid = t.oid
               AND c.contype IN ('p', 'f')
               AND a.attnum = ANY(c.conkey)
            WHERE n.nspname = %s
              AND t.relname = %s
              AND t.relkind = 'r'
              AND a.attnum > 0
              AND NOT a.attisdropped
            GROUP BY a.attnum, a.attname
            ORDER BY a.attnum;
            """,
            [schema_name, table_name],
        )

        for column_name, is_primary_key, is_foreign_key in cursor.fetchall():
            if is_primary_key or is_foreign_key:
                column_keys[column_name] = {
                    "primary": bool(is_primary_key),
                    "foreign": bool(is_foreign_key),
                }

    return column_keys


@require_GET
def list_schemas(request):
    """Devuelve los schemas visibles para el usuario de base de datos configurado en Django."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT n.nspname
                FROM pg_namespace n
                WHERE n.nspname <> 'information_schema'
                  AND n.nspname <> 'public'
                  AND n.nspname NOT LIKE 'pg_%'
                  AND has_schema_privilege(current_user, n.oid, 'USAGE')
                ORDER BY n.nspname;
            """)

            schemas = [row[0] for row in cursor.fetchall() if is_user_schema(row[0])]

        return JsonResponse({"ok": True, "schemas": schemas})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)})


@require_GET
def list_tables(request):
    """Devuelve las tablas base de un schema visible."""
    schema_name = request.GET.get("schema", "").strip()

    if not is_user_schema(schema_name):
        return JsonResponse({
            "ok": False,
            "error": "Schema inválido o no permitido.",
        })

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name;
                """,
                [schema_name],
            )
            tables = [row[0] for row in cursor.fetchall()]

        return JsonResponse({"ok": True, "schema": schema_name, "tables": tables})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)})


@csrf_exempt
@require_POST
def preview_table(request):
    """Devuelve una vista previa segura de una tabla usando schema y tabla validados."""
    try:
        body = json.loads(request.body)
        schema_name = body.get("schema", "").strip()
        table_name = body.get("table", "").strip()

        if not _table_exists(schema_name, table_name):
            return JsonResponse({
                "ok": False,
                "error": "La tabla solicitada no existe o no está disponible.",
            })

        quoted_schema = connection.ops.quote_name(schema_name)
        quoted_table = connection.ops.quote_name(table_name)

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL TRANSACTION READ ONLY;")
                cursor.execute("SET LOCAL statement_timeout = '5s';")
                cursor.execute(f"SET LOCAL search_path TO {quoted_schema};")
                cursor.execute(f"SELECT * FROM {quoted_schema}.{quoted_table} LIMIT 1000;")

                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                key_metadata = _get_table_key_metadata(schema_name, table_name)

        return JsonResponse({
            "ok": True,
            "schema": schema_name,
            "table": table_name,
            "columns": columns,
            "rows": rows,
            "column_keys": key_metadata,
        })
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)})


@csrf_exempt
@require_POST
def run_sql(request):
    try:
        body = json.loads(request.body)
        query = body.get("query", "").strip()
        schema_name = body.get("schema", "").strip()

        if not query:
            return JsonResponse({
                "ok": False,
                "error": "No se recibió ninguna consulta SQL.",
            })

        if not is_user_schema(schema_name):
            return JsonResponse({
                "ok": False,
                "error": "Schema inválido o no permitido.",
            })

        try:
            validate_safe_select_query(query, schema_name)
        except ValidationError as e:
            return JsonResponse({
                "ok": False,
                "error": e.messages[0] if hasattr(e, "messages") else str(e),
            })

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL TRANSACTION READ ONLY;")
                cursor.execute("SET LOCAL statement_timeout = '5s';")

                quoted_schema = connection.ops.quote_name(schema_name)
                cursor.execute(f"SET LOCAL search_path TO {quoted_schema};")

                cursor.execute(query)

                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

        description_result = analizar_query(query)
        description_steps = description_result.get("steps", [])

        relational_tree = relational_tree_to_text(query)

        try:
            tree_preview_result = build_tree_preview_result(query, schema_name)
        except Exception as preview_error:
            tree_preview_result = {
                "tree_html": "",
                "tree_previews": {},
                "preview_error": str(preview_error),
            }

        return JsonResponse({
            "ok": True,
            "schema": schema_name,
            "columns": columns,
            "rows": rows,
            "description": description_steps,
            "tree": relational_tree,
            "tree_html": tree_preview_result.get("tree_html", ""),
            "tree_previews": tree_preview_result.get("tree_previews", {}),
            "tree_preview_error": tree_preview_result.get("preview_error"),
        })

    except Exception as e:
        return JsonResponse({
            "ok": False,
            "error": str(e),
        })