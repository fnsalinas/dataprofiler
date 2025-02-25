# Documentación de la Carpeta de profile_output

**Autor**: [Fabio Salinas](https://github.com/fnsalinas)  
**Fecha**: 2025-02-24  
**Versión**: 1.0  
**Estado**: Publicado  
**Aplicación**: DataProfiler
**Descripción**: Documentación de la carpeta de salida de perfiles del proyecto DataProfiler.

---

La carpeta de salida de perfiles (`dataprofiler/profile_output/`) contiene todos los archivos de salida generados por el proyecto DataProfiler. Estos archivos contienen información detallada sobre los perfiles de los conjuntos de datos analizados.

## Estructura de la Carpeta

- `YYYYMMDD_HHMMSS_SCHEMA.TABLE.csv`: Archivo CSV con el perfil del conjunto de datos `SCHEMA.TABLE` generado en la fecha `YYYYMMDD` y hora `HHMMSS`.
- `YYYYMMDD_HHMMSS_SCHEMA.TABLE.html`: Archivo HTML con el perfil del conjunto de datos `SCHEMA.TABLE` generado en la fecha `YYYYMMDD` y hora `HHMMSS`.
- `YYYYMMDD_HHMMSS_SCHEMA.TABLE.json`: Archivo JSON con el perfil del conjunto de datos `SCHEMA.TABLE` generado en la fecha `YYYYMMDD` y hora `HHMMSS`.

## Uso de los Archivos

Los archivos de salida de perfiles contienen información detallada sobre los conjuntos de datos analizados, incluyendo estadísticas descriptivas, histogramas, correlaciones, valores nulos, valores únicos, entre otros. Estos archivos pueden ser
utilizados para analizar y visualizar los perfiles de los conjuntos de datos, identificar problemas de calidad de datos, y tomar decisiones informadas sobre el tratamiento de los mismos.

## Mantenimiento de los Archivos

Los archivos de salida de perfiles deben ser mantenidos en la carpeta de salida de perfiles (`dataprofiler/profile_output/`) para futuras referencias y auditorías. Se recomienda mantener una estructura de nombres consistente y ordenada para facilitar la identificación y recuperación de los perfiles de los conjuntos de datos.

## Contacto

Para más información o asistencia, por favor contacta al equipo de desarrollo.
