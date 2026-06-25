import json

from django.db import connection, transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from editor.query_description import analizar_query
from editor.relational_tree import relational_tree_to_text
from editor.relational_preview import build_tree_preview_result

SYSTEM_SCHEMAS = {"information_schema", "pg_catalog", "public"}


def sql_editor(request):
    return render(request, "sql_editor.html")


def _is_user_schema(schema_name: str) -> bool:
    """Oculta schemas internos y schemas no usados para ejercicios."""
    return (
        bool(schema_name)
        and schema_name not in SYSTEM_SCHEMAS
        and not schema_name.startswith("pg_")
    )


def _table_exists(schema_name: str, table_name: str) -> bool:
    if not _is_user_schema(schema_name) or not table_name:
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


@require_GET
def list_schemas(request):
    """Devuelve los schemas visibles para el usuario de base de datos configurado en Django."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT schema_name
                FROM information_schema.schemata
                ORDER BY schema_name;
            """)
            schemas = [row[0] for row in cursor.fetchall() if _is_user_schema(row[0])]

        return JsonResponse({"ok": True, "schemas": schemas})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)})


@require_GET
def list_tables(request):
    """Devuelve las tablas base de un schema visible."""
    schema_name = request.GET.get("schema", "").strip()

    if not _is_user_schema(schema_name):
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
                cursor.execute(f"SELECT * FROM {quoted_schema}.{quoted_table} LIMIT 100;")

                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

        return JsonResponse({
            "ok": True,
            "schema": schema_name,
            "table": table_name,
            "columns": columns,
            "rows": rows,
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

        if not _is_user_schema(schema_name):
            return JsonResponse({
                "ok": False,
                "error": "Schema inválido o no permitido.",
            })

        # Restricción básica de aplicación, sólo se permite lectura.
        if not query.lower().startswith("select"):
            return JsonResponse({
                "ok": False,
                "error": "Por seguridad, solo se permiten consultas SELECT.",
            })

        # Evita ejecutar varias sentencias en una sola llamada.
        normalized_query = query.rstrip().rstrip(";").strip()
        if ";" in normalized_query:
            return JsonResponse({
                "ok": False,
                "error": "Por seguridad, solo se permite una consulta SELECT a la vez.",
            })

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL TRANSACTION READ ONLY;")

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