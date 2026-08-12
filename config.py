"""
Configuración general para la aplicación Generador Batch SUNAT.
Centraliza constantes de negocio, nombres de salida y parámetros de interfaz.
"""

TAMANO_BATCH: int = 200
LONGITUD_RUC: int = 11
DELIMITADOR_SUNAT: str = "|"
COLUMNA_RUC_DEFAULT: str = "RUC"

ZIP_FILENAME: str = "BATCH_SUNAT.zip"
INVALIDOS_FILENAME: str = "RUC_INVALIDOS.xlsx"
PREFIX_BATCH: str = "Batch_"

PREVIEW_ROWS_COUNT: int = 15
PROGRESS_UPDATE_INTERVAL: int = 50
