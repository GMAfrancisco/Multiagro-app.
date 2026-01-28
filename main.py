import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse, os

# 1. SETUP E IA
st.set_page_config(page_title="Multiagro App", layout="wide")
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except: st.error("⚠️ Error de conexión")

# 2. UI STYLE
st.markdown("<style>.stApp{background:#F8FAF8} .card{background:white;padding:20px;border-radius:15px;border-top:8px solid #1B5E20;box-shadow:0 4px 10px rgba(0,0,0,0.05)}</style>", unsafe_allow_html=True)

# 3. HEADER (Logo Centrado y Grande)
_, col_mid, _ = st.columns([1, 2, 1])
with col_mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"):
            st.image(f, use_container_width=True)

st.markdown("<h1 style='text-align:center;color:#1B5E20;margin-top:-20px;'>Diagnóstico Inteligente de Cultivos</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>Tecnología AgTech de precisión</p>", unsafe_allow_html=True)

# 4. DIAGNÓSTICO
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    cult = c1.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
    opc = c2.radio("Entrada:", ["Galería", "Cámara"], horizontal=True)
    img = st.camera_input("Capturar") if opc == "Cámara" else st.file_uploader("Subir", type=['jpg','png','jpeg'])
    
    if img and st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("Analizando..."):
            try:
                prmt = f"Experto RD: analiza este {cult}, identifica plagas y sugiere manejo."
                res = model.generate_content([prmt, Image.open(img)])
                st.success("✅ Diagnóstico listo"); st.write
