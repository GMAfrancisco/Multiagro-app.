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

# --- 3. ESTILOS CSS (Versión simplificada para evitar errores) ---
st.markdown("<style>.main-card { background: white; padding: 20px; border-radius: 15px; border-top: 5px solid #1B5E20; box-shadow: 0 4px 10px rgba(0,0,0,0.05); } .prod-card { background: #f9f9f9; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #eee; }</style>", unsafe_allow_html=True)

# --- 4. FUNCIÓN PARA CARGAR IMÁGENES ---
def mostrar_imagen_segura(nombre_sin_ext, ancho=None):
    archivos = os.listdir(".")
    encontrado = False
    for f in archivos:
        if f.lower().startswith(nombre_sin_ext.lower()):
            try:
                img = Image.open(f)
                if ancho:
                    st.image(img, width=ancho)
                else:
                    st.image(img, use_container_width=True)
                encontrado = True
                break
            except:
                continue
    if not encontrado:
        st.info(f"📍 {nombre_sin_ext}")

# --- 5. CABECERA ---
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    mostrar_imagen_segura("Grupo_Multiagro", ancho=280)

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
st.markdown(f"<h3 style='color:{V_OSCURO};'>🛒 Productos</h3>", unsafe_allow_html=True)
items = [
    {"n": "Fungicida Elite", "p": "RD$ 2,800"},
    {"n": "Bio-Estimulante", "p": "RD$ 3,450"},
    {"n": "Herbicida Total", "p": "RD$ 1,200"},
    {"n": "Potasio Soluble", "p": "RD$ 1,950"}
]
p_cols = st.columns(4)
for i in range(4):
    with p_cols[i]:
        st.markdown(f"<div class='prod-card'><b>{items[i]['n']}</b><br>{items[i]['p']}</div>", unsafe_allow_html=True)
        link = f"https://wa.me/18095551234?text=Interes en {items[i]['n']}"
        st.markdown(f"[💬 WhatsApp]({link})")

# --- 8. LOGOS EMPRESAS ---
st.divider()
st.markdown("<p style='text-align:center; color:gray;'>NUESTRAS EMPRESAS</p>", unsafe_allow_html=True)
logos_id = ["LogoMundoAgricola", "LogoMultisemillas", "LogoMultiriegos", "LogoFortius", "LogoAgroservicios"]
l_cols = st.columns(5)
for i in range(5):
    with l_cols[i]:
        mostrar_imagen_segura(logos_id[i])

st.markdown("<p style='text-align:center; font-size:12px; color:#aaa; margin-top:50px;'>© 2026 GRUPO MULTIAGRO</p>", unsafe_allow_html=True)
