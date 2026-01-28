import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse, os

# 1. SETUP E IA
st.set_page_config(page_title="Multiagro App", layout="wide")
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except: st.error("⚠️ Error API")

# 2. ESTILOS
st.markdown("<style>.stApp{background:#F8FAF8} .card{background:white;padding:20px;border-radius:15px;border-top:8px solid #1B5E20;box-shadow:0 4px 10px rgba(0,0,0,0.05)}</style>", unsafe_allow_html=True)

# 3. HEADER (Logo Centrado y Grande)
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)

st.markdown("<h1 style='text-align:center;color:#1B5E20;margin-top:-20px;'>Diagnóstico Inteligente de Cultivos</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>Tecnología AgTech para el campo dominicano</p>", unsafe_allow_html=True)

# 4. DIAGNÓSTICO
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    cult = c1.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
    opc = c2.radio("Entrada:", ["Galería", "Cámara"], horizontal=True)
    img = st.camera_input("Captura") if opc == "Cámara" else st.file_uploader("Foto", type=['jpg','png','jpeg'])
    
    if img and st.button("🚀 INICIAR ESCANEO"):
        with st.spinner("Analizando..."):
            try:
                res = model.generate_content([f"Agrónomo RD: analiza {cult}, identifica plagas y sugiere manejo técnico.", Image.open(img)])
                st.success("✅ Completado"); st.write(res.text)
            except Exception as e: st.error(f"Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# 5. PRODUCTOS
st.markdown("<h3 style='color:#1B5E20;margin-top:20px'>🛒 Soluciones</h3>", unsafe_allow_html=True)
itms = [{"n":"Fungicida Elite","p":"RD$2,800"},{"n":"Bio-Estimulante","p":"RD$3,450"},{"n":"Herbicida Total","p":"RD$1,200"},{"n":"Potasio Soluble","p":"RD$1,950"}]
cols = st.columns(4)
for i in range(4):
    with cols[i]:
        st.info(f"**{itms[i]['n']}**\n\n{itms[i]['p
