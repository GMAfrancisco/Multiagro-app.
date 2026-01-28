import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Multiagro App", page_icon="🌱", layout="wide")

# Colores Corporativos
V_OSCURO = "#1B5E20"
V_VIVO = "#388E3C"

# --- 2. CONFIGURACIÓN IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except Exception as e:
    st.error("⚠️ Error en API Key. Verifique los Secrets.")

# --- 3. ESTILOS CSS (Ajustados para uniformidad) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAF8; }
    .main-card { background: white; padding: 25px; border-radius: 15px; border-top: 8px solid #1B5E20; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .prod-card { background: white; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #eee; min-height: 110px; }
    /* Estilo para forzar uniformidad en logos inferiores */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 80px;  /* Altura fija para todos los logos */
        margin-bottom: 10px;
    }
    .logo-container img {
        max-height: 80px;
        max-width: 100%;
        object-fit: contain;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNCIÓN PARA CARGAR IMÁGENES (Con altura fija) ---
def mostrar_logo_uniforme(nombre_sin_ext, es_footer=True):
    archivos = os.listdir(".")
    for f in archivos:
        if f.lower().startswith(nombre_sin_ext.lower()):
            try:
                if es_footer:
                    # Usamos HTML para forzar el tamaño uniforme en el pie de página
                    path = f"./{f}"
                    st.markdown(f'<div class="logo-container"><img src="app/static/{f}"></div>', unsafe_allow_html=True)
                    # Nota: Si el path static falla, usamos el método estándar de Streamlit con height
                    st.image(f, height=70) 
                else:
                    st.image(f, width=280)
                return True
            except:
                continue
    st.info(f"📍 {nombre_sin_ext}")
    return False

# --- 5. CABECERA ---
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    # Para el logo principal no forzamos altura tan pequeña
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"):
            st.image(f, width=300)

st.markdown(f"<h1 style='text-align:center; color:{V_OSCURO};'>Consultor AgTech Multiagro</h1>", unsafe_allow_html=True)

# --- 6. DIAGNÓSTICO IA ---
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.subheader("🔍 Diagnóstico de Cultivos")
col_a, col_b = st.columns(2)
with col_a:
    cultivo = st.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
with col_b:
    opcion = st.radio("Entrada:", ["Subir Foto", "Cámara"], horizontal=True)

img_input = None
if opcion == "Cámara":
    img_input = st.camera_input("Capturar")
else:
    img_input = st.file_uploader("Galería", type=['jpg', 'png', 'jpeg'])

if img_input:
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Analizando..."):
            try:
                pil_img = Image.open(img_input)
                prompt = f"Como agrónomo en RD, analiza este {cultivo} e identifica plagas."
                res = model.generate_content([prompt, pil_img])
                st.success("✅ Diagnóstico listo")
                st.write(res.text)
            except Exception as e:
                st.error(f"Error: {e}")
st.markdown("</div>", unsafe_allow_html=True)

# --- 7. CATÁLOGO ---
st.markdown(f"<h3 style='color:{V_OSCURO}; margin-top:30px;'>🛒 Productos Destacados</h3>", unsafe_allow_html=True)
items = [
    {"n": "Fungicida Elite", "p": "RD$ 2,800"},
    {"n": "Bio-Estimulante", "p": "RD$ 3,450"},
    {"n": "Herbicida Total", "p": "RD$ 1,200"},
    {"n": "Potasio Soluble", "p": "RD$ 1,950"}
]
p_cols = st.columns(4)
for i in range(4):
    with p_cols[i]:
        st.markdown(f"<div class='prod-card'><b>{items[i]['n']}</b><br><span style='color:{V_VIVO}'>{items[i]['p']}</span></div>", unsafe_allow_html=True)
        link = f"https://wa.me/18095551234?text=Interes en {items[i]['n']}"
        st.markdown(f"[💬 WhatsApp]({link})")

# --- 8. LOGOS EMPRESAS (Altura Uniforme) ---
st.divider()
st.markdown("<p style='text-align:center; color:gray; font
