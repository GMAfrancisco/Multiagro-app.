import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse, os

# 1. CONFIGURACIÓN E IA
st.set_page_config(page_title="Multiagro App", layout="wide")
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except: st.error("⚠️ Error de conexión con IA")

# 2. ESTILOS VISUALES
st.markdown("<style>.stApp{background:#F8FAF8} .card{background:white;padding:20px;border-radius:15px;border-top:8px solid #1B5E20;box-shadow:0 4px 10px rgba(0,0,0,0.05)}</style>", unsafe_allow_html=True)

# 3. HEADER (Logo Centrado y Grande)
_, col_mid, _ = st.columns([1, 2, 1])
with col_mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"):
            st.image(f, use_container_width=True)

st.markdown("<h1 style='text-align:center;color:#1B5E20;margin-top:-20px;'>Diagnóstico Inteligente de Cultivos</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>Tecnología AgTech para el campo dominicano</p>", unsafe_allow_html=True)

# 4. MÓDULO DE DIAGNÓSTICO
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    cultivo = c1.selectbox("Tipo de Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
    opcion = c2.radio("Captura:", ["Galería", "Cámara"], horizontal=True)
    
    img = st.camera_input("Capturar") if opcion == "Cámara" else st.file_uploader("Subir", type=['jpg','png','jpeg'])
    
    if img and st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("La IA está analizando la muestra..."):
            try:
                # Prompt optimizado para República Dominicana
                prmt = f"Experto Agrónomo RD: analiza este cultivo de {cultivo}, identifica plagas y sugiere manejo técnico."
                res = model.generate_content([prmt, Image.open(img)])
                st.success("✅ Diagnóstico Completado")
                st.write(res.text)
            except: st.error("Error en el escaneo")
    st.markdown("</div>", unsafe_allow_html=True)

# 5. CATÁLOGO DE PRODUCTOS
st.markdown("<h3 style='color:#1B5E20;margin-top:25px'>🛒 Soluciones Recomendadas</h3>", unsafe_allow_html=True)
prods = [("Fungicida Elite", "RD$2,800"), ("Bio-Estimulante", "RD$3,450"), ("Herbicida Total", "RD$1,200"), ("Potasio Soluble", "RD$1,950")]
p_cols = st.columns(4)
for i, (nombre, precio) in enumerate(prods):
    with p_cols[i]:
        st.info(f"**{nombre}**\n\n{precio}")
        txt_wa = urllib.parse.quote(f"Hola Multiagro, me interesa: {nombre}")
        st.markdown(f"[💬 WhatsApp](https://wa.me/18095551234?text={txt_wa})")

# 6. LOGOS EMPRESAS (Altura Uniforme 80px)
st.divider()
st.markdown("<p style='text-align:center;color:gray;font-weight:bold'>NUESTRAS EMPRESAS</p>", unsafe_allow_html=True)
l_ids = ["LogoMundoAgricola", "LogoMultisemillas", "LogoMultiriegos", "LogoFortius", "LogoAgroservicios"]
l_cols = st.columns(5)
for i, l_id in enumerate(l_ids):
    with l_cols[i]:
        for f in os.listdir("."):
            if f.lower().startswith(l_id.lower()):
                im = Image.open(f)
                ratio = 80 / float(im.size[1])
                st.image(im.resize((int(im.size[0]*ratio), 80), Image.Resampling.LANCZOS))
                break

st.markdown("<p style='text-align:center;font-size:12px;color:#aaa;margin-top:30px;'>© 2026 GRUPO MULTIAGRO | República Dominicana</p>", unsafe_allow_html=True)
