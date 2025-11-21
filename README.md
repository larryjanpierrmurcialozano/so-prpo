so-prpo

Proyecto de ejemplo: backend en Flask con frontend estático, manejo de uploads, migraciones con Alembic y tareas de limpieza programadas.

Descripción

Este repositorio contiene una aplicación web (Flask) con:
- API REST para productos, páginas y configuración.
- Backend en `backend/` con configuración, modelos y extensiones.
- Frontend simple en `frontend/` y plantillas en `static/templates/`.
- Migraciones en `migrations/` (Alembic).
- Scripts de configuración y despliegue: `setup_project.sh`, `setup_mysql.sh`, `Dockerfile`, etc.

Instalación rápida

1. Crear y activar un entorno virtual (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
- Copiar `.env.example` a `.env` y editar valores.

4. Inicializar la base de datos y migraciones (ejemplo):

```bash
# Ejemplos genéricos; ajustar según tu entorno
python backend/db_setup.py
alembic upgrade head
```

Ejecución

```bash
# Desde la raíz del proyecto
python run.py
```

Archivos importantes

- `backend/` — código del servidor Flask
- `frontend/` — recursos front-end y plantillas
- `migrations/` — versiones de la base de datos (Alembic)
- `requirements.txt` — dependencias Python

Etiquetas (texto plano)

Flask
MySQL
Docker
Alembic
Migraciones
API
Backend
Frontend
Uploads
Cron
Testing

Licencia

Este proyecto está bajo la licencia MIT — ver el archivo `LICENSE` para el texto completo.

Contribuciones

Si quieres contribuir, abre un issue o un pull request. Sigue las convenciones de estilo del proyecto y asegúrate de que las pruebas pasen antes de enviar cambios.

Contacto

Repositorio actualizado por el propietario del proyecto.

