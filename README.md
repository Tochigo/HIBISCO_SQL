# HIBISCO SQL

HIBISCO SQL es una aplicación web desarrollada con Django y PostgreSQL para practicar consultas SQL. La plataforma permite visualizar tablas disponibles, ejecutar consultas, revisar resultados y observar una descripción de los pasos de ejecución junto con un árbol relacional.

---

## Requisitos

Para ejecutar la aplicación mediante Docker se requiere:

* Git
* Docker
* Docker Compose
* Acceso SSH al servidor
* Un usuario con permisos para ejecutar Docker

---

## Instalación en servidor Linux con Docker

### 1. Conectarse al servidor

Desde tu equipo local, conéctate al servidor mediante SSH:

```bash
ssh -p <PUERTO_SSH> <USUARIO>@<NOMBRE_DEL_SERVIDOR>
```

Reemplaza:

* `<PUERTO_SSH>` por el puerto SSH del servidor.
* `<USUARIO>` por tu usuario en el servidor.
* `<NOMBRE_DEL_SERVIDOR>` por el nombre o dirección del servidor.

---

### 2. Clonar el repositorio

En el servidor, clona el repositorio del proyecto:

```bash
git clone https://github.com/Tochigo/HIBISCO_SQL.git
cd HIBISCO_SQL
```

---

### 3. Crear el archivo `.env`

En la raíz del proyecto, crea un archivo `.env`:

```bash
nano .env
```

Agrega el siguiente contenido, ajustando los valores según corresponda:

```env
SECRET_KEY=<CLAVE_SECRETA_DJANGO>
DEBUG=False
ALLOWED_HOSTS=<DOMINIO_O_IP>,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://<DOMINIO>

DB_NAME=hibisco_sql
DB_USER=postgres
DB_PASSWORD=<CONTRASEÑA_POSTGRES>
DB_HOST=db
DB_PORT=5432
```

Notas importantes:

* `SECRET_KEY` debe ser una clave segura y no debe compartirse públicamente.
* `DEBUG=False` permite ejecutar Django en modo de producción.
* `ALLOWED_HOSTS` debe incluir el dominio o IP desde donde se accederá a la aplicación.
* `CSRF_TRUSTED_ORIGINS` debe incluir el dominio completo con `https://` si se accede mediante HTTPS.
* `DB_HOST=db` corresponde al nombre del servicio de PostgreSQL definido en `docker-compose.yml`.
* El archivo `.env` no debe subirse al repositorio.

---

### 4. Revisar configuración de Docker

El archivo `docker-compose.yml` debe definir dos servicios principales:

* `db`: base de datos PostgreSQL.
* `web`: aplicación Django.

El servicio `web` debe exponer el puerto interno `8000` de Django hacia el puerto del servidor que será usado por el proxy reverso o por el acceso externo.

Ejemplo:

```yaml
services:
  db:
    image: postgres:16
    restart: always
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    restart: always
    command: >
      sh -c "python manage.py collectstatic --noinput &&
             gunicorn sql_compiler.wsgi:application --bind 0.0.0.0:8000"
    volumes:
      - .:/app
    ports:
      - "<PUERTO_SERVIDOR>:8000"
    env_file:
      - .env
    depends_on:
      - db

volumes:
  postgres_data:
```

Reemplaza `<PUERTO_SERVIDOR>` por el puerto del servidor al que debe llegar el tráfico externo o el proxy reverso.

---

### 5. Construir y levantar los contenedores

Desde la raíz del proyecto, ejecuta:

```bash
docker compose up --build -d
```

Esto construye la imagen de Django y levanta los servicios `web` y `db`.

Para verificar que los contenedores estén activos:

```bash
docker compose ps
```

---

### 6. Ejecutar migraciones de Django

Una vez levantados los contenedores, ejecuta las migraciones:

```bash
docker compose exec web python manage.py migrate
```

Opcionalmente, puedes crear un superusuario para acceder al panel de administración de Django:

```bash
docker compose exec web python manage.py createsuperuser
```

---

### 7. Cargar esquemas de ejemplo

Los archivos SQL de carga se encuentran en:

```text
database_load_files/
```

Para cargar el esquema de cursos:

```bash
docker compose exec -T db psql -U postgres -d hibisco_sql < database_load_files/esquema_cursos.sql
```

Para cargar el esquema de videojuegos:

```bash
docker compose exec -T db psql -U postgres -d hibisco_sql < database_load_files/esquema_videojuegos.sql
```

Si en el archivo `.env` se configuró otro usuario o nombre de base de datos, reemplaza `postgres` y `hibisco_sql` por los valores correspondientes.

