import os
import sys
from backend.app import create_app
from backend.db_setup import check_and_create_database, check_and_add_missing_columns

if __name__ == '__main__':
    print("\n" + "═" * 70)
    print("██████╗  █████╗     ██╗   ██╗██╗███╗   ██╗ ██████╗██╗███╗   ██╗")
    print("██╔══██╗██╔══██╗    ██║   ██║██║████╗  ██║██╔════╝██║████╗  ██║")
    print("██║  ██║███████║    ██║   ██║██║██╔██╗ ██║██║     ██║██╔██╗ ██║")
    print("██║  ██║██╔══██║    ╚██╗ ██╔╝██║██║╚██╗██║██║     ██║██║╚██╗██║")
    print("██████╔╝██║  ██║     ╚████╔╝ ██║██║ ╚████║╚██████╗██║██║ ╚████║")
    print("╚═════╝ ╚═╝  ╚═╝      ╚═══╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚═╝╚═╝  ╚═══╝")
    print("                    Inventario Online Profesional")
    print("═" * 70)

    print("\n🔧 VERIFICACIÓN DEL SISTEMA")
    print("─" * 40)

    print("├── Verificando conexión MySQL...", end="", flush=True)
    if not check_and_create_database():
        print(" ❌ FALLO")
        print("│")
        print("├── ⚠️  ERROR DE CONEXIÓN A BASE DE DATOS")
        print("├── Posibles causas:")
        print("│   • Servicio MySQL no está ejecutándose")
        print("│   • Credenciales incorrectas en archivo .env")
        print("│   • Puerto 3306 bloqueado o en uso")
        print("│")
        print("├── Soluciones recomendadas:")
        print("│   1. sudo systemctl start mysql")
        print("│   2. Verificar archivo .env")
        print("│   3. mysql -u root -p (probar conexión)")
        print("│")
        response = input("└── ¿Continuar sin base de datos? (s/N): ")
        if response.lower() != 's':
            print("\n🛑 Aplicación detenida por el usuario.")
            print("═" * 70)
            sys.exit(1)
        print("│")
        print("└── ⚠  Continuando en modo degradado...")
    else:
        print(" ✅ TODO OK")

    print("├── Verificando estructura de tablas...", end="", flush=True)
    if check_and_add_missing_columns():
        print(" ✅ TODO OK")
    else:
        print(" Con errores (continuando)")

    print("\n INICIANDO SERVIDOR")
    print("─" * 40)

    app = create_app()

    print(f"\n📊 INFORMACIÓN DEL SERVIDOR")
    print("─" * 40)
    print(f"├── URL Principal: http://localhost:5000")
    print(f"├── Modo: Desarrollo")
    print(f"├── Host: 0.0.0.0 (Acceso externo habilitado)")
    print(f"├── Puerto: 5000")
    print(f"└── Base de datos: MySQL")

    print(f"\n RUTAS PRINCIPALES")
    print("─" * 40)
    print("├── Página Principal")
    print("│   └── http://localhost:5000/")
    print("├── Búsqueda Avanzada")
    print("│   └── http://localhost:5000/search")
    print("└── Dashboard")
    print("    └── http://localhost:5000/dashboard")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
