import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Multiagro App", page_icon="🌱", layout="wide")

# --- 2. CONFIGURACIÓN IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except:
    st.error("⚠️ Error de conexión con IA.")

# --- 3. ESTILOS PERSONALIZADOS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #F8FAF8; }}
    .main-card {{
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05); border-top: 8px solid #1B5E20;
    }}
    .product-card {{
        background: white; border-radius: 12px; padding: 15px;
        text-align: center; border: 1px solid #EEE;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNCIÓN PARA CARGAR IMÁGENES ---
def mostrar_imagen(nombre_archivo, ancho=None):
    for file in os.listdir("."):
        if file.lower() == nombre_archivo.lower():
            try:
                img = Image.open(file)
                if ancho:
                    return st.image(img, width=ancho)
                return st.image(img, use_container_width=True)
            except:
                pass
    return st.write(f"⚠️ {nombre_archivo}")

# --- 5. CABECERA ---
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
mostrar_imagen("Grupo_Multiagro_Mesa de trabajo 1.png", ancho=300)
st.markdown("<h2 style='color:#1B5E20;'>Consultor AgTech Multiagro</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- 6. MÓDULO DE DIAGNÓSTICO ---
with st.container():
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("🔍 Diagnóstico con Inteligencia Artificial")
    
    col_a, col_b = st.columns(2)
    with col_a:
        cultivo = st.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales Campo Abierto", "Vegetales Invernadero", "Aguacate", "Café"])
    with col_b:
        opcion = st.radio("Método:", ["Subir Foto", "Usar Cámara"], horizontal=True)

    img_input = None
    if opcion == "Usar Cámara":
        img_input = st.camera_input("Capturar")
    else:
        img_input = st.file_uploader("Seleccionar de Galería", type=['jpg', 'png', 'jpeg'])

    if img_input:
        st.image(img_input, width=350, caption="Imagen cargada")
        if st.button("🚀 ANALIZAR AHORA"):
            with st.spinner("La IA de Multiagro está analizando..."):
                try:
                    pil_img = Image.open(img_input)
                    prompt = f"Como experto agrónomo en República Dominicana, analiza este cultivo de {cultivo}. Identifica plagas o deficiencias y recomienda soluciones de Grupo Multiagro."
                    res = model.generate_content([prompt, pil_img])
                    st.success("Análisis completado")
                    st.markdown("### 📋 Diagnóstico Sugerido")
                    st.write(res.text)
                except Exception as e:
                    st.error(f"Error técnico: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 7. PRODUCTOS ---
st.markdown("<br><h3>🛒 Productos Destacados</h3>", unsafe_allow_html=True)
items = [
    {"n": "Fungicida Elite", "p": "RD$ 2,800"},
    {"n": "Bio-Estimulante", "p": "RD$ 3,450"},
    {"n": "Herbicida Total", "p": "RD$ 1,200"},
    {"n": "Potasio Soluble", "p": "RD$ 1,950"}
]
p_cols = st.columns(4)
for i in range(len(items)):
    with p_cols[i]:
        st.markdown(f"<div class='product-card'><b>{items[i]['n']}</b><br><span style='color:#388E3C'>{items[i]['p']}</span></div>", unsafe_allow_html=True)
        txt_wa = urllib.parse.quote(f"Hola Multiagro, me interesa cotizar: {items[i]['n']}")
        st.markdown(f"[💬 WhatsApp](https://wa.me/18095551234?text={txt_wa})")

# --- 8. LOGOS EMPRESAS ---
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray; font-weight:bold;'>NUESTRAS EMPRESAS</p>", unsafe_allow_html=True)

logos_ficheros = [
    "Logo Mundo Agricola.jpg", 
    "Logo Multisemillas.jpg", 
    "IMG-20251217-WA0012.jpg", 
    "Logo-Fortius.png", 
    "Logo-Agroservicios-Final_Mesa de trabajo 1.png"
]

l_cols = st.columns(len(logos_ficheros))
for i, l_nombre in enumerate(logos_ficheros):
    with l_cols[i]:
        mostrar_imagen(l_nombre)

st.markdown("<p style='text-align:center; font-size:12px; color:#aaa; margin-top:50px;'>© 2026 GRUPO MULTIAGRO | RD</p>", unsafe_allow_html=True)
