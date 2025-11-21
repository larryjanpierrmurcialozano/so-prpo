subdominios añadir.
implementacion de tablas personalizables.
un search que muestre por igual las paginas pero dentro de un nuevo html y no uno vinculado al search principal sin usuario.



# 📚 CONCEPTOS AVANZADOS DEL PROYECTO - GUÍA COMPLETA

1. Arquitectura con Blueprints
   Definición ampliada: módulo autorretringido que agrupa rutas, handlers, templates y recursos relacionados; actúa como una "mini-aplicación" plugable dentro de la app Flask.
   Cuándo usar: cuando la app crece (múltiples áreas funcionales), equipos trabajan paralelamente o se requiere reuso.
   Beneficios prácticos: encapsulación de rutas/plantillas, tests por módulo, carga perezosa, prefijos de URL y facil integración en la factory.
   Riesgos/precauciones: evitar dependencias circulares entre blueprints; mantener interfaces claras (funciones públicas mínimas).
   Ejemplo de uso: separar auth, products, api; registrar con url_prefix para rutas coherentes.
2. Factory Pattern (Application Factory)
   Definición ampliada: función que crea y configura la instancia de la aplicación en runtime, recibiendo la configuración como parámetro.
   Cuándo usar: ambientes múltiples (dev/test/prod), pruebas unitarias, despliegue con WSGI (gunicorn), inicialización tardía de extensiones.
   Beneficios prácticos: instancias aisladas para tests, evitar variables globales, configurar logs/paths dinámicamente.
   Riesgos/precauciones: no inicializar extensiones globalmente con la app; usar init_app y evitar lógica con efectos secundarios fuera de la factory.
   Práctica recomendada: inyectar config_class, crear carpetas (uploads) dentro de la factory y registrar blueprints/commands allí.
3. Migraciones de Base de Datos
   Definición ampliada: sistema que traduce cambios en modelos ORM a scripts versionados (upgrade/downgrade) y los aplica a la BD.
   Cuándo usar: cambios estructurales en modelos en cualquier entorno real (dev/prod/stage).
   Beneficios prácticos: historial de cambios, reversibilidad, colaboración entre devs, despliegues controlados.
   Riesgos/precauciones: revisar migraciones generadas automáticamente (no confiar ciegamente), planear cambios destructivos (p.ej. DROP COLUMN) y hacer backups antes de migraciones en prod.
   Buenas prácticas: pruebas de migración en staging, usar transacciones y migraciones pequeñas y atómicas.
4. Docker y Containerización
   Definición ampliada: empaquetado de la app con runtime y dependencias en una imagen inmutable que corre en cualquier host con Docker.
   Cuándo usar: replicabilidad entre entornos, despliegues automáticos, integración CI/CD, aislar dependencias del host.
   Beneficios prácticos: reproducción idéntica del entorno, facil despliegue horizontal, versiones consistentes.
   Riesgos/precauciones: no incluir secretos en la imagen (usar variables de entorno/secret manager), mantener imágenes ligeras, mapear volúmenes cuando sea necesario (uploads, DB persistente).
   Buenas prácticas: multi-stage builds, usar docker-compose para servicios múltiples (web + db), healthchecks y readiness probes en producción.
5. CRON Jobs y Automatización
   Definición ampliada: tareas programadas que ejecutan scripts periódicos en el servidor (limpieza, backups, sincronizaciones).
   Cuándo usar: tareas repetitivas no interactivas: limpieza, exportes, notificaciones, mantenimiento.
   Beneficios prácticos: elimina trabajo manual, mantiene consistencia temporal y permite escalado (ejecutar en contenedores/cron manager).
   Riesgos/precauciones: manejo de concurrencia (evitar ejecuciones solapadas), logging/alertas si fallan, asegurar entorno virtual y variables de entorno.
   Buenas prácticas: usar locks (file/DB/redis) para evitar doble ejecución, centralizar logs y supervisión.
6. Sistemas de Limpieza Enterprise
   Definición ampliada: conjunto de políticas y tareas automáticas que mantienen integridad y rendimiento de datos (retención, eliminación de huérfanos, archivado).
   Cuándo usar: apps con crecimiento de datos, requisitos legales (GDPR), o necesidad de optimizar costes/performace.
   Beneficios prácticos: cumplimiento legal, menor tamaño de BD, menores tiempos de backup, mejor rendimiento.
   Riesgos/precauciones: definir políticas claras (retención, soft-delete vs hard-delete), pruebas exhaustivas para evitar pérdida de datos, mantener auditoría.
   Implementación: pipelines de limpieza con métricas, reversibles o con backup previo, y notificaciones a stakeholders.
7. Control de Versiones Optimista
   Definición ampliada: técnica para detectar conflictos concurrentes agregando un campo de versión/timestamp y comparándolo antes de persistir cambios.
   Cuándo usar: edición concurrente de recursos (productos, documentos) donde bloquear sería ineficiente.
   Beneficios prácticos: evita pérdida silenciosa de cambios, no bloquea lecturas, permite UX de resolución de conflictos.
   Riesgos/precauciones: UX para el usuario (mostrar conflictos), manejar reintentos y merge manual si necesario, evitar aplicar incrementos sin verificación atómica.
   Buenas prácticas: incluir versión en formularios/API, verificar en update/where clausula para que la actualización sea condicional (optimistic update).
8. Cascade Deletes Avanzados
   Definición ampliada: configuración ORM/BD para propagar eliminaciones a filas relacionadas automáticamente (ORM: cascade, BD: ON DELETE CASCADE).
   Cuándo usar: relaciones dependientes donde la existencia del hijo no tiene sentido sin el padre (p.ej. productos de un usuario).
   Beneficios prácticos: evita huérfanos, simplifica operaciones de borrado, coherencia referencial.
   Riesgos/precauciones: borrados masivos accidentales, pérdida de datos históricos; revisar cascadas en ambas capas (ORM y DB) para no duplicar o contradicciones.
   Recomendación: auditar antes de aplicar cascade en entidades críticas; ofrecer confirmaciones y logs para borrados que disparen cascadas grandes.









