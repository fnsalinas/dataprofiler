from typing import List, Dict, Any
import os
from pathlib import Path
from datetime import datetime
import json
import pandas as pd
from ydata_profiling import ProfileReport

from common import get_sql_statement
from aws_secrets_handler import AWSSecretsManager
from db_manager import SQLProcessor, DatabaseConfig
from aws_s3_handler import S3Manager
from logger_config import get_logger

# Configuración de logs
logger = get_logger()

APPMAINPATH = os.environ.get('APPMAINPATH')
REGION_NAME = os.environ.get('REGION_NAME')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
SECRET_NAME = os.environ.get('SECRET_NAME')

def get_df(sql_filename: str) -> pd.DataFrame:
    """
    Obtiene un DataFrame a partir de una consulta SQL almacenada en un archivo.

    Esta función:
    - Obtiene credenciales de AWS Secrets Manager para conectarse a la base de datos.
    - Configura la conexión a PostgreSQL.
    - Carga la consulta SQL desde el archivo indicado.
    - Ejecuta la consulta y devuelve los resultados en un DataFrame de pandas.

    Args:
        sql_filename (str): Nombre del archivo SQL dentro del directorio `/sql/`.

    Returns:
        pd.DataFrame: DataFrame con los resultados de la consulta SQL.

    Raises:
        ValueError: Si alguna de las variables de entorno necesarias no está definida.
        FileNotFoundError: Si el archivo SQL no existe.
        Exception: Si hay un error en la conexión a la base de datos o en la ejecución del SQL.
    """
    logger.info(f"Obteniendo DataFrame desde la base de datos con la consulta '{sql_filename}'...")
    if not REGION_NAME or not SECRET_NAME or not APPMAINPATH:
        logger.error("Las variables de entorno 'REGION_NAME', 'SECRET_NAME' o 'APPMAINPATH' no están definidas.")
        raise ValueError("Las variables de entorno 'REGION_NAME', 'SECRET_NAME' o 'APPMAINPATH' no están definidas.")

    logger.info(f"Obteniendo DataFrame desde la base de datos con la consulta '{sql_filename}'...")
    sql_path = Path(APPMAINPATH) / "sql" / sql_filename

    if not sql_path.exists():
        logger.error(f"El archivo SQL '{sql_path}' no existe.")
        raise FileNotFoundError(f"El archivo SQL '{sql_path}' no existe.")

    try:
        logger.info("Obteniendo credenciales de AWS Secrets Manager...")
        with AWSSecretsManager(REGION_NAME) as sm:
            secret = {"db_type": "postgresql", **sm.get_secret(SECRET_NAME)}

        logger.info("Configurando conexión a la base de datos...")
        dbconfig = DatabaseConfig(**secret)
        sqlprocessor = SQLProcessor(dbconfig)

        logger.info(f"Cargando consulta SQL desde el archivo '{sql_path}'...")
        sql = get_sql_statement(str(sql_path))

        logger.info("Ejecutando consulta SQL...")
        return sqlprocessor.fetch_data(sql)

    except Exception as e:
        logger.error(f"Error al obtener el DataFrame desde la base de datos: {e}")
        raise Exception(f"Error al obtener el DataFrame desde la base de datos: {e}")

def run_profiling(df: pd.DataFrame, profile_name: str) -> Dict[str, Any]:
    """
    Genera un informe de perfilado de datos y lo guarda en formatos HTML, JSON y CSV.
    Luego, sube estos archivos a un bucket de S3.

    Args:
        df (pd.DataFrame): DataFrame a ser perfilado.
        profile_name (str): Nombre del perfil para los archivos generados.

    Returns:
        None
    """
    actual_datetime: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_filepath: str = f"{APPMAINPATH}/profile_output/{actual_datetime}_{profile_name}.html"
    json_filepath: str = f"{APPMAINPATH}/profile_output/{actual_datetime}_{profile_name}.json"
    csv_filepath: str = f"{APPMAINPATH}/profile_output/{actual_datetime}_{profile_name}.csv"
    
    profile = ProfileReport(df, title=f"{actual_datetime}.{profile_name}")
    profile.to_file(html_filepath)
    profile.to_file(json_filepath)

    with open(json_filepath, "r") as f:
        data = json.load(f)

    vars_to_omit: List[str] = ["value_counts_without_nan", "value_counts_index_sorted", "histogram"]
    consolidated_data = {}
    
    for var in data["variables"].keys():
        consolidated_data[var] = {}
        for key in data["variables"][var].keys():
            if key not in vars_to_omit:
                consolidated_data[var][key] = data["variables"][var][key]
    
    df_output = pd.DataFrame(consolidated_data).T.reset_index().rename(columns={"index": "variable"})
    df_output.to_csv(csv_filepath, index=False)

    s3_manager = S3Manager(REGION_NAME)
    s3_manager.upload_file(html_filepath, BUCKET_NAME, f"profiling/{actual_datetime}_{profile_name}.html")
    s3_manager.upload_file(json_filepath, BUCKET_NAME, f"profiling/{actual_datetime}_{profile_name}.json")
    s3_manager.upload_file(csv_filepath, BUCKET_NAME, f"profiling/{actual_datetime}_{profile_name}.csv")
    
    message: Dict[str, Any] = {
        "REGIÓN": REGION_NAME,
        "BUCKET_NAME": BUCKET_NAME,
        "HTML path": f"s3://{BUCKET_NAME}/profiling/{actual_datetime}_{profile_name}.html",
        "JSON path": f"s3://{BUCKET_NAME}/profiling/{actual_datetime}_{profile_name}.json",
        "CSV path": f"s3://{BUCKET_NAME}/profiling/{actual_datetime}_{profile_name}.csv"
        }
    
    logger.info(f"Perfil generado exitosamente para {profile_name}.")
    logger.info(f"Rutas de los archivos generados: {message}")
    
    return message