---

### 8. Acceder a la aplicación

Una vez levantada la aplicación, se puede acceder desde:

```text
https://<DOMINIO>
```

o, si corresponde, directamente mediante:

```text
http://<NOMBRE_DEL_SERVIDOR>:<PUERTO_SERVIDOR>
```

---

## Configuración para `DEBUG=False`

Para ejecutar la aplicación con `DEBUG=False`, el proyecto utiliza:

* `gunicorn` como servidor WSGI.
* `whitenoise` para servir archivos estáticos.
* `collectstatic` para recopilar los archivos CSS y JS antes de iniciar la aplicación.

El archivo `requirements.txt` debe incluir:

```text
Django==5.2.1
psycopg2-binary==2.9.10
sqlparse==0.5.5
sqlglot
whitenoise
gunicorn
```

En `settings.py`, WhiteNoise debe estar configurado en `MIDDLEWARE` justo después de `SecurityMiddleware`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

Además, la configuración de archivos estáticos debe incluir:

```python
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
```

Con esta configuración, el comando `collectstatic` copia los archivos desde `static/` hacia `staticfiles/`, y WhiteNoise permite que Django los sirva correctamente con `DEBUG=False`.

---

## Comandos útiles

### Ver estado de los contenedores

```bash
docker compose ps
```

### Ver logs de la aplicación

```bash
docker compose logs -f web
```

### Ver logs de la base de datos

```bash
docker compose logs -f db
```

### Reiniciar los servicios

```bash
docker compose restart
```

### Detener los servicios

```bash
docker compose down
```

### Detener los servicios y eliminar la base de datos

```bash
docker compose down -v
```

Advertencia: este comando elimina el volumen `postgres_data`, por lo que también elimina los datos cargados en PostgreSQL.

---

## Actualizar la aplicación en el servidor

Para actualizar el proyecto con cambios nuevos desde GitHub:

```bash
git pull origin main
docker compose up --build -d
docker compose exec web python manage.py migrate
```

Como el servicio `web` ejecuta `collectstatic` antes de iniciar Gunicorn, los archivos estáticos se recopilan automáticamente al reconstruir o reiniciar el contenedor.

Si los scripts SQL cambiaron y se desea recargar la base de datos desde cero:

```bash
docker compose down -v
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec -T db psql -U postgres -d hibisco_sql < database_load_files/esquema_cursos.sql
docker compose exec -T db psql -U postgres -d hibisco_sql < database_load_files/esquema_videojuegos.sql
```

---

## Problemas comunes

### La aplicación no carga desde el dominio configurado

Verifica que el servicio `web` esté exponiendo el puerto correcto:

```yaml
ports:
  - "<PUERTO_SERVIDOR>:8000"
```

También revisa que los contenedores estén activos:

```bash
docker compose ps
```

Y revisa los logs:

```bash
docker compose logs -f web
```

---

### Error de conexión a PostgreSQL

Verifica que el archivo `.env` use:

```env
DB_HOST=db
```

Dentro de Docker Compose, `localhost` no apunta al contenedor de PostgreSQL, sino al propio contenedor de Django.

---

### Error relacionado con `ALLOWED_HOSTS`

Si aparece un error de host no permitido, revisa que el dominio o IP esté incluido en:

```env
ALLOWED_HOSTS=<DOMINIO_O_IP>,localhost,127.0.0.1
```

---

### Error relacionado con CSRF

Si se accede mediante HTTPS y ocurre un error CSRF, revisa que el dominio esté incluido en:

```env
CSRF_TRUSTED_ORIGINS=https://<DOMINIO>
```

---

### Los CSS o JS no cargan

Verifica que `whitenoise` esté instalado y configurado, que exista `STATIC_ROOT`, y que se haya ejecutado:

```bash
docker compose exec web python manage.py collectstatic --noinput
```

Si el `docker-compose.yml` usa el comando recomendado, `collectstatic` se ejecuta automáticamente antes de iniciar Gunicorn.

---

### El puerto configurado ya está ocupado

Revisa si otro servicio está usando el puerto:

```bash
sudo lsof -i :<PUERTO_SERVIDOR>
```

Si el puerto está ocupado, se debe detener el servicio que lo usa o ajustar la configuración del proxy reverso para apuntar a otro puerto.

---

## Estructura relevante del proyecto

```text
database_load_files/
  esquema_cursos.sql
  esquema_videojuegos.sql

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

---

## Créditos

Hibisco SQL © 2026 — Diego Reyes G.
