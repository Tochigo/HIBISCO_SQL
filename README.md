# HIBISCO SQL

HIBISCO SQL es una aplicación web desarrollada con Django y PostgreSQL para practicar consultas SQL. La plataforma permite visualizar tablas disponibles, ejecutar consultas, revisar resultados y observar una descripción de los pasos de ejecución junto con un árbol relacional.

---

## Dependencias

- Python 3.10 o superior.
- PostgreSQL.
- `pip` y `venv`.
- Django 5.2.1
- psycopg2-binary 2.9.10
- sqlparse 0.5.5
- sqlglot


---

# Instalación

## 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd <HIBISCO_SQL>
```

---

## 2. Crear y activar entorno virtual

### En Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### En Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 4. Configurar variables de entorno

El archivo `settings.py` obtiene la configuración sensible desde variables de entorno. Crea un archivo `.env` o configura estas variables directamente en tu terminal:

```env
SECRET_KEY=django-insecure-cambia-este-valor
DEBUG=False
DB_NAME=hibisco_sql
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```

> Nota: Se recomienda el uso del archivo `.env`, los valores de SECRET_KEY y relacionados a la DB deben ser modificados según corresponda.

### Variables en Windows PowerShell

```powershell
$env:SECRET_KEY="django-insecure-cambia-este-valor"
$env:DEBUG="True"
$env:DB_NAME="hibisco_sql"
$env:DB_USER="postgres"
$env:DB_PASSWORD="tu_password"
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
```

### Variables en Linux / macOS

```bash
export SECRET_KEY="django-insecure-cambia-este-valor"
export DEBUG="True"
export DB_NAME="hibisco_sql"
export DB_USER="postgres"
export DB_PASSWORD="tu_password"
export DB_HOST="localhost"
export DB_PORT="5432"
```

---

## 5. Crear la base de datos en PostgreSQL

Ingresa a PostgreSQL:

```bash
psql -U postgres
```

Crea la base de datos:

```sql
CREATE DATABASE hibisco_sql;
```

Luego sal de `psql`:

```sql
\q
```

---

## 6. Ejecutar migraciones de Django

```bash
python manage.py migrate
```

Opcionalmente, puedes crear un superusuario para acceder al panel de administración de Django:

```bash
python manage.py createsuperuser
```

---

## 7. Cargar esquemas de ejemplo

El proyecto incluye scripts SQL para cargar datos de prueba.

### Esquema de cursos

```bash
psql -U postgres -d hibisco_sql -f esquema_cursos.sql
```

Este script crea el esquema `cursos` y sus tablas asociadas.

### Esquema de videojuegos

```bash
psql -U postgres -d hibisco_sql -f esquema_videojuegos.sql
```

Este script crea el esquema `videojuegos` y sus tablas asociadas.

Si usas otro usuario de PostgreSQL, reemplaza `postgres` por el usuario configurado en `DB_USER`.

---

## 8. Ejecutar el servidor

```bash
python manage.py runserver
```

Luego abre la aplicación en el navegador:

```text
http://127.0.0.1:8000/
```

---

## 9. Estructura esperada del proyecto

Una estructura recomendada para los templates y archivos estáticos es:

```text
templates/
  base.html
  sql_editor.html
  select.html
  where.html
  alias.html
  union.html
  except.html
  seach&comparison.html
  join.html
  left_right_join.html
  outer_join.html
  nested_querys.html
  agregations.html

static/
  css/
    base.css
    sql_editor.css
    operator.css
  js/
    theme.js
    sql_editor.js
    operator.js
```


## 10. Problemas comunes

### Error: `SECRET_KEY` vacío

Verifica que la variable `SECRET_KEY` esté definida antes de iniciar el servidor.

### Error de conexión a PostgreSQL

Revisa que PostgreSQL esté activo y que las variables `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT` coincidan con tu instalación.


### No cargan los CSS o JS

Verifica que `STATICFILES_DIRS` apunte a la carpeta correcta:

```python
STATICFILES_DIRS = [BASE_DIR / "static"]
```

También recuerda cargar estáticos en los templates con:

```django
{% load static %}
```

---

## Créditos

Hibisco SQL © 2026 — Diego Reyes G
