#!/bin/bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🧹 SISTEMA DE LIMPIEZA AUTOMÁTICA DA VINCIN${NC}"
echo "=================================================="
echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

PROJECT_DIR="/home/larry/IdeaProjects/so prpo"
cd "$PROJECT_DIR" || {
    echo -e "${RED}❌ Error: No se pudo acceder al directorio del proyecto${NC}"
    exit 1
}

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo -e "${GREEN}✅ Entorno virtual activado${NC}"
else
    echo -e "${RED}❌ Error: No se encontró el entorno virtual${NC}"
    exit 1
fi

export FLASK_APP=backend/app.py

echo -e "\n${YELLOW}📊 OBTENIENDO ESTADÍSTICAS PREVIAS...${NC}"
python -c "
import sys
sys.path.append('.')
from backend.cleanup_tasks import get_cleanup_stats
stats = get_cleanup_stats()
print(f'Cuentas inactivas detectadas: {stats[\"inactive_accounts\"]}')
print(f'Categorías no utilizadas detectadas: {stats[\"unused_categories\"]}')
"

echo -e "\n${YELLOW}🔄 EJECUTANDO LIMPIEZA AUTOMÁTICA...${NC}"
python -c "
import sys
sys.path.append('.')
from backend.cleanup_tasks import run_full_cleanup
from backend.extensions import db
from backend.app import create_app

# Crear contexto de aplicación
app = create_app()
with app.app_context():
    results = run_full_cleanup()
    print(f'✅ Limpieza completada:')
    print(f'   - Cuentas eliminadas: {results[\"deleted_accounts\"]}')
    print(f'   - Categorías eliminadas: {results[\"deleted_categories\"]}')
    print(f'   - Timestamp: {results[\"timestamp\"]}')
"

echo -e "\n${GREEN}✅ LIMPIEZA AUTOMÁTICA COMPLETADA${NC}"
echo "=================================================="

LOG_FILE="$PROJECT_DIR/cleanup_logs.txt"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Limpieza automática ejecutada" >> "$LOG_FILE"
