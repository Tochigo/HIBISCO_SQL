from django.shortcuts import render

def sql_editor(request):
    # De momento solo se muestra el frontend
    return render(request, 'editor/sql_editor.html')
