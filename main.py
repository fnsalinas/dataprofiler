
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
from data_profiler import get_df, run_profiling
from logger_config import get_logger

# Inicializar FastAPI
app = FastAPI(
    title="Data Profiler API",
    description="API para generar perfiles de datos a partir de consultas SQL.",
    version="1.2.0"
)

# Obtener logger
logger = get_logger()

# 📌 Modelo de validación con Pydantic
class ProfileRequest(BaseModel):
    profile_name: str = Field(..., example="market_prod.investments", description="Nombre del perfil a generar.")
    sql_filename: str = Field(default="01_dql_investments.sql", example="01_dql_investments.sql",
                              description="Nombre del archivo SQL en la carpeta /sql/.")

def process_profiling(profile_request: ProfileRequest):
    """
    Función que ejecuta el proceso de perfilado de datos.

    Args:
        profile_request (ProfileRequest): Datos validados de la petición.

    Returns:
        str: Mensaje de éxito.
    
    Raises:
        HTTPException: Si hay errores en la ejecución.
    """
    try:
        logger.info(f"Iniciando perfilado para {profile_request.profile_name} con SQL: {profile_request.sql_filename}")

        # Obtener DataFrame desde la consulta SQL
        df = get_df(profile_request.sql_filename)
        if df.empty:
            raise ValueError("El DataFrame está vacío. Verifique la consulta SQL.")

        # Ejecutar el perfilado
        profiling_message = run_profiling(df, profile_request.profile_name)

        logger.info(f"Perfil generado exitosamente para {profile_request.profile_name}")
        
        message = {
            "message": f"Perfil generado correctamente para {profile_request.profile_name}",
            "profile_name": profile_request.profile_name,
            "sql_filename": profile_request.sql_filename,
            "columns": df.columns.tolist(),
            "rows": df.shape[0],
            "columns_count": df.shape[1],
            "profile_path": f"/app/profiles/{profile_request.profile_name}.html",
            "profiling_message": profiling_message
        }
        
        return message

    except FileNotFoundError:
        logger.error(f"Archivo SQL '{profile_request.sql_filename}' no encontrado.")
        raise HTTPException(status_code=404, detail=f"El archivo SQL '{profile_request.sql_filename}' no existe.")

    except ValueError as ve:
        logger.warning(f"Advertencia: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        logger.error(f"Error inesperado al generar el perfil: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/profile/")
def generate_profile(profile_request: ProfileRequest):
    """
    Endpoint para generar un perfil de datos.

    - Obtiene los datos desde un archivo SQL.
    - Ejecuta el perfilado con `run_profiling()`.
    
    Args:
        profile_request (ProfileRequest): Datos validados mediante Pydantic.

    Returns:
        dict: Mensaje de éxito o error.
    """
    message = process_profiling(profile_request)
    return {"message": message}

# 📌 Ejecutar el servidor Uvicorn al ejecutar el script directamente
if __name__ == "__main__":
    logger.info("Iniciando API con Uvicorn en http://0.0.0.0:8000 🚀")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
