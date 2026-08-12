"""
Módulo de validación estructural de RUC.
Procesa la columna de RUC mediante operaciones vectorizadas de pandas.
"""

import pandas as pd
from typing import Dict, Any, Tuple

from config import LONGITUD_RUC, COLUMNA_RUC_DEFAULT


def validate_ruc_dataframe(
    df: pd.DataFrame,
    column_name: str = COLUMNA_RUC_DEFAULT,
    remove_duplicates: bool = True
) -> Tuple[pd.Series, pd.DataFrame, Dict[str, Any]]:
    """
    Valida estructuralmente una columna de RUC.

    Un RUC válido para esta aplicación:
    - no está vacío;
    - tiene exactamente 11 caracteres;
    - contiene únicamente dígitos.

    No corrige silenciosamente valores inválidos.
    """

    if column_name not in df.columns:
        cols_lower = {str(col).lower().strip(): col for col in df.columns}
        key = column_name.lower().strip()
        if key in cols_lower:
            column_name = cols_lower[key]
        else:
            raise KeyError(
                f"No se encontró la columna '{column_name}' en el archivo Excel."
            )

    raw_series = df[column_name]

    # Se conserva el contenido como texto y solo se eliminan espacios al inicio/final.
    # No se elimina '.0' ni se modifica el contenido para convertir un valor inválido
    # en aparentemente válido.
    cleaned_series = raw_series.astype("string").str.strip()

    is_empty_mask = (
        raw_series.isna()
        | cleaned_series.isna()
        | cleaned_series.fillna("").isin(["", "nan", "None", "<NA>", "NaN"])
    )

    working = cleaned_series.fillna("")

    is_numeric_mask = working.str.isdigit()
    is_correct_len_mask = working.str.len() == LONGITUD_RUC

    is_valid_mask = is_numeric_mask & is_correct_len_mask & (~is_empty_mask)
    is_invalid_mask = (~is_valid_mask) & (~is_empty_mask)

    valid_series = working[is_valid_mask].copy()

    # El conteo real de duplicados es independiente de si el usuario decide eliminarlos.
    duplicates_count = int(valid_series.duplicated(keep="first").sum())

    if remove_duplicates:
        valid_final = valid_series.drop_duplicates(keep="first")
    else:
        valid_final = valid_series

    invalid_rows_indices = df.index[is_invalid_mask].tolist()
    invalid_raw_values = raw_series[is_invalid_mask].tolist()
    invalid_cleaned_values = working[is_invalid_mask].tolist()

    reasons = []
    for val_clean in invalid_cleaned_values:
        if not val_clean.isdigit():
            reasons.append(
                "Contiene caracteres no numéricos, espacios internos o símbolos"
            )
        elif len(val_clean) != LONGITUD_RUC:
            reasons.append(
                f"Tiene {len(val_clean)} dígitos (se requieren exactamente {LONGITUD_RUC})"
            )
        else:
            reasons.append("Formato estructural inválido")

    # Índice pandas 0-based + encabezado Excel = fila visible Excel.
    excel_rows = [idx + 2 for idx in invalid_rows_indices]

    invalid_df = pd.DataFrame({
        "Fila Excel": excel_rows,
        "Valor Original": invalid_raw_values,
        "Motivo de Invalidez": reasons
    })

    stats = {
        "total_cargados": len(df),
        "registros_vacios": int(is_empty_mask.sum()),
        "total_no_vacios": len(df) - int(is_empty_mask.sum()),
        "validos_unicos": len(valid_final),
        "validos_totales": len(valid_series),
        "invalidos_count": len(invalid_df),
        "duplicados_count": duplicates_count,
        "remove_duplicates_active": remove_duplicates,
    }

    return valid_final.reset_index(drop=True), invalid_df, stats
