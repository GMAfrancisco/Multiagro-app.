import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Multiagro App", page_icon="🌱", layout="wide")

# Colores Corporativos
VERDE_OSCURO = "#1B5E20"
VERDE_VIVO = "#388E3C"

# --- CONFIGURACIÓN IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except:
    st.error("⚠️ Error en API Key. Verifique los Secrets en Streamlit.")

# --- DISEÑO ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #F8FAF8; }}
    .main-card {{
        background: white; padding: 30px; border-radius: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.03); border-top: 10px solid {VERDE_OSCURO};
    }}
    .product-card {{
        background: white; border-radius: 15px; padding: 15px;
        text-align: center; border: 1px solid #EAEAEA; min-height: 150px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
try:
    st.image("Grupo_Multiagro_Mesa de trabajo 1.png", width=300)
except:
    st.title("GRUPO MULTIAGRO")

st.markdown(f"<h1 style='color:{VERDE_OSCURO}; text-align:center;'>Consultor AgTech Multiagro</h1>", unsafe_allow_html=True)

# --- MÓDULO DE DIAGNÓSTICO ---
with st.container():
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("🔍 Diagnóstico de Cultivos")
    
    c1, c2 = st.columns(2)
    with c1:
        cultivo_sel = st.selectbox("Seleccione su Cultivo", ["Arroz", "Banano / Plátano", "Cacao", "Vegetales Campo Abierto", "Vegetales Invernadero", "Aguacate", "Café"])
    with c2:
        modo_captura = st.radio("Método:", ["Subir Archivo", "Cámara en vivo"], horizontal=True)

    img_input = None
    if modo_captura == "Cámara en vivo":
        img_input = st.camera_input("Capturar síntoma")
    else:
        img_input = st.file_uploader("Subir foto de la galería", type=['jpg', 'png', 'jpeg'])

    if img_input:
        st.image(img_input, width=320)
        if st.button("🚀 INICIAR ANÁLISIS"):
            with st.spinner("Nuestro agrónomo digital está analizando..."):
                try:
                    img_pil = Image.open(img_input)
                    instruccion = f"Como experto agrónomo en República Dominicana, analiza la imagen de este cultivo de {cultivo_sel}. Identifica plagas o deficiencias y recomienda soluciones de Grupo Multiagro."
                    response = model.generate_content([instruccion, img_pil])
                    
                    st.success("Diagnóstico Completado")
                    st.markdown("### 📋 Resultados:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error al conectar con la IA: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# --- CATÁLOGO ---
st.markdown("<br><h3>🛒 Productos Destacados</h3>", unsafe_allow_html=True)
items = [
    {"n": "Fungicida Elite", "p": "RD$ 2,800"},
    {"n": "Bio-Estimulante", "p": "RD$ 3,450"},
    {"n": "Herbicida Total", "p": "RD$ 1,200"},
    {"n": "Potasio Soluble", "p": "RD$ 1,950"}
]

cols = st.columns(4)
for idx, col in enumerate(cols):
