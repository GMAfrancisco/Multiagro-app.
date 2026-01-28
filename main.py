import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Multiagro App", page_icon="🌱", layout="wide")

V_OSCURO = "#1B5E20"
V_VIVO = "#388E3C"

# --- 2. CONFIGURACIÓN IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except Exception as e:
    st.error(f"⚠️ Error en API Key: {e}")

# --- 3. ESTILOS CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #F8FAF8; }}
    .main-card {{
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05); border-top: 8px solid {V_OSCURO};
    }}
    .product-card {{
        background: white; border-radius: 12px; padding: 12px;
        text-align: center; border: 1px solid #EEE; min-height: 100px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNCIÓN PARA CARGAR IMÁGENES ---
def cargar_imagen_flexible(nombre_buscado, ancho=None):
    if not os.path.exists("."):
        return st.write(f"⚠️ Error de sistema")
    for archivo_real in os.listdir("."):
        if archivo_real.lower() == nombre_buscado.lower():
            try:
                img = Image.open(archivo_real)
                if ancho:
                    return st.image(img, width=ancho)
                return st.image(img, use_container_width=True)
            except:
                return st.write(f"❌ Error al abrir {nombre_buscado}")
    return st.write(f"⚠️ {nombre_buscado[:15]}...")

# --- 5. CABECERA ---
# Aquí definimos las columnas correctamente para evitar el NameError
col_h1, col_h2, col_h3 = st.columns([1, 2, 1])
with col_h2:
    cargar_imagen_flexible("Grupo_Multiagro_Mesa de trabajo 1.png", ancho=280)

# --- 6. DIAGNÓSTICO ---
LISTA_CULTIVOS = ["Arroz", "Banano", "Cacao", "Vegetales Campo Abierto", "Vegetales Invernadero", "Aguacate", "Café"]

with st.container():
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{V_OSCURO};'>🔍 Diagnóstico IA</h2>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        cultivo = st.selectbox("Cultivo:", LISTA_CULTIVOS)
    with col_b:
        opcion = st.radio("Acción:", ["Subir Foto", "Usar Cámara"], horizontal=True)

    img = None
    if opcion == "Usar Cámara":
        img = st.camera_input("Capturar síntoma")
    else:
        img = st.file_uploader("Galería", type=['jpg', 'png', 'jpeg'])

    if img:
        st.image(img, width=300)
        if st.button("🚀 ANALIZAR AHORA"):
            with st.spinner("Analizando con tecnología Multiagro..."):
                try:
                    pil_img = Image.open(img)
                    prompt = f"Como agrónomo en RD, analiza este {cultivo} e identifica plagas o deficiencias."
                    res = model.generate_content([prompt, pil_img])
                    st.success("¡Diagnóstico listo!")
                    st.write(res.text)
                except Exception as e:
                    st.error(f"Error técnico: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 7. PRODUCTOS ---
st.markdown("<br><h3>🛒 Catálogo Destacado</h3>", unsafe_allow_html=True)
items = [
    {"n": "Fungicida Elite", "p": "RD$ 2,800"},
    {"n": "Bio-Estimulante", "p": "RD$ 3,450"},
    {"n": "Herbicida Total", "p": "RD$ 1,200"},
    {"n": "Potasio Soluble", "p": "RD$ 1,950"}
]

cols_prod = st.columns(4)
for i in range(len(items)):
    with cols_prod[i]:
        st.markdown(f"<div class='product-card'><b>{items[i]['n']}</b><br>{items[i]['p']}</div>", unsafe_allow_html=True)
        txt = urllib.parse.quote(f"Me interesa: {items[i]['n']}")
        st.markdown(f"[💬 Cotizar WhatsApp](https://wa.me/18095551234?text={txt})")

# --- 8. LOGOS (MARCAS ALIADAS) ---
st.markdown("---")
st.markdown("<p style='text-align:center; color:#999; font-weight:bold;'>NUESTRAS EMPRESAS</p>", unsafe_allow_html=True)

logos_finales = [
    "LogoMundoAgricola.jpg", 
    "LogoMultisemillas.jpg", 
    "LogoMultiriegos.jpg", 
    "LogoFortius.png", 
    "LogoAgroservicios.jpg"
]

cols_footer = st.columns
