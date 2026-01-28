import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACIÓN DE IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ Falta configurar la API Key en los Secrets de Streamlit.")

# --- DISEÑO Y LOGO ---
st.set_page_config(page_title="Multiagro IA", layout="wide")
st.image("Grupo_Multiagro_Mesa de trabajo 1.png", width=300)

# --- BASE DE DATOS DE PRODUCTOS ---
# (Mantenemos tu base de datos de cultivos anterior aquí...)
PRODUCTOS_MULTIAGRO = {
    "Arroz": ["Urea Multiagro", "Pro-Arroz", "Zinc Foliar"],
    "Vegetales (Campo Abierto)": ["Insecticida Bio-Safe", "Fertirriego Base", "Calcio-Boro"],
    # ... (añadir los demás que ya tenemos)
}

st.title("Asistente Agrícola con IA Real 🤖")

tabs = st.tabs(["🔍 Diagnóstico", "🛒 Catálogo"])

with tabs[0]:
    cultivo_sel = st.selectbox("Cultivo a evaluar:", list(PRODUCTOS_MULTIAGRO.keys()))
    foto = st.camera_input("Capturar síntoma")

    if foto:
        img = Image.open(foto)
        st.image(img, caption="Imagen analizada", width=400)
        
        with st.spinner("La IA de Multiagro está analizando el síntoma..."):
            try:
                # Prompt especializado para agronomía dominicana
                prompt = f"Actúa como un experto agrónomo de República Dominicana. Analiza esta imagen de {cultivo_sel}. Identifica posibles plagas, enfermedades o deficiencias nutricionales. Sé conciso y profesional."
                response = model.generate_content([prompt, img])
                
                st.markdown("### 🧠 Diagnóstico de la IA:")
                st.write(response.text)
                
                # RECOMENDACIÓN INTELIGENTE
                st.markdown("---")
                st.subheader(f"🛒 Recomendaciones de Multiagro para {cultivo_sel}:")
                recs = PRODUCTOS_MULTIAGRO.get(cultivo_sel, [])
                cols = st.columns(len(recs))
                for i, p in enumerate(recs):
                    with cols[i]:
                        st.info(f"**{p}**")
                        st.button("Añadir al carrito", key=f"btn_{p}")
            except Exception as e:
                st.error(f"Error en el análisis: {e}")

with tabs[1]:
    st.write("Explorando 2,500+ referencias...")
    # (Aquí va el resto de tu catálogo)
