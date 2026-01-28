import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse, os

# 1. SETUP
st.set_page_config(page_title="Multiagro App", layout="wide")
V_O, V_V = "#1B5E20", "#388E3C"

# 2. IA
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except: st.error("⚠️ Error API Key")

# 3. UI STYLE
st.markdown(f"<style>.stApp{{background:#F8FAF8}}.card{{background:white;padding:20px;border-radius:15px;border-top:8px solid {V_O};box-shadow:0 4px 10px rgba(0,0,0,0.05)}}</style>", unsafe_allow_html=True)

# 4. HEADER
c1, c2, c3 = st.columns([1,2,1])
with c2:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"): st.image(f, width=280)

st.markdown(f"<h1 style='text-align:center;color:{V_O}'>Multiagro AgTech</h1>", unsafe_allow_html=True)

# 5. DIAGNÓSTICO
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🔍 Diagnóstico con IA")
    col1, col2 = st.columns(2)
    cultivo = col1.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
    opcion = col2.radio("Entrada:", ["Galería", "Cámara"], horizontal=True)
    
    img = st.camera_input("Capturar") if opcion == "Cámara" else st.file_uploader("Subir", type=['jpg','png','jpeg'])
    
    if img and st.button("🚀 ANALIZAR"):
        with st.spinner("Procesando..."):
            try:
                res = model.generate_content([f"Experto RD: analiza {cultivo} e identifica plagas", Image.open(img)])
                st.success("✅ Listo"); st.write(res.text)
            except Exception as e: st.error(f"Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# 6. PRODUCTOS
st.markdown(f"<h3 style='color:{V_O};margin-top:20px'>🛒 Catálogo</h3>", unsafe_allow_html=True)
itms = [{"n":"Fungicida Elite","p":"RD$2,800"},{"n":"Bio-Estimulante","p":"RD$3,450"},{"n":"Herbicida Total","p":"RD$1,200"},{"n":"Potasio Soluble","p":"RD$1,950"}]
cols = st.columns(4)
for i in range(4):
    with cols[i]:
        st.info(f"**{itms[i]['n']}**\n\n{itms[i]['p']}")
        url = f"https://wa.me/18095551234?text=Interes en {itms[i]['n']}"
        st.markdown(f"[💬 WhatsApp]({url})")

# 7. LOGOS (UNIFORMES)
st.divider()
st.markdown("<p style='text-align:center;color:gray;font-weight:bold'>NUESTRAS EMPRESAS</p>", unsafe_allow_html=True)
l_ids = ["LogoMundoAgricola", "LogoMultisemillas", "LogoMultiriegos", "LogoFortius", "LogoAgroservicios"]
l_cols = st.columns(5)
for i in range(5):
    with l_cols[i]:
        found = False
        for f in os.listdir("."):
            if f.lower().startswith(l_ids[i].lower()):
                im = Image.open(f)
                ratio = 80 / float(im.size[1])
                st.image(im.resize((int(im.size[0]*ratio), 80), Image.Resampling.LANCZOS))
                found = True; break
        if not found: st.caption(f"📍 {l_ids[i]}")

st.markdown("<p style='text-align:center;font-size:12px;color:#aaa'>© 2026 GRUPO MULTIAGRO</p>", unsafe_allow_html=True)
