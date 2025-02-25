
from datetime import datetime
import os
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

def get_logger() -> logger:
    """
    Configura y devuelve una instancia de logger para la aplicación.

    - Escribe logs en consola y en un archivo dentro de `logs/`.
    - Evita agregar múltiples manejadores duplicados.
    - Se asegura de que el directorio de logs exista antes de escribir.
    
    Returns:
        logger: Instancia global de Loguru Logger.
    """
    app_main_path = os.getenv('APPMAINPATH')
    if not app_main_path:
        raise ValueError("La variable de entorno 'APPMAINPATH' no está definida.")

    logs_dir = os.path.join(app_main_path, 'logs')
    os.makedirs(logs_dir, exist_ok=True)  # Asegurar que el directorio existe

    log_file_date = datetime.now().strftime('%Y%m%d')
    log_file_path = os.path.join(logs_dir, f'{log_file_date}_log_app.log')

    # Obtener todos los manejadores activos en Loguru
    existing_handlers = {h for h in logger.__dict__["_core"].handlers.values()}

    # Si no hay un manejador de archivo, lo agregamos
    if not any("log_app.log" in str(h) for h in existing_handlers):
        logger.add(
            log_file_path,
            rotation="1 day",
            retention="7 days",
            backtrace=True,
            diagnose=True,
            level="INFO",
            colorize=False,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}",
        )

    return logger
