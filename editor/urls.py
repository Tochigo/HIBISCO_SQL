from django.urls import path

from .views.operators import (
    home,
    select_view,
    where_view,
    alias_view,
    union_view,
    except_view,
    busqueda_view,
    join_view,
    left_right_join_view,
    outer_join_view,
    nested_querys_view,
    agregaciones_view,
)

from .views.sql_editor_views import (
    sql_editor,
    run_sql,
    list_schemas,
    list_tables,
    preview_table,
)


urlpatterns = [
    path('', sql_editor, name='home'),

    path('operador/select/', select_view, name='SELECT'),
    path('operador/where/', where_view, name='WHERE'),
    path('operador/alias/', alias_view, name='ALIAS'),
    path('operador/union/', union_view, name='UNION'),
    path('operador/except/', except_view, name='EXCEPT'),
    path('operador/busqueda_view/', busqueda_view, name='BUSQUEDA&COMPARACION'),
    path('operador/join/', join_view, name='JOIN'),
    path('operador/left_right_join/', left_right_join_view, name='LEFT&RIGHTJOIN'),
    path('operador/outer_join/', outer_join_view, name='OUTER_JOIN'),
    path('operador/nested_querys/', nested_querys_view, name='NESTED_QUERYS'),
    path('operador/agregaciones/', agregaciones_view, name='AGREGATIONS'),

    path('sql/', sql_editor, name='sql_editor'),
    path('sql/run/', run_sql, name='run_sql'),
    path('sql/schemas/', list_schemas, name='list_schemas'),
    path('sql/tables/', list_tables, name='list_tables'),
    path('sql/preview-table/', preview_table, name='preview_table'),
]