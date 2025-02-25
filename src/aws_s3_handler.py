
import boto3
from botocore.exceptions import (
    NoCredentialsError,
    PartialCredentialsError,
    ClientError,
)
from logger_config import get_logger

# Configuración de logs
logger = get_logger()

def handle_s3_exceptions(func):
    """Decorador para manejar excepciones de boto3 en operaciones con S3."""
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except FileNotFoundError:
            logger.error("Archivo no encontrado.")
            return False
        except NoCredentialsError:
            logger.error("Credenciales de AWS no disponibles.")
            return False
        except PartialCredentialsError:
            logger.error("Credenciales de AWS incompletas.")
            return False
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Error en {func.__name__}: {error_code} - {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado en {func.__name__}: {e}")
            return False
    return wrapper

class S3Manager:
    """
    Clase para manejar operaciones de Amazon S3 (Subida, Descarga y Creación de Buckets).
    """

    def __init__(self, region_name: str = "us-east-1"):
        """
        Inicializa el cliente de S3.

        :param region_name: Región de AWS donde se trabajará con S3.
        """
        self.region_name = region_name
        self.s3 = boto3.client("s3", region_name=self.region_name)
        logger.info(f"Cliente S3 inicializado en la región {self.region_name}.")

    @handle_s3_exceptions
    def upload_file(self, local_path: str, bucket_name: str, s3_path: str) -> bool:
        """
        Sube un archivo local a un bucket de S3.

        :param local_path: Ruta del archivo local.
        :param bucket_name: Nombre del bucket de S3.
        :param s3_path: Ruta en S3 donde se subirá el archivo.
        :return: True si la operación es exitosa, False en caso contrario.
        """
        logger.info(f"Subiendo {local_path} a s3://{bucket_name}/{s3_path}.")
        self.s3.upload_file(local_path, bucket_name, s3_path)
        logger.info(f"Archivo {local_path} subido exitosamente a {s3_path} en el bucket {bucket_name}.")
        return True

    @handle_s3_exceptions
    def download_file(self, bucket_name: str, s3_path: str, local_path: str) -> bool:
        """
        Descarga un archivo de un bucket de S3 a una ubicación local.

        :param bucket_name: Nombre del bucket de S3.
        :param s3_path: Ruta del archivo en S3.
        :param local_path: Ruta donde se guardará el archivo localmente.
        :return: True si la operación es exitosa, False en caso contrario.
        """
        logger.info(f"Descargando {s3_path} de s3://{bucket_name} a {local_path}.")
        self.s3.download_file(bucket_name, s3_path, local_path)
        logger.info(f"Archivo {s3_path} descargado exitosamente en {local_path}.")
        return True

    @handle_s3_exceptions
    def create_bucket(self, bucket_name: str) -> bool:
        """
        Crea un bucket en S3.

        :param bucket_name: Nombre del bucket a crear.
        :return: True si el bucket fue creado, False en caso contrario.
        """
        logger.info(f"Creando bucket {bucket_name}.")
        self.s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': self.region_name}
        )
        logger.info(f"Bucket {bucket_name} creado exitosamente en la región {self.region_name}.")
        return True

    @handle_s3_exceptions
    def list_files(self, bucket_name: str, prefix: str = "") -> list:
        """
        Lista los archivos dentro de un bucket S3 opcionalmente filtrando por prefijo.

        :param bucket_name: Nombre del bucket de S3.
        :param prefix: Prefijo opcional para filtrar archivos.
        :return: Lista con los nombres de los archivos en el bucket.
        """
        logger.info(f"Listando archivos en s3://{bucket_name}/{prefix}.")
        response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        files = [obj["Key"] for obj in response.get("Contents", [])]
        logger.info(f"Se encontraron {len(files)} archivos en {bucket_name}.")
        return files

    @handle_s3_exceptions
    def delete_file(self, bucket_name: str, s3_path: str) -> bool:
        """
        Elimina un archivo de un bucket de S3.

        :param bucket_name: Nombre del bucket.
        :param s3_path: Ruta del archivo en S3.
        :return: True si el archivo fue eliminado, False en caso contrario.
        """
        logger.info(f"Eliminando {s3_path} de s3://{bucket_name}.")
        self.s3.delete_object(Bucket=bucket_name, Key=s3_path)
        logger.info(f"Archivo {s3_path} eliminado exitosamente de {bucket_name}.")
        return True
