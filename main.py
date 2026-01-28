import streamlit as st

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Multiagro IA", page_icon="🌱")
LOGO_URL = "https://www.grupomultiagro.com/wp-content/uploads/2022/03/logo-multiagro-horizontal.png"

# --- INTERFAZ ---
st.image(LOGO_URL, width=200)
st.title("Consultor Agrícola IA")
st.markdown("---")

# Selección de modo de consulta
modo_consulta = st.radio("¿Cómo desea consultar?", ["Asistente IA (Rápido)", "Asesor Multiagro (Personalizado)"])

if modo_consulta == "Asistente IA (Rápido)":
    st.info("🤖 Nuestra IA analizará su cultivo y le dará recomendaciones inmediatas.")
    cultivo = st.selectbox("Cultivo", ["Arroz", "Banano", "Cacao", "Vegetales", "Otros"])
    foto = st.camera_input("Tome una foto al problema")
    
    if foto:
        with st.spinner("Analizando con IA de Multiagro..."):
            # Aquí conectaremos con el modelo de visión más adelante
            st.markdown("### 🧠 Diagnóstico Sugerido:")
            st.write(f"Basado en la imagen de su cultivo de **{cultivo}**, detecto posibles deficiencias nutricionales.")
            st.success("Recomendación: Aplicar Fertilizante Foliar Multiagro 20-20-20.")
            
            # El puente hacia el humano
            st.warning("¿Desea una segunda opinión profesional?")
            if st.button("Solicitar validación de un Agrónomo Real"):
                st.write("📩 Enviando caso a un asesor de su zona...")

else:
    st.header("👨‍🌾 Contacto Directo con Asesor")
    st.write("Suba su consulta y el técnico de su provincia le contactará vía WhatsApp.")
    nombre = st.text_input("Su nombre")
    consulta = st.text_area("Describa su problema")
    if st.button("Contactar Asesor"):
        st.success(f"Gracias {nombre}, un técnico de Multiagro se comunicará con usted.")

st.sidebar.markdown("---")
st.sidebar.write("© 2026 Grupo Multiagro")
