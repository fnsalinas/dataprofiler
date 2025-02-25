#!/bin/bash

echo "Iniciando la configuración del entorno virtual..."

if [ -f .env ]; then
    echo "Cargando variables de entorno desde el archivo .env..."
    export $(grep -v '^#' .env | xargs)
fi

cd "$APPMAINPATH" || { echo "No se pudo cambiar al directorio $APPMAINPATH"; exit 1; }

# Verificar si el ambiente virtual existe
VENV_PATH="./dataprofiler/bin/activate"
if [ ! -f "$VENV_PATH" ]; then
    echo "❌ Error: El ambiente virtual 'dataprofiler' no existe en la ruta especificada."
    exit 1
fi

# Activar el ambiente virtual
echo "🔹 Activando el ambiente virtual..."
source "$VENV_PATH"

# Verificar si Python está disponible en el entorno virtual
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python no está disponible en el ambiente virtual."
    exit 1
fi

# # Ejecutar el script de FastAPI
# echo "🚀 Iniciando la API con FastAPI..."
# python main.py

# Ejecutar la API con Uvicorn
echo "🚀 Iniciando la API con FastAPI en http://0.0.0.0:8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload