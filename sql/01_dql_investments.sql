
/*
AUTOR: Fabio Salinas
FECHA: 2025-02-24


DESCRIPCIÓN: Este script recupera todas las columnas de la tabla 'investments' en el esquema 'market_prod'.

TABLA: market_prod.investments
COLUMNAS:
    - created_at: TIMESTAMP, la fecha y hora en que se creó el registro.
    - updated_at: TIMESTAMP, la fecha y hora en que se actualizó por última vez el registro.
    - id: INTEGER, el identificador único para el registro de inversión.
    - item: VARCHAR, el nombre o descripción del artículo de inversión.
    - concepto: VARCHAR, el concepto o categoría de la inversión.
    - fecha: DATE, la fecha de la inversión.
    - moneda: VARCHAR, la moneda de la inversión.
    - valor: DECIMAL, el valor de la inversión.
    - propietario: VARCHAR, el propietario de la inversión.
    - umbral_venta: DECIMAL, el umbral de venta para la inversión.
    - umbral_compra: DECIMAL, el umbral de compra para la inversión.
    - aplicacion: VARCHAR, la aplicación o plataforma asociada con la inversión.

USO: Esta consulta se puede utilizar para obtener todos los registros de inversión junto con sus detalles para análisis o propósitos de informes.
*/

SELECT
    created_at
    , updated_at
    , id
    , item
    , concepto
    , fecha
    , moneda
    , valor
    , propietario
    , umbral_venta
    , umbral_compra
    , aplicacion
FROM market_prod.investments
;
