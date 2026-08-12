"""
Módulo de procesamiento de datos y lectura de Excel.
"""

import io
import math
from typing import Dict, Any, Tuple

import pandas as pd

from config import TAMANO_BATCH, COLUMNA_RUC_DEFAULT
from validators import validate_ruc_dataframe


def load_excel_rucs(uploaded_file) -> pd.DataFrame:
    """
    Lee el Excel forzando texto para preservar exactamente los RUC.
    """
    try:
        df = pd.read_excel(uploaded_file, dtype=str)
        df.columns = df.columns.astype(str).str.strip()
        return df
    except Exception as e:
        raise ValueError(f"Error al leer el archivo Excel: {str(e)}") from e


def process_data_for_batch(
    df: pd.DataFrame,
    remove_duplicates: bool = True,
    batch_size: int = TAMANO_BATCH
) -> Tuple[pd.Series, pd.DataFrame, Dict[str, Any]]:
    """
    Valida los RUC y calcula la distribución de lotes.
    """
    if batch_size <= 0:
        raise ValueError("El tamaño de Batch debe ser mayor que cero.")

    valid_rucs, invalid_df, stats = validate_ruc_dataframe(
        df=df,
        column_name=COLUMNA_RUC_DEFAULT,
        remove_duplicates=remove_duplicates
    )

    total_validos = len(valid_rucs)

    if total_validos > 0:
        total_batches = math.ceil(total_validos / batch_size)
        full_batches = total_validos // batch_size
        last_batch_count = total_validos % batch_size

        if last_batch_count == 0:
            last_batch_count = batch_size
            # Si todos son lotes completos, el último ya está incluido en full_batches.
            batch_final_parcial = False
        else:
            batch_final_parcial = True
    else:
        total_batches = 0
        full_batches = 0
        last_batch_count = 0
        batch_final_parcial = False

    stats.update({
        "total_batches": total_batches,
        "full_batches": full_batches,
        "last_batch_count": last_batch_count,
        "batch_final_parcial": batch_final_parcial,
        "batch_size": batch_size,
    })

    return valid_rucs, invalid_df, stats


def export_invalid_to_excel(invalid_df: pd.DataFrame) -> bytes:
    """
    Genera un Excel con los registros inválidos.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        invalid_df.to_excel(writer, index=False, sheet_name="RUC_Invalidos")

    output.seek(0)
    return output.getvalue()
