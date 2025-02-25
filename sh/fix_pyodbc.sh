#!/bin/bash

echo "Actualizando paquetes y asegurando que unixODBC esté instalado..."
sudo apt update && sudo apt install -y unixodbc unixodbc-dev

echo "Verificando la existencia de libodbc.so.2..."
if [ -f /usr/lib/libodbc.so.2 ] || [ -f /usr/lib64/libodbc.so.2 ]; then
    echo "La librería libodbc.so.2 ya existe. No es necesario hacer nada."
else
    echo "libodbc.so.2 no encontrada. Creando enlace simbólico..."
    if [ -f /usr/lib/libodbc.so ]; then
        sudo ln -s /usr/lib/libodbc.so /usr/lib/libodbc.so.2
    elif [ -f /usr/lib64/libodbc.so ]; then
        sudo ln -s /usr/lib64/libodbc.so /usr/lib64/libodbc.so.2
    else
        echo "Error: No se encontró libodbc.so en /usr/lib ni en /usr/lib64."
        exit 1
    fi
fi

echo "Recargando librerías compartidas..."
sudo ldconfig

echo "Prueba de instalación de pyodbc..."
python3 -c "import pyodbc; print('PyODBC importado correctamente. Drivers:', pyodbc.drivers())" || {
    echo "Error al importar pyodbc. Revisa la instalación manualmente."
    exit 1
}

echo "Proceso completado exitosamente."
