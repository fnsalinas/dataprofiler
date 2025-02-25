
import os
import json
from typing import Dict, Any, List, Optional
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from logger_config import get_logger

# Cargar variables de entorno
load_dotenv()
logger = get_logger()

# Decorador para manejo centralizado de excepciones
def handle_boto3_exceptions(func):
    """Decorador para manejar excepciones de Boto3 y registrar errores."""
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Error en {func.__name__}: {error_code} - {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado en {func.__name__}: {e}")
            raise
    return wrapper

# Validación de estructura de secretos de bases de datos
class DatabaseSecret(BaseModel):
    host: str
    port: int = Field(gt=0, lt=65536)  # Puerto válido entre 1 y 65535
    user: str
    password: str
    database: str

class AWSSecretsManager:
    """Clase para gestionar secretos en AWS Secrets Manager."""
    
    def __init__(self, region_name: Optional[str] = None):
        """
        Inicializa el cliente de AWS Secrets Manager.

        :param region_name: Región de AWS (opcional, por defecto se toma de variables de entorno).
        """
        self.region_name = region_name or os.getenv("REGION_NAME", "us-east-2")
        self.client = boto3.client("secretsmanager", region_name=self.region_name)
        logger.info(f"Cliente de Secrets Manager inicializado en la región {self.region_name}.")
    
    def __enter__(self):
        """Habilita el uso de 'with' para conexiones seguras."""
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Cierra la conexión al terminar el bloque 'with'."""
        self.client.close()
        logger.info("Conexión al cliente de Secrets Manager cerrada.")

    @handle_boto3_exceptions
    def create_secret(self, secret_name: str, secret_data: Any) -> None:
        """
        Crea un secreto en AWS Secrets Manager.

        :param secret_name: Nombre del secreto.
        :param secret_data: Contenido del secreto (dict o string).
        """
        if isinstance(secret_data, dict):
            secret_data = json.dumps(secret_data)

        logger.info(f"Creando secreto: {secret_name}")
        self.client.create_secret(Name=secret_name, SecretString=secret_data)
        logger.info(f"Secreto '{secret_name}' creado exitosamente.")

    @handle_boto3_exceptions
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """
        Obtiene un secreto desde AWS Secrets Manager.

        :param secret_name: Nombre del secreto.
        :return: Diccionario con el secreto decodificado.
        """
        logger.info(f"Obteniendo secreto: {secret_name}")
        response = self.client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(response["SecretString"])

        # Si es un secreto de base de datos, se valida con Pydantic
        if secret_data.get("engine") == "postgres":
            db_secret = DatabaseSecret(
                host=secret_data["host"],
                port=secret_data["port"],
                user=secret_data["username"],
                password=secret_data["password"],
                database=secret_data["dbname"]
            )
            return db_secret.dict()

        return secret_data

    @handle_boto3_exceptions
    def list_secrets(self) -> List[str]:
        """
        Lista todos los secretos en AWS Secrets Manager.

        :return: Lista con los nombres de los secretos.
        """
        logger.info("Listando secretos en AWS Secrets Manager.")
        response = self.client.list_secrets()
        secret_names = [secret["Name"] for secret in response.get("SecretList", [])]
        logger.info(f"Se encontraron {len(secret_names)} secretos.")
        return secret_names

    @handle_boto3_exceptions
    def update_secret(self, secret_name: str, secret_data: Any) -> None:
        """
        Actualiza un secreto en AWS Secrets Manager.

        :param secret_name: Nombre del secreto.
        :param secret_data: Contenido del secreto (dict o string).
        """
        if isinstance(secret_data, dict):
            secret_data = json.dumps(secret_data)

        logger.info(f"Actualizando secreto: {secret_name}")
        self.client.update_secret(SecretId=secret_name, SecretString=secret_data)
        logger.info(f"Secreto '{secret_name}' actualizado correctamente.")
