"""
Generador Batch SUNAT - Aplicación Streamlit.
"""

import altair as alt
import pandas as pd
import streamlit as st

from config import (
    TAMANO_BATCH,
    ZIP_FILENAME,
    INVALIDOS_FILENAME,
    PREVIEW_ROWS_COUNT,
)
from data_processor import (
    load_excel_rucs,
    process_data_for_batch,
    export_invalid_to_excel,
)
from batch_generator import (
    format_sunat_batch_content,
    create_batches_zip_in_memory,
)


st.set_page_config(
    page_title="Generador Batch SUNAT",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.1rem;
            color: #4B5563;
            margin-bottom: 1.5rem;
        }
        .kpi-card {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 0.75rem;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .kpi-title {
            font-size: 0.85rem;
            color: #64748B;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .kpi-value {
            font-size: 1.8rem;
            font-weight: 800;
            color: #0F172A;
            margin-top: 0.3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.title("⚙️ Parámetros")

    remove_duplicates_option = st.checkbox(
        "Eliminar RUC duplicados",
        value=True,
        help=(
            "Conserva la primera aparición de cada RUC. "
            "La cantidad de duplicados se reporta aunque esta opción esté desactivada."
        ),
    )

    st.divider()
    st.markdown("### 📋 Formato Batch")
    st.info(
        f"• **Máximo por archivo:** {TAMANO_BATCH} RUC\n\n"
        "• **Formato:** `<RUC>|` por línea\n\n"
        "• **Longitud:** 11 dígitos numéricos\n\n"
        "• **Sin encabezados ni comillas**"
    )

    st.divider()
    st.caption(
        "Herramienta de preparación de archivos Batch. "
        "No es un servicio oficial de SUNAT."
    )


st.markdown(
    '<div class="main-header">Generador Batch SUNAT</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">'
    'Preparación automatizada de archivos TXT para consultas masivas de RUC'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("### PASO 1 — Cargar archivo Excel")

uploaded_file = st.file_uploader(
    "Seleccione o arrastre su archivo Excel (.xlsx) con la columna 'RUC':",
    type=["xlsx"],
)

if uploaded_file is None:
    st.info(
        "💡 Cargue un archivo Excel para iniciar la validación "
        "y generación de archivos Batch."
    )
    st.stop()


try:
    raw_df = load_excel_rucs(uploaded_file)

    if raw_df.empty:
        st.error("El archivo Excel no contiene registros.")
        st.stop()

    st.success(
        f"📁 Archivo cargado: **{uploaded_file.name}** "
        f"({len(raw_df):,} filas)"
    )

    st.divider()
    st.markdown("### PASO 2 — Análisis y validación de RUC")

    with st.spinner("Validando registros..."):
        valid_rucs, invalid_df, stats = process_data_for_batch(
            df=raw_df,
            remove_duplicates=remove_duplicates_option,
            batch_size=TAMANO_BATCH,
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">RUC cargados</div>
                <div class="kpi-value">{stats["total_cargados"]:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">RUC a procesar</div>
                <div class="kpi-value" style="color:#16A34A;">
                    {stats["validos_unicos"]:,}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Archivos Batch</div>
                <div class="kpi-value" style="color:#2563EB;">
                    {stats["total_batches"]:,}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Máximo por archivo</div>
                <div class="kpi-value">{TAMANO_BATCH}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    sec1, sec2, sec3 = st.columns(3)
    with sec1:
        st.caption(f"⚠️ **Duplicados detectados:** {stats['duplicados_count']:,}")
    with sec2:
        st.caption(f"❌ **Inválidos:** {stats['invalidos_count']:,}")
    with sec3:
        st.caption(f"⚪ **Vacíos:** {stats['registros_vacios']:,}")

    chart_data = pd.DataFrame({
        "Estado": ["A procesar", "Inválidos", "Duplicados", "Vacíos"],
        "Cantidad": [
            stats["validos_unicos"],
            stats["invalidos_count"],
            stats["duplicados_count"],
            stats["registros_vacios"],
        ],
    })

    bar_chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
        .encode(
            x=alt.X("Estado:N", sort=None, title=None),
            y=alt.Y("Cantidad:Q", title="Cantidad de registros"),
            tooltip=["Estado", "Cantidad"],
        )
        .properties(height=220)
    )

    st.altair_chart(bar_chart, use_container_width=True)

    if stats["invalidos_count"] > 0:
        with st.expander(
            f"⚠️ Ver detalle de RUC inválidos "
            f"({stats['invalidos_count']:,})"
        ):
            st.dataframe(
                invalid_df,
                use_container_width=True,
                hide_index=True,
            )

            invalid_excel_bytes = export_invalid_to_excel(invalid_df)

            st.download_button(
                label="⬇️ Descargar RUC_INVALIDOS.xlsx",
                data=invalid_excel_bytes,
                file_name=INVALIDOS_FILENAME,
                mime=(
                    "application/"
                    "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
            )

    st.divider()
    st.markdown("### PASO 3 — Vista previa")

    if stats["validos_unicos"] == 0:
        st.error(
            "No existen RUC válidos para generar archivos Batch."
        )
        st.stop()

    preview_sample = valid_rucs.iloc[:PREVIEW_ROWS_COUNT].tolist()
    preview_txt = format_sunat_batch_content(preview_sample)

    st.write(
        f"**Vista previa de `Batch_1.txt` "
        f"(primeros {len(preview_sample)} registros):**"
    )
    st.code(preview_txt, language="text")

    p1, p2 = st.columns(2)
    with p1:
        st.info(
            f"📌 **Batch 1 contendrá:** "
            f"{min(TAMANO_BATCH, stats['validos_unicos']):,} RUC"
        )
    with p2:
        st.info(
            f"🏁 **Último Batch ({stats['total_batches']}) contendrá:** "
            f"{stats['last_batch_count']:,} RUC"
        )

    st.divider()
    st.markdown("### PASO 4 — Generación y descarga")

    if st.button(
        "🚀 Generar Batch SUNAT",
        type="primary",
        use_container_width=True,
    ):
        progress_bar = st.progress(0)
        status_box = st.status(
            "Preparando generación en memoria...",
            expanded=True,
        )

        def update_progress(current: int, total: int):
            progress_bar.progress(current / total)
            status_box.update(
                label=f"Generando Batch {current:,} de {total:,}..."
            )

        try:
            status_box.write(
                "Dividiendo RUC y construyendo archivos TXT..."
            )

            zip_data = create_batches_zip_in_memory(
                valid_rucs=valid_rucs.tolist(),
                batch_size=TAMANO_BATCH,
                progress_callback=update_progress,
            )

            progress_bar.progress(1.0)
            status_box.update(
                label="Proceso completado correctamente",
                state="complete",
                expanded=False,
            )

            st.success(
                f"✓ **{stats['validos_unicos']:,}** RUC procesados\n\n"
                f"✓ **{stats['total_batches']:,}** archivos TXT generados"
            )

            st.download_button(
                label=f"⬇️ Descargar {ZIP_FILENAME}",
                data=zip_data,
                file_name=ZIP_FILENAME,
                mime="application/zip",
                use_container_width=True,
            )

        except Exception as ex:
            status_box.update(
                label="Ocurrió un error en la generación",
                state="error",
            )
            st.error(f"Error al generar los Batch: {str(ex)}")

except Exception as e:
    st.error(f"Error procesando el archivo: {str(e)}")
