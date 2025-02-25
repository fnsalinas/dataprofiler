
from typing import Optional
import pandas as pd
import warnings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import cx_Oracle
from contextlib import closing
from pydantic import BaseModel, Field, validator
from logger_config import get_logger

# Configuración de logs
logging = get_logger()

# Suprime warnings irrelevantes de Pandas con SQLAlchemy
warnings.filterwarnings("ignore", category=UserWarning, message="pandas only supports SQLAlchemy connectable")


class DatabaseConnectionError(Exception):
    """Excepción personalizada para errores de conexión a la base de datos."""
    pass


class DatabaseConfig(BaseModel):
    """
    Clase que maneja la configuración de la base de datos y valida sus valores de entrada usando Pydantic.
    """

    db_type: str = Field(..., description="Tipo de base de datos ('postgresql', 'redshift', 'mysql', 'sqlserver', 'oracle')")
    host: str = Field(..., description="Dirección del servidor SQL")
    port: int = Field(..., gt=0, lt=65536, description="Número de puerto (válido entre 1 y 65535)")
    user: str = Field(..., description="Usuario de la base de datos")
    password: str = Field(..., description="Contraseña")
    database: str = Field(..., description="Nombre de la base de datos")
    driver: Optional[str] = Field(None, description="Driver específico (solo para SQL Server y Oracle)")

    @validator("db_type")
    def validate_db_type(cls, value):
        """Valida que el tipo de base de datos sea uno de los permitidos."""
        allowed_db_types = {"postgresql", "redshift", "mysql", "sqlserver", "oracle"}
        if value.lower() not in allowed_db_types:
            raise ValueError(f"Base de datos '{value}' no soportada. Tipos permitidos: {allowed_db_types}")
        return value.lower()

    def get_connection_url(self) -> str:
        """
        Genera la URL de conexión para SQLAlchemy.

        Returns:
            str: URL de conexión.
        """
        db_urls = {
            "postgresql": f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}",
            "redshift": f"redshift+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}",
            "mysql": f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}",
            "sqlserver": f"mssql+pyodbc://{self.user}:{self.password}@{self.host},{self.port}/{self.database}?driver={self.driver or '{ODBC Driver 17 for SQL Server}'}",
            "oracle": f"oracle+cx_oracle://{self.user}:{self.password}@{cx_Oracle.makedsn(self.host, self.port, service_name=self.database)}"
        }
        return db_urls[self.db_type]


def handle_sql_exceptions(func):
    """Decorador para manejar excepciones SQL y registrar errores."""
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logging.error(f"Error en {func.__name__}: {e}")
            raise DatabaseConnectionError(f"Fallo en {func.__name__}: {e}")
    return wrapper


class SQLProcessor:
    """
    Clase para gestionar conexiones y consultas SQL en PostgreSQL, Redshift, MySQL, SQL Server y Oracle.
    """

    def __init__(self, config: DatabaseConfig):
        """
        Inicializa la conexión a la base de datos usando un objeto de configuración validado.

        Args:
            config (DatabaseConfig): Configuración de la base de datos.
        """
        self.config = config
        self.engine = None
        self.session = None
        self.connect()

    def __enter__(self):
        """Habilita el uso de 'with' para conexiones seguras."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al salir del contexto."""
        self.disconnect()

    @handle_sql_exceptions
    def connect(self):
        """Establece conexión con la base de datos y crea el motor SQLAlchemy."""
        self.disconnect()  # Asegurar que no haya conexiones previas
        self.engine = create_engine(self.config.get_connection_url())
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        logging.info(f"Conexión a {self.config.db_type} establecida exitosamente.")

    def disconnect(self):
        """Cierra la conexión con la base de datos si está activa."""
        if self.session:
            self.session.close()
            logging.info("Conexión cerrada correctamente.")

    @handle_sql_exceptions
    def execute_query(self, query: str):
        """
        Ejecuta una consulta SQL sin retorno de datos.

        Args:
            query (str): Consulta SQL a ejecutar.
        """
        with self.engine.begin() as connection:
            connection.execute(text(query))
            logging.info("Consulta ejecutada correctamente.")

    @handle_sql_exceptions
    def fetch_data(self, query: str) -> pd.DataFrame:
        """
        Ejecuta una consulta SQL y devuelve los resultados en un DataFrame.

        Args:
            query (str): Consulta SQL.

        Returns:
            pd.DataFrame: Datos obtenidos.
        """
        return pd.read_sql(text(query), self.engine)

    @handle_sql_exceptions
    def upload_csv_to_table(self, file_path: str, table_name: str, delimiter: str = ","):
        """
        Carga un archivo CSV en una tabla de la base de datos.

        Args:
            file_path (str): Ruta del archivo CSV.
            table_name (str): Nombre de la tabla.
            delimiter (str, opcional): Delimitador del CSV.
        """
        df = pd.read_csv(file_path, delimiter=delimiter)
        self.upload_dataframe_to_table(df, table_name)

    @handle_sql_exceptions
    def upload_dataframe_to_table(self, df: pd.DataFrame, table_name: str):
        """
        Sube un DataFrame a una tabla en la base de datos.

        Args:
            df (pd.DataFrame): DataFrame a cargar.
            table_name (str): Nombre de la tabla destino.
        """
        if df.empty:
            logging.warning("El DataFrame está vacío, no se subirá.")
            return

        df.to_sql(table_name, self.engine, if_exists="append", index=False)
        logging.info(f"DataFrame subido a {table_name}.")
