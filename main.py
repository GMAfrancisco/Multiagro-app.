import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Multiagro App", page_icon="🌱", layout="wide")

V_OSCURO = "#1B5E20"
V_VIVO = "#388E3C"

# --- 2. IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except:
    st.error("⚠️ Error en API Key.")

# --- 3. CSS PARA UNIFORMIDAD TOTAL ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #F8FAF8; }}
    .main-card {{ 
        background: white; padding: 25px; border-radius: 15px; 
        border-top: 8px solid {V_OSCURO}; box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
    }}
    /* ESTO FUERZA LA UNIFORMIDAD DE LOS LOGOS */
    .logo-block {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px; /* Altura idéntica para todos */
        background-color: white;
        border-radius: 8px;
        padding: 10px;
    }}
    img {{
        max-height: 80px; /* Ningún logo pasará de aquí */
        width: auto;
        object-fit: contain;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. CABECERA ---
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"):
            st.image(f, width=300)

st.markdown(f"<h1 style='text-align:center; color:{V_OSCURO};'>Consultor AgTech Multiagro</h1>", unsafe_allow_html=True)

# --- 5. DIAGNÓSTICO ---
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
                prompt = f"Agrónomo RD: analiza este cultivo de {cultivo} e identifica problemas."
                res = model.generate_content([prompt, pil_img])
                st.success("✅ Diagnóstico listo")
                st.write(res.text)
            except Exception as e:
                st.error(f"Error: {e}")
st.markdown("</div>", unsafe_allow_html=True)

# --- 6. PRODUCTOS ---
st.markdown(f"<h3 style='margin-top:30px; color:{V_OSCURO};'>🛒 Catálogo</h3>", unsafe_allow_html=True)
items = [
    {"n": "Fungicida Elite", "p": "RD$ 2,800"},
    {"n": "Bio-Estimulante", "p": "RD$ 3,450"},
    {"n": "Herbicida Total", "p": "RD$ 1,200"},
    {"n": "Potasio Soluble", "p": "RD$ 1,950"}
]
p_cols = st.columns(4)
for i in range(4):
    with p_cols[i]:
        st.info(f"**{items[i]['n']}**\n\n{items[i]['p']}")
        st.markdown(f"[💬 WhatsApp](https://wa.me/18095551234?text=Interes en {items[i]['n']})")

# --- 7. LOGOS EMPRESAS (VERSION ESTRICTA) ---
st.divider()
st.markdown("<p style='text-align:center; color:gray; font-weight:bold;'>NUESTRAS EMPRESAS</p>", unsafe_allow_html=True)

logos_id = ["LogoMundoAgricola", "LogoMultisemillas", "LogoMultiriegos", "LogoFortius", "LogoAgroservicios"]
l_cols = st.columns(5)

for i in range(5):
    with l_cols[i]:
        # Buscamos el archivo real
        encontrado = False
        for f in os.listdir("."):
            if f.lower().startswith(logos_id[i].lower()):
                # Forzamos altura fija de 80 píxeles para todos
                st.image(f, height=80)
                encontrado = True
                break
        if not encontrado:
            st.caption(f"📍 {logos_id[i]}")

st.markdown("<p style='text-align:center; font-size:12px; color:#aaa; margin-top:50px;'>© 2026 GRUPO MULTIAGRO</p>", unsafe_allow_html=True)
