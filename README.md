# DataProfiler

DataProfiler es una herramienta para analizar y perfilar datos de manera eficiente. Este README proporciona una guía completa sobre cómo configurar y utilizar el proyecto.

## Requisitos

- Python 3.10 o superior
- pip

## Instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/fnsalinas/dataprofiler.git
    cd dataprofiler
    ```

2. Crea un entorno virtual y actívalo:
    ```bash
    python3 -m virtualenv dataprofiler
    source dataprofiler/bin/activate
    ```

3. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## Configuración

Para configurar el proyecto, necesitas crear un archivo `.env` en el directorio raíz del proyecto. Este archivo debe contener las siguientes variables de entorno:

```
APPMAINPATH=/path/to/dataprofiler
REGION_NAME=NOMBRE_DE_LA_REGION
BUCKET_NAME=NOMBRE_DEL_BUCKET
SECRET_NAME=NOMBRE_DEL_SECRETO
```

### Ejemplo de archivo `.env`

```env
APPMAINPATH=/home/user/dataprofiler
REGION_NAME=us-east-2
BUCKET_NAME=dwh-data-pr01
SECRET_NAME=aws_postgres
```

## Uso

Para ejecutar el proyecto, utiliza el siguiente comando:

```bash
python main.py
```

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
