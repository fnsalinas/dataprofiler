#!/bin/bash

echo "Iniciando la configuración del entorno virtual..."

if [ -f .env ]; then
    echo "Cargando variables de entorno desde el archivo .env..."
    export $(grep -v '^#' .env | xargs)
fi

cd "$APPMAINPATH" || { echo "No se pudo cambiar al directorio $APPMAINPATH"; exit 1; }

if [ ! -d "dataprofiler" ]; then
    echo "Creando entorno virtual en el directorio 'dataprofiler'..."
    python3 -m venv dataprofiler
else
    echo "El entorno virtual ya existe."
fi

echo "Activando el entorno virtual..."
source dataprofiler/bin/activate

echo "Actualizando pip..."
pip install --upgrade pip

echo "Instalando el paquete en modo editable..."
pip install -e .

echo "Instalando las dependencias del paquete..."
pip install -r requirements.txt

echo "Configuración del entorno virtual completa."
