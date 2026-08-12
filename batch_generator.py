"""
Generación de archivos TXT y ZIP en memoria.
Formato esperado por lote: <RUC>|\n
"""

import io
import zipfile
from typing import Callable, Optional, Sequence

from config import (
    TAMANO_BATCH,
    DELIMITADOR_SUNAT,
    PREFIX_BATCH,
    PROGRESS_UPDATE_INTERVAL,
)


def format_sunat_batch_content(ruc_chunk: Sequence[str]) -> str:
    """
    Genera el contenido exacto de un Batch:
    RUC|
    RUC|
    ...
    """
    return "".join(f"{ruc}{DELIMITADOR_SUNAT}\n" for ruc in ruc_chunk)


def create_batches_zip_in_memory(
    valid_rucs: Sequence[str],
    batch_size: int = TAMANO_BATCH,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> bytes:
    """
    Divide los RUC en lotes y crea BATCH_SUNAT.zip completamente en memoria.
    """
    if batch_size <= 0:
        raise ValueError("El tamaño de Batch debe ser mayor que cero.")

    total_records = len(valid_rucs)

    if total_records == 0:
        raise ValueError(
            "No existen RUC válidos para generar los archivos Batch."
        )

    total_batches = (total_records + batch_size - 1) // batch_size
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED
    ) as zip_file:

        for i in range(total_batches):
            start_idx = i * batch_size
            end_idx = min(start_idx + batch_size, total_records)
            chunk = valid_rucs[start_idx:end_idx]

            batch_content = format_sunat_batch_content(chunk)
            filename = f"{PREFIX_BATCH}{i + 1}.txt"

            # UTF-8 sin BOM.
            zip_file.writestr(filename, batch_content.encode("utf-8"))

            if progress_callback and (
                i % PROGRESS_UPDATE_INTERVAL == 0
                or i == total_batches - 1
            ):
                progress_callback(i + 1, total_batches)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()
