from django.urls import path
from .views import sql_editor

urlpatterns = [
    path('', sql_editor, name='sql_editor'),
]
