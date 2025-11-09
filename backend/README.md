Instrucciones para el backend

Usamos Flask + SQLAlchemy + Flask-Migrate.

Variables de entorno:
- DATABASE_URL
- SECRET_KEY

crear un virtualenv y ejecutar:

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=mysql://mysql:mysql@localhost:3036/inventario
flask db init
flask db migrate
flask db upgrade
flask run

