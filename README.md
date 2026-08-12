# Generador Batch SUNAT

Aplicación web en Python + Streamlit para preparar archivos TXT por lotes a partir de una columna de RUC en Excel.

## Funcionalidad

- Lee un archivo `.xlsx` con una columna `RUC`.
- Trata los RUC como texto.
- Valida que cada RUC tenga exactamente 11 dígitos.
- Reporta vacíos, inválidos y duplicados.
- Permite eliminar duplicados conservando la primera aparición.
- Divide los RUC válidos en lotes de máximo 200.
- Genera `Batch_1.txt`, `Batch_2.txt`, etc.
- Cada línea se genera como `RUC|` seguida de salto de línea.
- Comprime todos los TXT en `BATCH_SUNAT.zip`.
- No crea miles de archivos temporales en disco.

## Estructura

```text
batch_sunat/
├── app.py
├── config.py
├── validators.py
├── data_processor.py
├── batch_generator.py
├── requirements.txt
└── README.md
```

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

## Formato de salida

```text
10000396170|
10000396171|
10000396172|
```

Cada TXT contiene como máximo 200 RUC y no incluye encabezado.

## Nota

Esta aplicación prepara archivos de texto para un flujo de consulta masiva. No es un servicio oficial de SUNAT y no envía información directamente a SUNAT.
