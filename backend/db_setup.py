"""
Utilidad para verificar y crear la base de datos MySQL automáticamente
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_mysql_config():
    return {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'port': int(os.environ.get('MYSQL_PORT', 3306)),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', ''),
        'database': os.environ.get('MYSQL_DB', 'inventario_davincin'),
        'charset': 'utf8mb4'
    }

def check_and_create_database():
    config = get_mysql_config()
    db_name = config.pop('database')

    try:
        connection = pymysql.connect(**config)
        cursor = connection.cursor()

        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        result = cursor.fetchone()

        if not result:
            print(f"⚠️  Base de datos '{db_name}' no encontrada. Creando...")
            cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Base de datos '{db_name}' creada exitosamente")
        else:
            print(f"✅ Base de datos '{db_name}' ya existe")

        cursor.close()
        connection.close()
        return True

    except pymysql.err.OperationalError as e:
        print(f"❌ Error al conectar a MySQL: {e}")
        print(f"\n💡 Soluciones posibles:")
        print(f"   1. Verifica que MySQL esté corriendo: systemctl status mysql")
        print(f"   2. Verifica las credenciales en el archivo .env")
        print(f"   3. Si usas 'root', ejecuta: sudo mysql")
        print(f"      Luego: CREATE USER '{config['user']}'@'localhost' IDENTIFIED BY '{config['password']}';")
        print(f"      Y: GRANT ALL PRIVILEGES ON *.* TO '{config['user']}'@'localhost'; FLUSH PRIVILEGES;")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def check_and_create_user():
    config = get_mysql_config()
    user = config['user']
    password = config['password']

    if user.lower() == 'root':
        return True

    try:
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user='root',
            password='',
            charset='utf8mb4'
        )
        cursor = connection.cursor()

        cursor.execute(f"SELECT User FROM mysql.user WHERE User = '{user}'")
        result = cursor.fetchone()

        if not result:
            print(f"⚠️  Usuario '{user}' no encontrado. Creando...")
            cursor.execute(f"CREATE USER IF NOT EXISTS '{user}'@'localhost' IDENTIFIED BY '{password}'")
            cursor.execute(f"GRANT ALL PRIVILEGES ON {config['database']}.* TO '{user}'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")
            print(f"✅ Usuario '{user}' creado exitosamente")

        cursor.close()
        connection.close()
        return True

    except Exception:
        return True

def check_and_add_missing_columns():
    config = get_mysql_config()

    try:
        connection = pymysql.connect(**config)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'users' 
            AND COLUMN_NAME = 'last_login'
        """, (config['database'],))

        result = cursor.fetchone()

        if not result:
            print("⚠️  Columna 'last_login' no encontrada. Agregando...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN last_login DATETIME NULL
            """)
            connection.commit()
            print("✅ Columna 'last_login' agregada exitosamente")
        else:
            print("✅ Columna 'last_login' ya existe")

        cursor.close()
        connection.close()
        return True

    except Exception as e:
        print(f"❌ Error al verificar/agregar columnas: {e}")
        return False

if __name__ == '__main__':
    print("🔍 Verificando configuración de MySQL...")
    check_and_create_user()
    check_and_create_database()
    check_and_add_missing_columns()
