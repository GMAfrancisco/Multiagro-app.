import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse, os, time

# 1. SETUP PROFESIONAL - TIER 1
st.set_page_config(page_title="Multiagro App", layout="wide")

try:
    # Usamos la llave que ya tienes vinculada al nivel de pago
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # El modelo 2.0 Flash es el ideal para cuentas con facturación activa
    model = genai.GenerativeModel('models/gemini-2.0-flash')
except:
    st.error("⚠️ Error de configuración. Verifique sus Secrets.")

# 2. ESTILO CORPORATIVO
st.markdown("<style>.stApp{background:#F8FAF8} .card{background:white;padding:25px;border-radius:15px;border-top:8px solid #1B5E20;box-shadow:0 4px 10px rgba(0,0,0,0.05)}</style>", unsafe_allow_html=True)

# 3. HEADER
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)

st.markdown("<h1 style='text-align:center;color:#1B5E20;margin-top:-20px;'>Diagnóstico Inteligente Profesional</h1>", unsafe_allow_html=True)

# 4. DIAGNÓSTICO CON MANEJO DE CUOTA TIER 1
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    cult = c1.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
    opc = c2.radio("Entrada:", ["Galería", "Cámara"], horizontal=True)
    img = st.camera_input("Foto") if opc == "Cámara" else st.file_uploader("Imagen", type=['jpg','png','jpeg'])
    
    if img and st.button("🚀 INICIAR ANÁLISIS PROFESIONAL"):
        with st.spinner("Procesando con prioridad de pago..."):
            # Pequeña pausa de seguridad para no saturar el Tier 1
            time.sleep(1) 
            try:
                # Prompt de alta precisión para fitopatología
                prompt = f"Actúa como agrónomo experto de República Dominicana. Analiza este {cult}, identifica plagas o deficiencias nutricionales y sugiere soluciones de Grupo Multiagro."
                res = model.generate_content([prompt, Image.open(img)])
                st.success("✅ Diagnóstico Tier 1 Completado")
                st.write(res.text)
            except Exception as e:
                if "429" in str(e):
                    st.warning("⚠️ El sistema está procesando muchas solicitudes. Reintentando automáticamente en 3 segundos...")
                    time.sleep(3)
                    # Reintento único
                    res = model.generate_content([prompt, Image.open(img)])
                    st.write(res.text)
                else:
                    st.error(f"Nota: Google está terminando de activar su Nivel 1. Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# 5. PRODUCTOS Y LOGOS
st.markdown("<h3 style='color:#1B5E20;margin-top:25px'>🛒 Soluciones de Grupo Multiagro</h3>", unsafe_allow_html=True)
nom, pre = ["Fungicida Elite", "Bio-Estimulante", "Herbicida Total", "Potasio Soluble"], ["RD$ 2,800", "RD$ 3,450", "RD$ 1,200", "RD$ 1,950"]
cols = st.columns(4)
for i in range(4):
    with cols[i]:
        st.info(f"**{nom[i]}**\n{pre[i]}")
        link = f"https://wa.me/18095551234?text=Consulta sobre {nom[i]}"
        st.markdown(f"[💬 WhatsApp]({link})")

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

st.markdown("<p style='text-align:center;font-size:12px;color:#aaa;'>© 2026 GRUPO MULTIAGRO | Servicio Técnico Profesional</p>", unsafe_allow_html=True)
