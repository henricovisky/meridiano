#!/bin/bash
# start_meridiano.sh
# Script para ser executado via cron em um servidor Ubuntu (1GB RAM)

# ATENÇÃO: Altere este caminho para o diretório real do projeto no servidor Ubuntu
PROJECT_DIR="/opt/meridiano" 
VENV_DIR="$PROJECT_DIR/.venv"

# Adiciona timestamp para os logs do cron
echo "==============================================="
echo "Iniciando Meridiano: $(date)"
echo "==============================================="

# Navega até o diretório do projeto
cd "$PROJECT_DIR" || { echo "Falha ao acessar o diretório $PROJECT_DIR"; exit 1; }

# Atualiza o repositório
echo "Executando git pull..."
git pull origin main

# Ativa o ambiente virtual
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "Ambiente virtual não encontrado em $VENV_DIR"
    exit 1
fi

# Instala/atualiza dependências, caso existam novidades no requirements ou pyproject
# poetry install --only main (caso use poetry) ou pip install -r requirements.txt
# echo "Atualizando dependências..."
# pip install -e .

# Executa o pipeline principal do meridiano (scraping, processing, briefing)
echo "Executando run_briefing.py..."
export PYTHONPATH="$PROJECT_DIR/src"
python3 src/meridiano/run_briefing.py --model gemini/gemma-3-4b-it --limit 5 --all

# Atualiza a página web (assumindo que o Flask roda via systemd)
# Descomente e ajuste o nome do serviço abaixo para reiniciar a aplicação web
echo "Reiniciando serviço da página web..."
sudo systemctl restart meridiano-web.service

echo "==============================================="
echo "Finalizado: $(date)"
echo "==============================================="
