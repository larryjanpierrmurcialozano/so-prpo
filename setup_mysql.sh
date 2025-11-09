#!/bin/bash

echo "🔧 Configurando MySQL para Da Vincin..."
echo ""

sudo mysql -e "
CREATE DATABASE IF NOT EXISTS inventario_davincin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


CREATE USER IF NOT EXISTS 'davincin_user'@'localhost' IDENTIFIED BY 'davincin2025';

GRANT ALL PRIVILEGES ON inventario_davincin.* TO 'davincin_user'@'localhost';

FLUSH PRIVILEGES;

SELECT 'Base de datos y usuario creados correctamente' AS Status;
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ MySQL configurado correctamente"
    echo ""
    echo "📋 Credenciales:"
    echo "   Usuario: davincin_user"
    echo "   Contraseña: davincin2025"
    echo "   Base de datos: inventario_davincin"
    echo "   Host: localhost"
    echo "   Puerto: 3306"
    echo ""
    echo "🔄 Actualizando archivo .env..."

    cat > .env << 'EOF'
MYSQL_USER=davincin_user
MYSQL_PASSWORD=davincin2025
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=inventario_davincin

SECRET_KEY=dev-secret-key-cambiar-en-produccion
EOF

    echo "✅ Archivo .env actualizado"
    echo ""
    echo "🚀 Ahora puedes ejecutar las migraciones:"
    echo "   flask db migrate -m 'Initial MySQL migration'"
    echo "   flask db upgrade"
else
    echo ""
    echo "❌ Error al configurar MySQL"
    echo "Verifica que MySQL esté corriendo y que tengas permisos sudo"
fi

