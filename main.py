import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse, os

# 1. SETUP - Ahora con el modelo Flash completo (más inteligente)
st.set_page_config(page_title="Multiagro App", layout="wide")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Al ser de pago, usamos 'gemini-2.0-flash' para diagnósticos más profundos
    model = genai.GenerativeModel('models/gemini-2.0-flash')
except:
    st.error("⚠️ Error de conexión con la llave de API")

# 2. ESTILO
st.markdown("<style>.stApp{background:#F8FAF8} .card{background:white;padding:25px;border-radius:15px;border-top:8px solid #1B5E20;box-shadow:0 4px 10px rgba(0,0,0,0.05)}</style>", unsafe_allow_html=True)

# 3. HEADER
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)

st.markdown("<h1 style='text-align:center;color:#1B5E20;margin-top:-20px;'>Diagnóstico Inteligente Profesional</h1>", unsafe_allow_html=True)

# 4. DIAGNÓSTICO
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    cult = c1.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
    opc = c2.radio("Entrada:", ["Galería", "Cámara"], horizontal=True)
    img = st.camera_input("Foto") if opc == "Cámara" else st.file_uploader("Imagen", type=['jpg','png','jpeg'])
    
    if img and st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("Consultando base de datos agrícola..."):
            try:
                # Prompt más robusto ya que tenemos más capacidad de procesamiento
                prompt = f"Actúa como un agrónomo experto en República Dominicana. Analiza este cultivo de {cult}, identifica plagas o enfermedades con precisión y recomienda productos de Grupo Multiagro."
                res = model.generate_content([prompt, Image.open(img)])
                st.success("✅ Análisis Profesional Completado")
                st.write(res.text)
            except Exception as e:
                st.error(f"Error técnico: {e}. Verifique su cuenta de facturación en Google AI Studio.")
    st.markdown("</div>", unsafe_allow_html=True)

# 5. PRODUCTOS Y LOGOS (Siguen iguales para mantener la marca)
st.markdown("<h3 style='color:#1B5E20;margin-top:25px'>🛒 Soluciones Disponibles</h3>", unsafe_allow_html=True)
nom, pre = ["Fungicida Elite", "Bio-Estimulante", "Herbicida Total", "Potasio Soluble"], ["RD$ 2,800", "RD$ 3,450", "RD$ 1,200", "RD$ 1,950"]
cols = st.columns(4)
for i in range(4):
    with cols[i]:
        st.info(f"**{nom[i]}**\n{pre[i]}")
        st.markdown(f"[💬 WhatsApp](https://wa.me/18095551234?text=Consulta:{nom[i]})")

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

st.markdown("<p style='text-align:center;font-size:12px;color:#aaa;'>© 2026 GRUPO MULTIAGRO</p>", unsafe_allow_html=True)
