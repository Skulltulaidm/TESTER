import re
import pandas as pd
import fitz
import streamlit as st
from io import BytesIO

def read_pdf(file_path):
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf_document:
        return "\n".join([page.get_text() for page in pdf_document])

def combine_lines(lines, pattern):
    combined_lines = []
    current_line = ""

    for line in lines:
        if re.match(pattern, line):
            if current_line:
                combined_lines.append(current_line.strip())
            current_line = line
        else:
            current_line += " " + line.strip()

    if current_line:
        combined_lines.append(current_line.strip())

    return "\n".join(combined_lines)


def process_matches(matches):
    data = []
    for match in matches:
        cod_transacc, cantidad = match[4], match[6]
        deposito = cantidad if cod_transacc == "003" else "0"
        retiro = cantidad if cod_transacc != "003" else "0"
        cheque = match[10] if match[10] else match[11]

        data.append(
            {
                "Fecha Operacion": match[0],
                "Fecha": match[1],
                "Referencia": match[2],
                "Descripción": match[3],
                "Cod. Transacc": cod_transacc,
                "Sucursal": match[5],
                "Depositos": deposito,
                "Retiros": retiro,
                "Saldo": match[7],
                "Movimiento": match[8],
                "Descripción Detallada": match[9],
                "Cheque": cheque,
            }
        )

    return pd.DataFrame(data)


# Streamlit UI
st.title("PDF a Excel")
uploaded_file = st.file_uploader("Sube tu archivo PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Procesando PDF..."):
        fecha_pattern = r"\d{2}/\d{2}/\d{4}"

        # Read PDF
        all_text = read_pdf(uploaded_file)
        lines = all_text.split("\n")
        combined_text = combine_lines(lines, fecha_pattern)

        pattern_flexible = re.compile(
            r"(\d{2}/\d{2}/\d{4})\s+"  # Fecha de operación
            r"(\d{2}/\d{2}/\d{4})\s+"  # Fecha
            r"(\d{10})?\s*"  # Referencia (hacerlo más flexible)
            r"([\w\s\.\:\-]+?)\s+"  # Descripción (hacerlo más flexible)
            r"(\d{3})\s+"  # Código de transacción
            r"(\d{4})\s+"  # Sucursal
            r"(\$?\d{1,3}(?:,\d{3})*\.\d{2})\s+"  # Deposito / Retiro
            r"(\$?\d{1,3}(?:,\d{3})*\.\d{2})\s+"  # Saldo
            r"(\d{4})\s+"  # Movimiento
            r"(.*?)\s*"  # Descripción Detallada (opcional)
            r"(?:(-)|(\$?(?!0{1,3}\.\d{2})\d{1,3}(?:,\d{3})*\.\d{2}))\s*"  # Cheque (guion o monto no "00.00")
        )

        matches_flexible = pattern_flexible.findall(combined_text)
        df_flexible = process_matches(matches_flexible)

    if df_flexible.empty:
        st.write("No se encontraron datos en el PDF.")
    else:
        st.write("PDF procesado con éxito.")
        st.dataframe(df_flexible)

        # Descargar como archivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_flexible.to_excel(writer, index=False)
        output.seek(0)

        # Descargar archivo Excel
        st.download_button(
            label="Descargar archivo Excel",
            data=output,
            file_name="Estado_de_Cuenta.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
