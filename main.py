import streamlit as st

st.set_page_config(page_title="Rescate Multiagro")

st.header("🚜 Grupo Multiagro - Modo Seguro")
st.success("Si ves este mensaje, la App está viva.")

st.info("Por favor, sigue estos pasos:")
st.write("1. Confirma que borraste el logo pesado de GitHub.")
st.write("2. Avisame cuando la App encienda para devolverte todas las funciones (IA, Odoo y Registro).")

if st.button("Revisar archivos disponibles"):
    import os
    st.write(os.listdir("."))