## 📖 Índice
1. [Arquitectura con Blueprints](#1-arquitectura-con-blueprints)
2. [Factory Patterns](#2-factory-patterns)
3. [Migraciones de Base de Datos](#3-migraciones-de-base-de-datos)
4. [Docker y Containerización](#4-docker-y-containerización)
5. [CRON Jobs y Automatización](#5-cron-jobs-y-automatización)
6. [Sistemas de Limpieza Enterprise](#6-sistemas-de-limpieza-enterprise)
7. [Control de Versiones Optimista](#7-control-de-versiones-optimista)
8. [Cascade Deletes Avanzados](#8-cascade-deletes-avanzados)

---

## 1. 📦 Arquitectura con Blueprints

### ¿Qué son los Blueprints?

Los **Blueprints** son una forma de organizar aplicaciones Flask en módulos independientes y reutilizables. Piensa en ellos como "mini-aplicaciones" que se conectan a la aplicación principal.

### ❌ Forma Simple (Lo que hace un estudiante típico)

```python
# app.py - TODO EN UN ARCHIVO
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # código de login
    pass

@app.route('/products')
def products():
    # código de productos
    pass

@app.route('/register')
def register():
    # código de registro
    pass

# ... 500+ líneas más ...
```

**Problemas:**
- ❌ Archivo gigante e imposible de mantener
- ❌ Difícil encontrar errores
- ❌ No se puede trabajar en equipo
- ❌ No es reutilizable

### ✅ Forma Avanzada (Tu proyecto)

**Estructura de archivos:**
```
backend/
├── app.py                 # Factory de la aplicación
├── extensions.py          # Extensiones compartidas
└── api/
    ├── __init__.py
    ├── auth.py            # Blueprint de autenticación
    ├── products.py        # Blueprint de productos
    ├── pages.py           # Blueprint de páginas
    ├── upload.py          # Blueprint de uploads
    ├── settings.py        # Blueprint de configuración
    └── search_advanced.py # Blueprint de búsqueda
```

**Código en backend/api/auth.py:**
```python
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required

# Crear el Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Solo maneja autenticación
    pass

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Solo maneja registro
    pass

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
```

**Código en backend/api/products.py:**
```python
from flask import Blueprint

# Blueprint con prefijo de URL
products_bp = Blueprint('products', __name__)

@products_bp.route('/')
def list_products():
    # Lista productos
    pass

@products_bp.route('/<int:product_id>')
def view_product(product_id):
    # Ver detalle
    pass

@products_bp.route('/create', methods=['GET', 'POST'])
def create_product():
    # Crear producto
    pass
```

**Registrar Blueprints en backend/app.py:**
```python
from flask import Flask
from .api.auth import auth_bp
from .api.products import products_bp
from .api.pages import pages_bp
from .api.upload import upload_bp
from .api.settings import settings_bp
from .api.search_advanced import search_bp

def create_app():
    app = Flask(__name__)
    
    # Registrar cada módulo
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(pages_bp)
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(settings_bp)
    app.register_blueprint(search_bp)
    
    return app
```

### 🎯 Ventajas de los Blueprints

✅ **Organización:** Cada módulo tiene su responsabilidad
✅ **Escalabilidad:** Fácil agregar nuevas funcionalidades
✅ **Mantenimiento:** Encontrar bugs es más fácil
✅ **Reutilización:** Puedes usar el mismo blueprint en diferentes proyectos
✅ **Trabajo en equipo:** Diferentes personas pueden trabajar en diferentes blueprints

### 🔍 Ejemplo Real en tu Proyecto

**URL sin Blueprints:**
```
/login           -> función login()
/register        -> función register()
/product_create  -> función product_create()
/product_edit    -> función product_edit()
```

**URL con Blueprints (tu proyecto):**
```
auth.login         -> /login
auth.register      -> /register
products.create    -> /products/create
products.edit      -> /products/edit/<id>
upload.upload_file -> /api/upload
```

---

## 2. 🏭 Factory Patterns

### ¿Qué es el Factory Pattern?

Es un patrón de diseño que permite **crear objetos de forma flexible y configurable**. En Flask, se usa para crear la aplicación de manera que pueda adaptarse a diferentes entornos (desarrollo, producción, testing).

### ❌ Forma Simple

```python
# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:pass@localhost/db'
db = SQLAlchemy(app)

# ❌ Problemas:
# - No puedes tener múltiples configuraciones
# - No puedes hacer testing fácilmente
# - La configuración está hardcodeada
# - No puedes crear múltiples instancias de la app
```

### ✅ Forma Avanzada (Factory Pattern - Tu proyecto)

**backend/extensions.py:**
```python
# Crear extensiones SIN inicializar
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Instancias globales pero NO conectadas a la app
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
```

**backend/config.py:**
```python
import os

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://user:pass@localhost/dev_db'

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestingConfig(Config):
    """Configuración para tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
```

**backend/app.py (Application Factory):**
```python
from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager

def create_app(config_class=Config):
    """
    Application Factory
    Crea y configura la aplicación Flask
    """
    # 1. Crear instancia de Flask
    app = Flask(__name__, 
                static_folder="../frontend/static", 
                template_folder="../frontend/templates")
    
    # 2. Cargar configuración
    app.config.from_object(config_class)
    
    # 3. Crear carpeta de uploads
    static_uploads = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static', 'uploads')
    uploads_path = os.path.abspath(static_uploads)
    os.makedirs(uploads_path, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = uploads_path
    
    # 4. Inicializar extensiones CON la app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    
    # 5. Configurar user loader
    from .models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None
    
    # 6. Registrar Blueprints
    from .api.auth import auth_bp
    from .api.products import products_bp
    from .api.pages import pages_bp
    from .api.upload import upload_bp
    from .api.settings import settings_bp
    from .api.search_advanced import search_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(pages_bp)
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(settings_bp)
    app.register_blueprint(search_bp)
    
    return app
```

### 🎯 Uso del Factory Pattern

**Para desarrollo:**
```python
from backend.app import create_app
from backend.config import DevelopmentConfig

app = create_app(DevelopmentConfig)
app.run(debug=True)
```

**Para testing:**
```python
from backend.app import create_app
from backend.config import TestingConfig

def test_something():
    app = create_app(TestingConfig)
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
```

**Para producción:**
```python
from backend.app import create_app
from backend.config import ProductionConfig

app = create_app(ProductionConfig)
# Ejecutar con gunicorn
```

### 🎁 Ventajas del Factory Pattern

✅ **Flexibilidad:** Crear diferentes instancias para diferentes propósitos
✅ **Testing:** Fácil crear apps de prueba con configuración diferente
✅ **Seguridad:** Variables sensibles en variables de entorno
✅ **Mantenibilidad:** Código más limpio y organizado
✅ **Profesional:** Patrón usado en aplicaciones enterprise

---

## 3. 🗄️ Migraciones de Base de Datos

### ¿Qué son las Migraciones?

Las migraciones son **"control de versiones para tu base de datos"**. Permiten hacer cambios en la estructura de la base de datos de forma controlada y reversible.

### ❌ Forma Simple (Sin migraciones)

```python
# models.py
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))

# Para crear las tablas:
db.create_all()

# ❌ PROBLEMAS:
# - Si cambias el modelo, pierdes todos los datos
# - No hay historial de cambios
# - No puedes volver atrás si algo sale mal
# - En producción, esto es DESASTROSO
```

**Escenario problemático:**
```python
# Día 1: Tienes 1000 usuarios en la base de datos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))

# Día 2: Necesitas agregar email
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(200))  # ¡NUEVO!

db.drop_all()  # ❌ ¡Borra los 1000 usuarios!
db.create_all()
```

### ✅ Forma Avanzada (Con Flask-Migrate - Tu proyecto)

**Estructura de migraciones:**
```
migrations/
├── alembic.ini          # Configuración de Alembic
├── env.py               # Entorno de migración
├── script.py.mako       # Template para nuevas migraciones
└── versions/            # Historial de cambios
    ├── 452dee38738f_initial_mysql_migration.py
    ├── 60e58207aeee_add_color_customization_fields.py
    ├── add_categories_system.py
    ├── add_last_login_and_cleanup_system.py
    ├── add_missing_fields.py
    ├── add_page_id_to_products.py
    └── multiple_pages_support.py
```

### 🔄 Proceso de Migración

**1. Inicializar sistema de migraciones (solo una vez):**
```bash
flask db init
```

**2. Crear primera migración:**
```bash
flask db migrate -m "initial_mysql_migration"
```

Esto genera un archivo como `452dee38738f_initial_mysql_migration.py`:
```python
"""initial_mysql_migration

Revision ID: 452dee38738f
Revises: 
Create Date: 2024-01-15 10:30:45.123456

"""
from alembic import op
import sqlalchemy as sa

revision = '452dee38738f'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Aplicar cambios"""
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=200), nullable=False),
        sa.Column('password_hash', sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

def downgrade():
    """Revertir cambios"""
    op.drop_table('users')
```

**3. Aplicar migración:**
```bash
flask db upgrade
```

**4. Agregar nuevo campo (ejemplo real de tu proyecto):**

Cambias el modelo:
```python
# models.py
class User(UserMixin, db.Model):
    # ...existing code...
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)  # NUEVO CAMPO
```

Creas migración:
```bash
flask db migrate -m "add_last_login_and_cleanup_system"
```

Se genera automáticamente:
```python
def upgrade():
    """Aplicar cambios"""
    op.add_column('users', 
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True)
    )

def downgrade():
    """Revertir cambios"""
    op.drop_column('users', 'last_login')
```

Aplicar:
```bash
flask db upgrade
```

**5. Si algo sale mal, puedes volver atrás:**
```bash
flask db downgrade  # Volver a la versión anterior
```

### 📊 Ejemplo Real: Evolución de tu Base de Datos

**Migración 1: Base inicial**
```
users (id, username, email, password_hash, created_at)
```

**Migración 2: Agregar páginas personalizadas**
```
pages (id, uuid, title, slug, owner_id)
```

**Migración 3: Agregar personalización de colores**
```
ALTER TABLE pages ADD COLUMN color_bg VARCHAR(7) DEFAULT '#ffffff';
ALTER TABLE pages ADD COLUMN color_header VARCHAR(7) DEFAULT '#667eea';
ALTER TABLE pages ADD COLUMN color_footer VARCHAR(7) DEFAULT '#343a40';
```

**Migración 4: Sistema de categorías**
```
categories (id, name, description, is_default, owner_id)
product_categories (id, product_id, category_id)
```

**Migración 5: Sistema de limpieza**
```
ALTER TABLE users ADD COLUMN last_login DATETIME;
```

### 🎯 Ventajas de las Migraciones

✅ **Historial:** Puedes ver todos los cambios en la BD
✅ **Reversible:** Si algo falla, vuelves atrás
✅ **Sin pérdida de datos:** Los datos se preservan
✅ **Colaboración:** El equipo comparte los cambios de BD
✅ **Producción segura:** Actualizar BD sin riesgo
✅ **Documentación:** Cada migración documenta qué cambió y cuándo

---

## 4. 🐳 Docker y Containerización

### ¿Qué es Docker?

Docker permite **empaquetar tu aplicación con todas sus dependencias** en un "contenedor" que funciona igual en cualquier computadora.

### ❌ Problema Sin Docker

**Estudiante A:**
```
- Windows 11
- Python 3.9
- MySQL 5.7
✅ La app funciona perfecto
```

**Profesor:**
```
- Ubuntu 22.04
- Python 3.12
- MySQL 8.0
❌ "No me funciona tu proyecto"
```

**Excusas clásicas:**
- "En mi computadora funciona..."
- "Necesitas instalar X librería"
- "Tienes que configurar Y..."

### ✅ Solución con Docker (Tu proyecto)

**Dockerfile:**
```dockerfile
# Imagen base de Python
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivo de dependencias
COPY requirements.txt ./

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código
COPY . /app

# Variables de entorno
ENV FLASK_APP=backend.app:create_app
ENV FLASK_ENV=development

# Puerto que usa la app
EXPOSE 5000

# Comando para ejecutar
CMD ["flask", "run", "--host=0.0.0.0"]
```

### 📦 ¿Qué hace cada línea?

```dockerfile
FROM python:3.11-slim
# Usa una imagen base con Python 3.11 ya instalado
# "slim" = versión ligera sin cosas innecesarias
```

```dockerfile
WORKDIR /app
# Todas las operaciones se harán en /app dentro del contenedor
```

```dockerfile
COPY requirements.txt ./
# Copia solo requirements.txt primero
# Aprovecha el cache de Docker para no reinstalar todo cada vez
```

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
# Instala todas las dependencias
# --no-cache-dir = no guardar archivos temporales (reduce tamaño)
```

```dockerfile
COPY . /app
# Copia TODO el código del proyecto
```

```dockerfile
ENV FLASK_APP=backend.app:create_app
# Variable de entorno que indica dónde está la app
```

```dockerfile
EXPOSE 5000
# Documenta que la app usa el puerto 5000
```

```dockerfile
CMD ["flask", "run", "--host=0.0.0.0"]
# Comando que se ejecuta al iniciar el contenedor
# --host=0.0.0.0 permite acceso desde fuera del contenedor
```

### 🚀 Uso de Docker

**Construir la imagen:**
```bash
docker build -t mi-tienda-app .
```

**Ejecutar el contenedor:**
```bash
docker run -p 5000:5000 mi-tienda-app
```

**Con docker-compose (más avanzado):**

Crear `docker-compose.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=mysql://user:pass@db:3306/tienda
    depends_on:
      - db
    volumes:
      - ./frontend/static/uploads:/app/frontend/static/uploads

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: tienda
      MYSQL_USER: user
      MYSQL_PASSWORD: pass
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

**Ejecutar todo:**
```bash
docker-compose up
```

### 🎯 Ventajas de Docker

✅ **Portabilidad:** Funciona igual en cualquier máquina
✅ **Aislamiento:** No interfiere con otras aplicaciones
✅ **Reproducibilidad:** Mismos resultados siempre
✅ **Fácil distribución:** Compartir es solo compartir el Dockerfile
✅ **Producción:** Mismo contenedor en dev y producción
✅ **Escalabilidad:** Fácil crear múltiples instancias

---

## 5. ⏰ CRON Jobs y Automatización

### ¿Qué es un CRON Job?

Un **CRON job** es una tarea que se ejecuta automáticamente en un horario específico. Es como poner una alarma para que tu computadora haga algo.

### ❌ Forma Manual

```bash
# Cada día, el administrador tiene que:
1. Conectarse al servidor
2. Ejecutar: python cleanup.py
3. Revisar logs
4. Repetir mañana...

# ❌ Problemas:
# - Se puede olvidar
# - No funciona los fines de semana
# - Requiere intervención manual
```

### ✅ Forma Automatizada (Tu proyecto)

**backend/cleanup_tasks.py:**
```python
from datetime import datetime, timezone, timedelta
from backend.models import User, db
import logging

logger = logging.getLogger(__name__)

def cleanup_inactive_accounts():
    """
    Elimina cuentas que no han iniciado sesión en 30 días
    """
    try:
        one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Usuarios que nunca iniciaron sesión
        never_logged_users = User.query.filter(
            User.last_login.is_(None),
            User.created_at < one_month_ago
        ).all()
        
        # Usuarios inactivos
        inactive_users = User.query.filter(
            User.last_login.isnot(None),
            User.last_login < one_month_ago
        ).all()
        
        all_inactive_users = never_logged_users + inactive_users
        
        deleted_count = 0
        for user in all_inactive_users:
            logger.info(f"Eliminando cuenta inactiva: {user.username} (ID: {user.id})")
            db.session.delete(user)
            deleted_count += 1
        
        if deleted_count > 0:
            db.session.commit()
            logger.info(f"✅ Limpieza completada: {deleted_count} cuentas eliminadas")
        else:
            logger.info("✅ No hay cuentas inactivas para eliminar")
            
        return deleted_count
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error en limpieza: {str(e)}")
        return 0

def cleanup_unused_categories():
    """
    Elimina categorías personalizadas sin productos y con más de 7 días
    """
    try:
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        # Categorías sin productos
        unused_categories = Category.query.filter(
            Category.is_default == False,
            Category.created_at < one_week_ago,
            ~Category.products.any()  # No tiene productos
        ).all()
        
        deleted_count = len(unused_categories)
        for category in unused_categories:
            db.session.delete(category)
        
        if deleted_count > 0:
            db.session.commit()
            logger.info(f"✅ {deleted_count} categorías sin uso eliminadas")
        
        return deleted_count
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error: {str(e)}")
        return 0
```

**auto_cleanup.sh (Script de automatización):**
```bash
#!/bin/bash

# Colores para salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🧹 SISTEMA DE LIMPIEZA AUTOMÁTICA${NC}"
echo "=================================================="
echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Ir al directorio del proyecto
PROJECT_DIR="/home/larry/IdeaProjects/so prpo"
cd "$PROJECT_DIR" || {
    echo -e "${RED}❌ Error: No se pudo acceder al directorio${NC}"
    exit 1
}

# Activar entorno virtual
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo -e "${GREEN}✅ Entorno virtual activado${NC}"
else
    echo -e "${RED}❌ Error: No se encontró el entorno virtual${NC}"
    exit 1
fi

# Configurar Flask
export FLASK_APP=backend/app.py

# Ejecutar limpieza
echo -e "\n${YELLOW}🧹 EJECUTANDO LIMPIEZA...${NC}"
python -c "
import sys
sys.path.append('.')

from backend.app import create_app
from backend.cleanup_tasks import cleanup_inactive_accounts, cleanup_unused_categories

app = create_app()
with app.app_context():
    print('Limpiando cuentas inactivas...')
    deleted_users = cleanup_inactive_accounts()
    
    print('Limpiando categorías sin uso...')
    deleted_categories = cleanup_unused_categories()
    
    print(f'Total: {deleted_users} usuarios, {deleted_categories} categorías eliminadas')
"

echo -e "\n${GREEN}✅ LIMPIEZA COMPLETADA${NC}"
echo "=================================================="
```

**setup_cron.sh (Configurar CRON automáticamente):**
```bash
#!/bin/bash

# Hacer el script ejecutable
chmod +x /home/larry/IdeaProjects/so\ prpo/auto_cleanup.sh

# Crear entrada CRON
CRON_JOB="0 3 * * * /home/larry/IdeaProjects/so\ prpo/auto_cleanup.sh >> /home/larry/cleanup.log 2>&1"

# Verificar si ya existe
(crontab -l 2>/dev/null | grep -v "auto_cleanup.sh"; echo "$CRON_JOB") | crontab -

echo "✅ CRON job configurado: Limpieza diaria a las 3:00 AM"
```

### 📅 Sintaxis de CRON

```
┌───────────── minuto (0-59)
│ ┌─────────── hora (0-23)
│ │ ┌───────── día del mes (1-31)
│ │ │ ┌─────── mes (1-12)
│ │ │ │ ┌───── día de la semana (0-7, 0 y 7 = domingo)
│ │ │ │ │
* * * * * comando
```

**Ejemplos:**
```bash
0 3 * * *       # Cada día a las 3:00 AM
*/15 * * * *    # Cada 15 minutos
0 */2 * * *     # Cada 2 horas
0 0 * * 0       # Cada domingo a medianoche
0 9 1 * *       # El día 1 de cada mes a las 9:00 AM
```

### 🔄 Flujo Completo de Automatización

```
1. CRON se activa a las 3:00 AM
        ↓
2. Ejecuta auto_cleanup.sh
        ↓
3. Script activa entorno virtual
        ↓
4. Ejecuta cleanup_inactive_accounts()
   - Busca usuarios con last_login > 30 días
   - Los elimina (CASCADE elimina sus productos/páginas)
        ↓
5. Ejecuta cleanup_unused_categories()
   - Busca categorías sin productos
   - Las elimina
        ↓
6. Guarda log en /home/larry/cleanup.log
        ↓
7. Envía notificación (opcional)
```

### 🎯 Ventajas de CRON + Automatización

✅ **Automatización total:** No requiere intervención manual
✅ **Consistencia:** Siempre se ejecuta en el mismo horario
✅ **Logs:** Historial de todas las ejecuciones
✅ **Eficiencia:** Libera recursos eliminando datos innecesarios
✅ **Mantenimiento:** La base de datos se mantiene limpia automáticamente
✅ **Profesional:** Así trabajan las empresas reales

---

## 6. 🧹 Sistemas de Limpieza Enterprise

### ¿Qué es un Sistema de Limpieza Enterprise?

Es un conjunto de procesos automáticos que **mantienen la base de datos limpia, eficiente y optimizada** sin intervención manual. Las empresas lo usan para:
- Eliminar datos obsoletos
- Cumplir con regulaciones (GDPR)
- Optimizar rendimiento
- Liberar espacio de almacenamiento

### ❌ Sin Sistema de Limpieza

```
Día 1:   10 usuarios, 50 productos     →  Base de datos: 1 MB
Mes 1:   100 usuarios, 500 productos   →  Base de datos: 10 MB
Año 1:   5000 usuarios, 20000 productos → Base de datos: 500 MB

Problemas:
- 4500 usuarios nunca volvieron a iniciar sesión (cuentas basura)
- 15000 productos de usuarios inactivos (desperdicio)
- Consultas cada vez más lentas
- Espacio en disco creciendo sin control
- Backups gigantes
```

### ✅ Con Sistema de Limpieza (Tu proyecto)

**Arquitectura del Sistema:**

```
┌─────────────────────────────────────────┐
│     SISTEMA DE LIMPIEZA ENTERPRISE      │
└─────────────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────┐      ┌──────▼──────┐
│ CRON   │      │  TRIGGERS   │
│ Jobs   │      │  BD         │
└───┬────┘      └──────┬──────┘
    │                  │
    │         ┌────────▼─────────┐
    └────────►│  CLEANUP TASKS   │
              └────────┬─────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
   │ Cuentas │   │Categorías│   │ Uploads │
   │Inactivas│   │ Sin Uso │   │Huérfanos│
   └─────────┘   └─────────┘   └─────────┘
```

**Componente 1: Limpieza de Cuentas Inactivas**

```python
def cleanup_inactive_accounts():
    """
    Política de retención: 30 días
    - Si no iniciaste sesión en 30 días → ELIMINACIÓN
    - Si te registraste pero nunca iniciaste sesión → ELIMINACIÓN
    """
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    # Estrategia 1: Nunca iniciaron sesión
    never_logged_users = User.query.filter(
        User.last_login.is_(None),        # last_login es NULL
        User.created_at < one_month_ago   # Creado hace más de 30 días
    ).all()
    
    # Estrategia 2: Usuarios inactivos
    inactive_users = User.query.filter(
        User.last_login.isnot(None),      # Sí iniciaron sesión alguna vez
        User.last_login < one_month_ago   # Pero hace más de 30 días
    ).all()
    
    # Combinar ambos grupos
    all_inactive_users = never_logged_users + inactive_users
    
    # Eliminar con CASCADE (ver sección 8)
    for user in all_inactive_users:
        db.session.delete(user)  # También elimina productos, página, categorías
    
    db.session.commit()
    return len(all_inactive_users)
```

**Componente 2: Limpieza de Categorías Sin Uso**

```python
def cleanup_unused_categories():
    """
    Política: Categorías personalizadas sin productos y con más de 7 días
    - Categorías del sistema (is_default=True) → NUNCA se eliminan
    - Categorías sin productos y antiguas → ELIMINACIÓN
    """
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    
    unused_categories = Category.query.filter(
        Category.is_default == False,              # No es categoría del sistema
        Category.created_at < one_week_ago,        # Tiene más de 7 días
        ~Category.products.any()                   # No tiene productos asociados
    ).all()
    
    for category in unused_categories:
        db.session.delete(category)
    
    db.session.commit()
    return len(unused_categories)
```

**Componente 3: Limpieza de Archivos Huérfanos (Bonus)**

```python
def cleanup_orphan_uploads():
    """
    Elimina imágenes en /uploads que no están referenciadas en la BD
    """
    import os
    from backend.models import Product, Page
    
    upload_folder = app.config['UPLOAD_FOLDER']
    
    # Obtener todas las imágenes en uso
    product_images = {p.image_url for p in Product.query.all() if p.image_url}
    page_logos = {p.logo_url for p in Page.query.all() if p.logo_url}
    used_images = product_images | page_logos
    
    # Archivos en disco
    disk_files = set(os.listdir(upload_folder))
    
    # Archivos huérfanos = en disco pero no en BD
    orphan_files = disk_files - used_images
    
    deleted_count = 0
    for filename in orphan_files:
        file_path = os.path.join(upload_folder, filename)
        try:
            os.remove(file_path)
            deleted_count += 1
        except Exception as e:
            logger.error(f"Error eliminando {filename}: {e}")
    
    return deleted_count
```

### 📊 Métricas y Logging

```python
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    filename='cleanup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_cleanup_metrics(deleted_users, deleted_categories, deleted_files):
    """Registra métricas de limpieza"""
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'deleted_users': deleted_users,
        'deleted_categories': deleted_categories,
        'deleted_files': deleted_files,
        'total_deleted': deleted_users + deleted_categories + deleted_files
    }
    
    logging.info(f"LIMPIEZA COMPLETADA: {metrics}")
    return metrics
```

**Ejemplo de log generado:**
```
2025-01-15 03:00:01 - INFO - 🧹 Iniciando limpieza automática
2025-01-15 03:00:02 - INFO - Eliminando cuenta inactiva: usuario123 (ID: 45)
2025-01-15 03:00:02 - INFO - Eliminando cuenta inactiva: test_user (ID: 67)
2025-01-15 03:00:03 - INFO - ✅ Limpieza de usuarios: 2 cuentas eliminadas
2025-01-15 03:00:04 - INFO - ✅ Limpieza de categorías: 5 categorías eliminadas
2025-01-15 03:00:05 - INFO - ✅ Limpieza de archivos: 8 imágenes eliminadas
2025-01-15 03:00:05 - INFO - LIMPIEZA COMPLETADA: {'timestamp': '2025-01-15T03:00:05', 'deleted_users': 2, 'deleted_categories': 5, 'deleted_files': 8, 'total_deleted': 15}
```

### 🎯 Beneficios del Sistema de Limpieza

✅ **Cumplimiento legal:** GDPR requiere eliminar datos de usuarios inactivos
✅ **Rendimiento:** Base de datos más pequeña = consultas más rápidas
✅ **Costos:** Menos espacio de almacenamiento
✅ **Seguridad:** Menos datos = menos superficie de ataque
✅ **Profesional:** Muestra que entiendes ciclo de vida de datos

---

## 7. 🔄 Control de Versiones Optimista

### ¿Qué es el Control de Versiones Optimista?

Es una técnica para **manejar modificaciones concurrentes** (varios usuarios editando lo mismo al mismo tiempo) sin bloquear la base de datos.

### 🤔 El Problema: Condición de Carrera

**Escenario:**
```
Usuario A y Usuario B editan el mismo producto al mismo tiempo

Tiempo  Usuario A                    Usuario B                    Base de Datos
-----   -------------------------    -------------------------    ---------------
10:00   Lee producto (precio: $100)  
10:01                                Lee producto (precio: $100)
10:02   Cambia a $120
10:03                                Cambia a $150
10:04   Guarda → precio: $120        
10:05                                Guarda → precio: $150        precio: $150

❌ PROBLEMA: El cambio de Usuario A se perdió sin que nadie se dé cuenta
```

### ❌ Enfoque Pesimista (Bloqueos)

```python
# Bloquear la fila mientras se edita
product = Product.query.with_for_update().get(product_id)
# Nadie más puede editar hasta que termine

# ❌ Problemas:
# - Si el usuario se va a tomar café, bloquea a todos
# - Reduce rendimiento
# - Puede causar deadlocks
```

### ✅ Enfoque Optimista (Tu proyecto)

**Agregar campo de versión al modelo:**

```python
class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False)
    
    # Campo de control de versiones
    version = db.Column(db.Integer, default=1, nullable=False)
    
    updated_at = db.Column(
        db.DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
```

**Lógica de actualización optimista:**

```python
from flask import flash, redirect
from sqlalchemy.exc import StaleDataError

@products_bp.route('/edit/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    # 1. Leer producto y versión actual
    product = Product.query.get_or_404(product_id)
    current_version = product.version
    
    # 2. Obtener versión que tenía el usuario al cargar el formulario
    form_version = int(request.form.get('version'))
    
    # 3. Verificar si alguien más modificó el producto
    if current_version != form_version:
        flash(
            '⚠️ Conflicto: Otra persona modificó este producto mientras lo editabas. '
            'Por favor revisa los cambios y vuelve a intentar.',
            'warning'
        )
        return redirect(url_for('products.view', id=product_id))
    
    # 4. Actualizar datos
    product.name = request.form.get('name')
    product.price = request.form.get('price')
    
    # 5. Incrementar versión
    product.version += 1
    
    # 6. Guardar con verificación atómica
    try:
        db.session.commit()
        flash('✅ Producto actualizado correctamente', 'success')
    except StaleDataError:
        db.session.rollback()
        flash('❌ Error: El producto fue modificado. Intenta nuevamente.', 'error')
    
    return redirect(url_for('products.list'))
```

**Formulario con versión oculta:**

```html
<!-- edit_product.html -->
<form method="POST" action="{{ url_for('products.edit', product_id=product.id) }}">
    <!-- Campo oculto con la versión -->
    <input type="hidden" name="version" value="{{ product.version }}">
    
    <label>Nombre:</label>
    <input type="text" name="name" value="{{ product.name }}" required>
    
    <label>Precio:</label>
    <input type="number" name="price" value="{{ product.price }}" step="0.01" required>
    
    <button type="submit">Guardar Cambios</button>
</form>

<!-- Mostrar última actualización -->
<p class="text-muted">
    Última modificación: {{ product.updated_at.strftime('%Y-%m-%d %H:%M:%S') }}
    (Versión {{ product.version }})
</p>
```

### 🔄 Flujo con Control de Versiones

```
Usuario A                          Usuario B                          Base de Datos
---------                          ---------                          -------------
Lee producto                       
version=1, precio=$100            
                                   Lee producto
                                   version=1, precio=$100
Edita precio a $120
Envía: version=1, nuevo_precio=$120
                                   
BD verifica: version==1 ✅
BD actualiza: precio=$120, version=2
                                   
                                   Edita precio a $150
                                   Envía: version=1, nuevo_precio=$150
                                   
                                   BD verifica: version==1 ❌ (ahora es 2)
                                   BD rechaza cambio
                                   
                                   Usuario B recibe advertencia:
                                   "El producto cambió. Versión actual: 2"
                                   
                                   Usuario B recarga página
                                   Ve precio=$120 (cambio de Usuario A)
                                   Decide si quiere cambiar a $150
```

### 🎯 Ventajas del Control de Versiones Optimista

✅ **No bloquea:** Múltiples usuarios pueden leer simultáneamente
✅ **Detecta conflictos:** Avisa cuando hay cambios concurrentes
✅ **Rendimiento:** No hay esperas ni deadlocks
✅ **Auditoría:** Puedes rastrear número de versiones
✅ **Experiencia de usuario:** Mejor que perder cambios silenciosamente

---

## 8. 🔗 Cascade Deletes Avanzados

### ¿Qué son los Cascade Deletes?

Cuando eliminas un registro, **automáticamente elimina todos los registros relacionados**. Es como derribar una ficha de dominó que hace caer todas las demás.

### ❌ Sin Cascade Deletes

```python
# models.py
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# Intentar eliminar usuario
user = User.query.get(1)
db.session.delete(user)
db.session.commit()

# ❌ ERROR: IntegrityError
# No puedes eliminar el usuario porque tiene productos asociados

# Solución manual (tedioso y propenso a errores):
user = User.query.get(1)
for product in user.products:
    db.session.delete(product)  # Eliminar cada producto
db.session.delete(user)
db.session.commit()
```

### ✅ Con Cascade Deletes (Tu proyecto)

**Modelo User con cascadas:**

```python
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)
    
    # Relaciones con CASCADE
    page = db.relationship(
        "Page", 
        uselist=False,              # Un usuario = una página
        back_populates="owner", 
        cascade="all, delete-orphan"  # 🔥 Si eliminas usuario → elimina página
    )
    
    products = db.relationship(
        "Product", 
        back_populates="owner", 
        cascade="all, delete-orphan"  # 🔥 Si eliminas usuario → elimina todos sus productos
    )
    
    custom_categories = db.relationship(
        "Category", 
        back_populates="owner", 
        cascade="all, delete-orphan",  # 🔥 Si eliminas usuario → elimina sus categorías
        foreign_keys="Category.owner_id"
    )
```

**Modelo Page con cascada:**

```python
class Page(db.Model):
    __tablename__ = "pages"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    
    # Foreign key con CASCADE a nivel de base de datos
    owner_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id", ondelete="CASCADE"),  # 🔥 CASCADE en BD
        nullable=False
    )
    
    owner = db.relationship("User", back_populates="page")
```

**Modelo Category con cascada:**

```python
class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    owner_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id", ondelete="CASCADE"),  # 🔥 CASCADE en BD
        nullable=True
    )
    
    owner = db.relationship("User", back_populates="custom_categories")
    
    # Relación many-to-many con productos
    products = db.relationship(
        "Product", 
        secondary="product_categories",  # Tabla intermedia
        back_populates="categories"
    )
```

**Tabla intermedia con CASCADE:**

```python
class ProductCategory(db.Model):
    __tablename__ = "product_categories"
    id = db.Column(db.Integer, primary_key=True)
    
    # Si se elimina el producto → elimina relación
    product_id = db.Column(
        db.Integer, 
        db.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Si se elimina la categoría → elimina relación
    category_id = db.Column(
        db.Integer, 
        db.ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False
    )
```

**Modelo Product con cascadas:**

```python
class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False)
    
    owner_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    owner = db.relationship("User", back_populates="products")
    categories = db.relationship(
        "Category", 
        secondary="product_categories", 
        back_populates="products"
    )
```

### 🌊 Efecto Cascada en Acción

**Eliminar un usuario desencadena:**

```
DELETE FROM users WHERE id = 1;

🔥 CASCADA AUTOMÁTICA:

1. Elimina Page del usuario
   DELETE FROM pages WHERE owner_id = 1;

2. Elimina todos los Products del usuario
   DELETE FROM products WHERE owner_id = 1;
   
3. Elimina todas las relaciones de esos productos
   DELETE FROM product_categories WHERE product_id IN (productos del usuario);

4. Elimina Categories personalizadas del usuario
   DELETE FROM categories WHERE owner_id = 1;

5. Elimina relaciones de esas categorías
   DELETE FROM product_categories WHERE category_id IN (categorías del usuario);

✅ TODO ESTO CON UNA SOLA LÍNEA:
   db.session.delete(user)
   db.session.commit()
```

### 📊 Ejemplo Visual

```
Usuario: john_doe (ID: 1)
│
├─ Page: "Tienda de John" (ID: 10)
│
├─ Products:
│  ├─ Producto A (ID: 100)
│  │  └─ Categorías: [Electrónica, Ofertas]
│  ├─ Producto B (ID: 101)
│  │  └─ Categorías: [Ropa]
│  └─ Producto C (ID: 102)
│     └─ Categorías: [Electrónica]
│
└─ Custom Categories:
   └─ "Mi Categoría Especial" (ID: 50)
      └─ Productos: ninguno

┌─────────────────────────────────────┐
│  db.session.delete(john_doe)        │
│  db.session.commit()                │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  CASCADE DELETE AUTOMÁTICO:         │
├─────────────────────────────────────┤
│  ✅ Page "Tienda de John" eliminada │
│  ✅ Producto A eliminado             │
│  ✅ Producto B eliminado             │
│  ✅ Producto C eliminado             │
│  ✅ 5 relaciones producto-categoría  │
│  ✅ Categoría "Mi Categoría..."     │
├─────────────────────────────────────┤
│  TOTAL: 1 usuario → 10 filas        │
│         eliminadas automáticamente  │
└─────────────────────────────────────┘
```

### 🎯 Tipos de CASCADE

**1. `cascade="all, delete-orphan"` (SQLAlchemy ORM):**
```python
products = db.relationship("Product", cascade="all, delete-orphan")
```
- `all`: Propaga todas las operaciones (save, update, delete, merge, etc.)
- `delete-orphan`: Si un producto ya no tiene owner, se elimina automáticamente

**2. `ondelete="CASCADE"` (Base de datos):**
```python
owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
```
- Ejecuta el CASCADE a nivel de base de datos
- Más rápido y confiable
- Funciona incluso si eliminas directamente con SQL

**3. `SET NULL` (Alternativa):**
```python
owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
```
- En lugar de eliminar, pone NULL en la foreign key
- Útil para datos históricos

**4. `RESTRICT` (Bloquear):**
```python
owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"))
```
- Impide eliminar si hay datos relacionados
- Para proteger datos críticos

### ⚠️ Precauciones con CASCADE

```python
# ⚠️ PELIGRO: Eliminar usuario borra TODO
user = User.query.get(1)
db.session.delete(user)
db.session.commit()
# Adiós 100 productos, página personalizada, categorías...

# ✅ MEJOR: Confirmar antes
from flask import request

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    confirmation = request.form.get('confirmation')
    
    if confirmation != current_user.username:
        flash('⚠️ Confirmación incorrecta', 'error')
        return redirect(url_for('settings'))
    
    # Mostrar lo que se va a eliminar
    products_count = len(current_user.products)
    
    flash(
        f'⚠️ Se eliminarán: tu página, {products_count} productos y todas tus categorías.',
        'warning'
    )
    
    # Eliminar con logging
    logger.warning(f"Usuario {current_user.username} eliminó su cuenta")
    db.session.delete(current_user)
    db.session.commit()
    
    flash('✅ Cuenta eliminada permanentemente', 'info')
    return redirect(url_for('auth.register'))
```

### 🎯 Ventajas de Cascade Deletes

✅ **Integridad:** No quedan datos huérfanos
✅ **Eficiencia:** Una operación elimina todo lo relacionado
✅ **Mantenimiento:** No hay que recordar eliminar manualmente
✅ **Automatización:** Funciona con el sistema de limpieza
✅ **Profesional:** Así se maneja en aplicaciones enterprise

---

## 🎓 Conclusión

Estos 8 conceptos avanzados convierten tu proyecto de un simple CRUD a una **aplicación de nivel profesional**:

| Concepto | Nivel Básico | Tu Proyecto |
|----------|-------------|-------------|
| **Blueprints** | 1 archivo gigante | Arquitectura modular |
| **Factory Pattern** | Config hardcodeada | Flexible y testeable |
| **Migraciones** | `db.create_all()` | Control de versiones de BD |
| **Docker** | "En mi PC funciona" | Portable y reproducible |
| **CRON** | Limpieza manual | Automatización total |
| **Limpieza Enterprise** | BD crece sin control | Optimización automática |
| **Versionado Optimista** | Pérdida de datos | Detección de conflictos |
| **Cascade Deletes** | Datos huérfanos | Integridad referencial |

### 📚 Recursos para Profundizar

- **Blueprints:** [Flask Blueprints Documentation](https://flask.palletsprojects.com/en/2.3.x/blueprints/)
- **Application Factory:** [Flask Application Factories](https://flask.palletsprojects.com/en/2.3.x/patterns/appfactories/)
- **Migraciones:** [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- **Docker:** [Docker Getting Started](https://docs.docker.com/get-started/)
- **SQLAlchemy Cascade:** [Cascades Documentation](https://docs.sqlalchemy.org/en/14/orm/cascades.html)

### 🚀 Siguiente Nivel

Para llevar tu proyecto aún más allá:
- **Testing automatizado** (pytest, unittest)
- **CI/CD** (GitHub Actions, GitLab CI)
- **Monitoring** (Prometheus, Grafana)
- **Caching** (Redis)
- **Load balancing** (Nginx, multiple containers)
- **Message queues** (Celery, RabbitMQ)

---

**¡Felicitaciones por implementar todos estos conceptos avanzados en tu proyecto!** 🎉

Ahora tienes el conocimiento para explicar cada parte de tu código de forma profesional.

