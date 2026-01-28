import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse, os

# 1. SETUP E IA (Optimizado para alta cuota)
st.set_page_config(page_title="Multiagro App", layout="wide")
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Usar flash-lite para maximizar la cantidad de consultas permitidas
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except: st.error("⚠️ Error de API")

# 2. UI STYLE
st.markdown("<style>.stApp{background:#F8FAF8} .card{background:white;padding:20px;border-radius:15px;border-top:8px solid #1B5E20;box-shadow:0 4px 10px rgba(0,0,0,0.05)}</style>", unsafe_allow_html=True)

# 3. HEADER
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)

st.markdown("<h1 style='text-align:center;color:#1B5E20;margin-top:-20px;'>Diagnóstico Inteligente de Cultivos</h1>", unsafe_allow_html=True)

# 4. DIAGNÓSTICO (Optimizado para no desperdiciar tokens)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    cult = c1.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
    opc = c2.radio("Entrada:", ["Galería", "Cámara"], horizontal=True)
    img = st.camera_input("Foto") if opc == "Cámara" else st.file_uploader("Imagen", type=['jpg','png','jpeg'])
    
    if img and st.button("🚀 ANALIZAR"):
        with st.spinner("Analizando..."):
            try:
                # Prompt corto para ahorrar cuota
                res = model.generate_content([f"Experto RD: diagnostica este {cult} y da solución.", Image.open(img)])
                st.success("✅ Diagnóstico listo"); st.write(res.text)
            except Exception as e:
                st.error("Límite de consultas alcanzado. Intente en unos minutos.")
    st.markdown("</div>", unsafe_allow_html=True)

# 5. PRODUCTOS
st.markdown("<h3 style='color:#1B5E20;margin-top:25px'>🛒 Soluciones</h3>", unsafe_allow_html=True)
nom, pre = ["Fungicida Elite", "Bio-Estimulante", "Herbicida Total", "Potasio Soluble"], ["RD$ 2,800", "RD$ 3,450", "RD$ 1,200", "RD$ 1,950"]
cols = st.columns(4)
for i in range(4):
    with cols[i]:
        st.info(f"**{nom[i]}**\n\n{pre[i]}")
        st.markdown(f"[💬 WhatsApp](https://wa.me/18095551234?text=Interes:{nom[i]})")

# 6. LOGOS
st.divider()
l_ids = ["LogoMundoAgricola", "LogoMultisemillas", "LogoMultiriegos", "LogoFortius", "LogoAgroservicios"]
l_cols = st.columns(5)
for i, l_id in enumerate(l_ids):
    with l_cols[i]:
        for f in os.listdir("."):
            if f.lower().startswith(l_id.lower()):
                im = Image.open(f)
                rat = 80 / float(im.size[1])
                st.image(im.resize((int(im.size[0]*rat), 80), Image.Resampling.LANCZOS))
                break

st.markdown("<p style='text-align:center;font-size:12px;color:#aaa;margin-top:30px;'>© 2026 GRUPO MULTIAGRO</p>", unsafe_allow_html=True)
