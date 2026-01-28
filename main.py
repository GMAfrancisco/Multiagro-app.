import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse, os, time

# 1. SETUP PROFESIONAL
st.set_page_config(page_title="Multiagro App", layout="wide")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Cambiamos a flash-lite temporalmente: tiene cuotas más altas en Tier 1
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except:
    st.error("⚠️ Error de API")

# 2. ESTILO
st.markdown("<style>.stApp{background:#F8FAF8} .card{background:white;padding:25px;border-radius:15px;border-top:8px solid #1B5E20;box-shadow:0 4px 10px rgba(0,0,0,0.05)}</style>", unsafe_allow_html=True)

# 3. HEADER
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)

st.markdown("<h1 style='text-align:center;color:#1B5E20;margin-top:-20px;'>Diagnóstico Inteligente</h1>", unsafe_allow_html=True)

# 4. DIAGNÓSTICO CON REINTENTOS (Solución al error 429)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    cult = c1.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
    opc = c2.radio("Entrada:", ["Galería", "Cámara"], horizontal=True)
    img = st.camera_input("Foto") if opc == "Cámara" else st.file_uploader("Imagen", type=['jpg','png','jpeg'])
    
    if img and st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("Procesando muestra..."):
            intentos = 0
            max_intentos = 3
            exito = False
            
            while intentos < max_intentos and not exito:
                try:
                    prmt = f"Agrónomo RD: analiza este {cult}, identifica plagas y sugiere manejo técnico."
                    res = model.generate_content([prmt, Image.open(img)])
                    st.success("✅ Diagnóstico Completado")
                    st.write(res.text)
                    exito = True
                except Exception as e:
                    intentos += 1
                    if "429" in str(e) or "ResourceExhausted" in str(e):
                        if intentos < max_intentos:
                            st.warning(f"Línea ocupada. Reintentando automáticamente en {intentos * 4} segundos...")
                            time.sleep(intentos * 4) # Espera progresiva
                        else:
                            st.error("Límite de Google alcanzado. Por favor, espere 1 minuto e intente de nuevo.")
                    else:
                        st.error(f"Error inesperado: {e}")
                        break
    st.markdown("</div>", unsafe_allow_html=True)

# 5. PRODUCTOS Y LOGOS
st.markdown("<h3 style='color:#1B5E20;margin-top:25px'>🛒 Soluciones Multiagro</h3>", unsafe_allow_html=True)
nom, pre = ["Fungicida Elite", "Bio-Estimulante", "Herbicida Total", "Potasio Soluble"], ["RD$ 2,800", "RD$ 3,450", "RD$ 1,200", "RD$ 1,950"]
cols = st.columns(4)
for i in range(4):
    with cols[i]:
        st.info(f"**{nom[i]}**\n{pre[i]}")
        st.markdown(f"[💬 WhatsApp](https://wa.me/18095551234?text=Interes:{nom[i]})")

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
