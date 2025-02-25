
from typing import Dict, Any, Optional, List, Tuple
import os
from logger_config import get_logger
from dotenv import load_dotenv
load_dotenv()

# Configuración de logs
logging = get_logger()

def get_sql_statement(sql_file: str) -> str:
    """
    Lee un archivo SQL y devuelve su contenido como una cadena.

    Args:
        sql_file (str): Ruta al archivo SQL.

    Returns:
        str: Contenido del archivo SQL.
    
    Raises:
        FileNotFoundError: Si el archivo no se encuentra.
    """
    logging.info(f"Intentando leer el archivo SQL desde: {sql_file}")
    if not os.path.exists(sql_file):
        logging.error(f"El archivo {sql_file} no se encuentra.")
        raise FileNotFoundError(f"El archivo {sql_file} no se encuentra.")

    with open(sql_file, "r") as file:
        sql_statement = file.read()
        logging.info(f"Archivo SQL leído correctamente desde: {sql_file}")

    return sql_statement

