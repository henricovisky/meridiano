#!/bin/bash

# ==============================================================================
# Meridiano Update Script
# Purpose: Sync code, run briefing pipeline, and ensure web app is updated.
# Recommended Trigger: Cron (e.g., every 6 hours)
# ==============================================================================

# 1. Configuração de Caminhos
# Substitua pelo caminho real no seu servidor Ubuntu
PROJECT_DIR="/opt/meridiano"
LOG_FILE="$PROJECT_DIR/cron_update.log"

# Navega para o diretório do projeto
cd "$PROJECT_DIR" || { echo "Erro: Diretorio nao encontrado"; exit 1; }

echo "--- Inicio da Atualizacao: $(date) ---" >> "$LOG_FILE"

# 2. Atualizar Código (Git Pull)
echo "[1/4] Puxando atualizacoes do Git..." >> "$LOG_FILE"
git pull origin main >> "$LOG_FILE" 2>&1

# 3. Rodar o Pipeline do Meridiano (Processamento de Dados)
# O script start_meridiano.py ja cuida do venv e instalacao de dependencias
echo "[2/4] Executando pipeline (start_meridiano.py)..." >> "$LOG_FILE"
# Usamos o python do sistema para rodar o inicializador, que por sua vez usa o venv
python3 start_meridiano.py --all >> "$LOG_FILE" 2>&1

# 4. Atualizar a Pagina Web (Reiniciar Servidor Web)
# Se voce estiver usando systemd (recomendado), descomente a linha abaixo:
echo "[3/4] Reiniciando serviço web (systemd)..." >> "$LOG_FILE"
sudo systemctl restart meridiano.service

# Alternativa: Se estiver rodando via PM2 (otimo para servidores com pouca RAM)
# pm2 restart meridiano >> "$LOG_FILE" 2>&1

# Alternativa simples: Matar e rodar novamente (nao recomendado para producao, mas funciona)
# pkill -f "meridiano.app"
# nohup ./venv/bin/python -m meridiano.app > web_app.log 2>&1 &

echo "[4/4] Processo concluido com sucesso." >> "$LOG_FILE"
echo "--- Fim da Atualizacao: $(date) ---" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
