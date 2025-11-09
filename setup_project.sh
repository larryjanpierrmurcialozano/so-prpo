#!/bin/bash
# Script de inicialización completa para Da Vincin
# Ejecuta esto en un dispositivo nuevo para configurar todo automáticamente

echo "🚀 Configuración Automática de Da Vincin"
echo "========================================"
echo ""

# 1. Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo "   Instala Python 3: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi
echo "✅ Python 3 encontrado"

# 2. Verificar que MySQL está instalado
if ! command -v mysql &> /dev/null; then
    echo "⚠️  MySQL no está instalado"
    read -p "¿Deseas instalar MySQL ahora? (s/n): " install_mysql
    if [ "$install_mysql" = "s" ]; then
        echo "📦 Instalando MySQL..."
        sudo apt update
        sudo apt install mysql-server -y
        sudo systemctl start mysql
        sudo systemctl enable mysql
        echo "✅ MySQL instalado"
    else
        echo "❌ MySQL es requerido para este proyecto"
        exit 1
    fi
else
    echo "✅ MySQL encontrado"
    # Verificar si MySQL está corriendo
    if ! systemctl is-active --quiet mysql; then
        echo "⚠️  MySQL no está corriendo. Iniciando..."
        sudo systemctl start mysql
    fi
    echo "✅ MySQL está corriendo"
fi

# 3. Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv .venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual encontrado"
fi

# 4. Activar entorno virtual e instalar dependencias
echo "📦 Instalando dependencias..."
source .venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencias instaladas"

# 5. Verificar archivo .env
if [ ! -f ".env" ]; then
    echo "⚠️  Archivo .env no encontrado. Creando desde ejemplo..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales de MySQL"
    echo "   Especialmente MYSQL_PASSWORD"
    read -p "Presiona Enter para continuar..."
fi

# 6. Configurar MySQL (crear usuario y base de datos)
echo "🔧 Configurando MySQL..."
if [ -f "setup_mysql.sh" ]; then
    ./setup_mysql.sh
else
    echo "⚠️  Script setup_mysql.sh no encontrado"
    echo "   Creando base de datos manualmente..."

    # Intentar crear con el script de Python
    python3 backend/db_setup.py
fi

# 7. Aplicar migraciones
echo "🔄 Aplicando migraciones de base de datos..."
export FLASK_APP=backend.app:create_app

if [ ! -d "migrations" ]; then
    flask db init
fi

flask db migrate -m "Initial setup" > /dev/null 2>&1
flask db upgrade

if [ $? -eq 0 ]; then
    echo "✅ Migraciones aplicadas"
else
    echo "⚠️  Error al aplicar migraciones (puede ser normal si ya están aplicadas)"
fi

# 8. Resumen
echo ""
echo "========================================"
echo "🎉 ¡Configuración completada!"
echo "========================================"
echo ""
echo "📋 Para iniciar el proyecto ejecuta:"
echo "   python run.py"
echo ""
echo "🌐 O desde tu IDE:"
echo "   Abre run.py y presiona Run"
echo ""
echo "📊 Para gestionar la base de datos:"
echo "   Abre MySQL Workbench y conecta con:"
echo "   - Host: localhost"
echo "   - Usuario: davincin_user"
echo "   - Contraseña: davincin2025"
echo "   - Base de datos: inventario_davincin"
echo ""
"""
Script para aplicar migraciones automáticamente al iniciar
"""
import os
import subprocess
import sys

def run_migrations():
    """Aplicar migraciones de base de datos automáticamente"""
    print("\n🔄 Verificando migraciones de base de datos...")

    migrations_dir = os.path.join(os.path.dirname(__file__), '..', 'migrations')

    # Si no existe el directorio de migraciones, inicializarlo
    if not os.path.exists(migrations_dir):
        print("⚠️  No se encontró el directorio de migraciones. Inicializando...")
        result = subprocess.run(
            ['flask', 'db', 'init'],
            env={**os.environ, 'FLASK_APP': 'backend.app:create_app'},
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Error al inicializar migraciones: {result.stderr}")
            return False
        print("✅ Migraciones inicializadas")

    # Verificar si hay migraciones pendientes
    result = subprocess.run(
        ['flask', 'db', 'current'],
        env={**os.environ, 'FLASK_APP': 'backend.app:create_app'},
        capture_output=True,
        text=True
    )

    # Si no hay versión actual, aplicar migraciones
    if 'None' in result.stdout or result.returncode != 0:
        print("⚠️  Se detectaron migraciones pendientes. Aplicando...")

        # Generar migración si no existe
        result = subprocess.run(
            ['flask', 'db', 'migrate', '-m', 'Auto migration'],
            env={**os.environ, 'FLASK_APP': 'backend.app:create_app'},
            capture_output=True,
            text=True
        )

        # Aplicar migraciones
        result = subprocess.run(
            ['flask', 'db', 'upgrade'],
            env={**os.environ, 'FLASK_APP': 'backend.app:create_app'},
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ Migraciones aplicadas exitosamente")
            return True
        else:
            print(f"❌ Error al aplicar migraciones: {result.stderr}")
            return False
    else:
        print("✅ Base de datos actualizada")
        return True

if __name__ == '__main__':
    run_migrations()

