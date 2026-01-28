import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Multiagro IA", page_icon="🌱", layout="wide")

# Intentar configurar IA
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ Configure su API Key en los Secrets de Streamlit.")

# --- DISEÑO ---
st.markdown("""
    <style>
    .stApp { background: #f0f4f0; }
    .product-card { 
        background: white; padding: 15px; border-radius: 12px; 
        border-left: 5px solid #1b5e20; margin-bottom: 10px; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# Logo
try:
    st.image("Grupo_Multiagro_Mesa de trabajo 1.png", width=320)
except:
    st.image("https://www.grupomultiagro.com/wp-content/uploads/2022/03/logo-multiagro-horizontal.png", width=300)

# --- DATOS ---
PROVINCIAS = ["Azua", "Baoruco", "Barahona", "Dajabón", "Duarte", "Elías Piña", "El Seibo", "Espaillat", "Hato Mayor", "Hermanas Mirabal", "Independencia", "La Altagracia", "La Romana", "La Vega", "María Trinidad Sánchez", "Monseñor Nouel", "Monte Cristi", "Monte Plata", "Pedernales", "Peravia", "Puerto Plata", "Samaná", "Sánchez Ramírez", "San Cristóbal", "San José de Ocoa", "San Juan", "San Pedro de Macorís", "Santiago", "Santiago Rodríguez", "Valverde", "Santo Domingo"]
CULTIVOS_DATA = {
    "Arroz": ["Urea Multiagro", "Pro-Arroz", "Zinc Foliar"],
    "Vegetales (Campo Abierto)": ["Bio-Safe", "Fertirriego Base", "Calcio-Boro"],
    "Vegetales (Invernadero)": ["Plástico Térmico", "Goteo Netafim", "Trampas Amarillas"],
    "Banano / Plátano": ["Sigatoka Elite", "Potasio Soluble"],
    "Cacao": ["Fungicida Cobre", "Fertilizante Floración"],
    "Café": ["Control Roya", "Abono Orgánico"]
}

# --- INTERFAZ ---
tab1, tab2 = st.tabs(["🔍 Diagnóstico IA", "🛒 Catálogo"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        cultivo_sel = st.selectbox("Cultivo", list(CULTIVOS_DATA.keys()))
    with col2:
        prov_sel = st.selectbox("Provincia", PROVINCIAS)

    st.markdown("### 📸 Imagen del Problema")
    foto_camara = st.camera_input("Tomar foto")
    foto_galeria = st.file_uploader("O subir de la galería", type=["jpg", "jpeg", "png"])

    imagen_final = foto_camara if foto_camara is not None else foto_galeria

    if imagen_final:
        img = Image.open(imagen_final)
        st.image(img, width=350, caption="Imagen para análisis")
        
        if st.button("🚀 ANALIZAR CON IA MULTIAGRO"):
            with st.spinner("Nuestra IA está analizando su cultivo..."):
