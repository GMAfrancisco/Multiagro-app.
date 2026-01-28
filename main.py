import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Multiagro IA", page_icon="🌱", layout="wide")

# (Mantenemos tu configuración de IA y CSS igual...)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ Configure su API Key en Secrets.")

# --- DISEÑO ---
st.markdown("<style>.stApp { background: #f0f4f0; } .product-card { background: white; padding: 15px; border-radius: 12px; border-left: 5px solid #1b5e20; margin-bottom: 10px; }</style>", unsafe_allow_html=True)
st.image("Grupo_Multiagro_Mesa de trabajo 1.png", width=320)

# --- DATOS (Simplificados para el ejemplo, pero usa los tuyos completos) ---
PROVINCIAS = ["La Vega", "Moca", "Azua", "San Juan", "Santiago", "Monte Cristi", "Dajabón", "Otras..."]
CULTIVOS_DATA = {"Arroz": ["Urea", "Pro-Arroz"], "Vegetales (Campo Abierto)": ["Bio-Safe", "Calcio"], "Banano": ["Sigatoka-Stop"]}

# --- INTERFAZ ---
tab1, tab2 = st.tabs(["🔍 Diagnóstico IA", "🛒 Catálogo"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        cultivo_sel = st.selectbox("Cultivo", list(CULTIVOS_DATA.keys()))
    with col2:
        prov_sel = st.selectbox("Provincia", PROVINCIAS)

    # --- DOBLE OPCIÓN DE IMAGEN ---
    st.markdown("### 📸 Capturar o Subir Imagen")
    foto_camara = st.camera_input("Tomar foto ahora")
    foto_galeria = st.file_uploader("O elige una foto de tu galería", type=["jpg", "jpeg", "png"])

    # Decidimos cuál imagen usar
    imagen_final = foto_camara if foto_camara is not None else foto_galeria

    if imagen_final:
        img = Image.open(imagen_final)
        st.image(img, width=350, caption="Imagen seleccionada")
        
        if st.button("🚀 ANALIZAR CON IA MULTIAGRO"):
            with st.spinner("Diagnosticando..."):
                prompt = f"Eres un agrónomo experto de Multiagro en Rep. Dominicana. Analiza este {cultivo_
