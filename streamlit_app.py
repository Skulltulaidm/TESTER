import streamlit as st
import importlib

st.title("Conversor de PDF a Excel")

# Elegir el banco
banco = st.selectbox("Selecciona el banco de tu estado de cuenta:", ["Monex", "Banorte", "Santander"])

# Subir archivo PDF
uploaded_file = st.file_uploader("Sube tu estado de cuenta en PDF:", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Procesando el archivo PDF..."):
        # Importación dinámica del módulo del banco seleccionado
        bank_module = importlib.import_module(banco.lower())

        # Procesamiento del PDF usando la función del módulo del banco
        output = bank_module.process_pdf(uploaded_file)

    st.success("Proceso completado")

    # Descargar archivo Excel
    st.download_button(
        label="Descargar archivo Excel",
        data=output,
        file_name=f"Estado_de_Cuenta_{banco}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
