#!/bin/bash

# Obter o caminho absoluto do script
SCRIPT_PATH="$(realpath "$0")"

# Obter o diretório do script
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

cd "$SCRIPT_DIR"
# Nome do seu aplicativo Streamlit
APP="source/main.py"  # Substitua pelo nome do seu arquivo .py

# Caminho do seu ambiente virtual
VENV_DIR="env"  # Substitua pelo caminho do seu ambiente virtual

# Diretório onde o log será salvo
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

# Nome do arquivo de log com data e hora
LOG_FILE="$LOG_DIR/streamlit_$(date +'%Y-%m-%d_%H-%M-%S').log"

# Ativar o ambiente virtual e verificar se foi bem-sucedido
if ! source "$VENV_DIR/bin/activate"; then
    echo "Erro ao ativar o ambiente virtual." >> "$LOG_FILE"
    exit 1
fi

# Inicia o aplicativo Streamlit em segundo plano e captura o PID
if streamlit run "$APP" --server.port 8501 >> "$LOG_FILE" 2>&1 & then
    PID=$!
    echo "Iniciando App Streamlit." >> "$LOG_FILE"
    echo "PID do processo: $PID" >> "$LOG_FILE"
    echo "Logs estão sendo salvos em: $LOG_FILE"
else
    echo "Erro ao iniciar o aplicativo Streamlit." >> "$LOG_FILE"
    exit 1
fi

