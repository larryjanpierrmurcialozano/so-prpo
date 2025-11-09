#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}📅 CONFIGURACIÓN DE LIMPIEZA AUTOMÁTICA${NC}"
echo "=================================================="

PROJECT_DIR="/home/larry/IdeaProjects/so prpo"
CLEANUP_SCRIPT="$PROJECT_DIR/auto_cleanup.sh"

if [ ! -f "$CLEANUP_SCRIPT" ]; then
    echo -e "${RED}❌ Error: No se encontró el script auto_cleanup.sh${NC}"
    exit 1
fi

chmod +x "$CLEANUP_SCRIPT"
echo -e "${GREEN}✅ Script auto_cleanup.sh ahora es ejecutable${NC}"

CRON_JOB="0 3 * * * $CLEANUP_SCRIPT >> $PROJECT_DIR/cleanup_logs.txt 2>&1"

(crontab -l 2>/dev/null | grep -v "$CLEANUP_SCRIPT"; echo "$CRON_JOB") | crontab -

echo -e "\n${GREEN}✅ Tarea CRON configurada exitosamente${NC}"
echo -e "📋 Configuración: Se ejecutará todos los días a las 3:00 AM"
echo ""
echo -e "${YELLOW}Tareas CRON actuales:${NC}"
crontab -l | grep cleanup

echo ""
echo -e "${YELLOW}Para verificar los logs de limpieza:${NC}"
echo "  tail -f $PROJECT_DIR/cleanup_logs.txt"
echo ""
echo -e "${YELLOW}Para eliminar la tarea automática:${NC}"
echo "  crontab -e  # y eliminar la línea manualmente"
echo ""
echo "=================================================="

