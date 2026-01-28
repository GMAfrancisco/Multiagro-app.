import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os

# 1. SETUP DE PÁGINA
st.set_page_config(page_title="Grupo Multiagro | AgTech", layout="wide")

# 2. FUNCIÓN ODOO (Sincronización de productos)
def get_odoo_prods():
    try:
        url = st.secrets["ODOO_URL"]
        db = st.secrets["ODOO_DB"]
        user = st.secrets["ODOO_USER"]
        key = st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 4})
            res = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price']})
            return res
    except:
        return None

# 3. ESTILOS CSS (Contraste y Diseño Móvil)
st.markdown("""
    <style>
    .stApp {background-color: #F0F2F0;}
    
    /* Títulos y etiquetas en NEGRO */
    h1, h2, h3, h4, p, label, .stMarkdown, div[data-testid="stRadio"] label {
        color: #1A1A1A !important;
        font-weight: 600 !important;
    }

    /* TARJETA DE DIAGNÓSTICO */
    .main-card {
        background: white; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 10px solid #1B5E20; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }

    /* ÁREA DE CARGA: Fondo oscuro y letras BLANCAS */
    [data-testid="stFileUploadDropzone"] {
        background-color: #333333 !important;
        border: 2px dashed #1B5E20 !important;
        border-radius: 15px;
    }
    [data-testid="stFileUploadDropzone"] div div span {
        color: white !important;
    }
    [data-testid="stFileUploadDropzone"] small {
        color: #cccccc !important;
    }

    /* ESlogan en cursiva verde */
    .eslogan {
        text-align: center;
        font-family: 'Georgia', serif;
        font-style: italic;
        color: #1B5E20 !important;
        font-size: 1.1rem;
        margin-top: -10px;
        margin-bottom: 25px;
    }

    /* Tarjetas de Producto */
    .product-card {
        background: #FFFFFF; 
        padding: 15px; 
        border-radius: 12px; 
        border: 2px solid #1B5E20; 
        text-align: center;
        margin-bottom: 10px;
    }
    .price-tag {
        color: #1B5E20 !important;
        font-size: 18px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 4. ENCABEZADO (Logo + Eslogan)
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"):
            st.image(f, use_container_width=True)
    st.markdown('<p class="eslogan">"Expertos en soluciones agrícolas"</p>', unsafe_allow_html=True)

# 5. BLOQUE 1: DIAGNÓSTICO (Letras Negras)
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.markdown("### 🔍 Diagnóstico de Cultivos")
metodo = st.radio("Seleccione método:", ["📂 Galería", "📸 Cámara"], horizontal=True)

if metodo == "📂 Galería":
    img = st.file_uploader("Subir imagen de la planta", type=['jpg', 'jpeg', 'png'])
else:
    img = st.camera_input("Capturar muestra")

if img:
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("IA analizando..."):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                prompt = "Analiza esta planta, identifica el problema y sugiere soluciones de Grupo Multiagro."
                res = model.generate_content([prompt, Image.open(img)])
                st.markdown("#### ✅ Resultado del Análisis")
                st.write(res.text)
            except:
                st.error("Error al conectar con la IA.")
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# 6. BLOQUE 2: SOLUCIONES MULTIAGRO (Odoo)
st.markdown("### 🛒 Soluciones Multiagro")
prods = get_odoo_prods()

if prods:
    cols = st.columns(len(prods))
    for i, p in enumerate(prods):
        with cols[i]:
            st.markdown(f"""
                <div class="product-card">
                    <span style="font-weight:bold;">{p['name']}</span><br>
                    <span class="price-tag">RD$ {p['list_price']:,.2f}</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"[💬 WhatsApp](https://wa.me/18095551234?text=Info:{p['name']})")
else:
    # Respaldo si no hay conexión
    c1, c2, c3, c4 = st.columns(4)
    for col, t in zip([c1,c2,c3,c4], ["Fungicidas", "Herbicidas", "Fertilizantes", "Bioestimulantes"]):
        col.info(f"**{t}**\n\nConsulte disponibilidad")

# 7. BLOQUE 3: LOGOS DE EMPRESAS (Pie de página)
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold; color:#333;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)

l_cols = st.columns(5)
l_ids = ["LogoMundoAgricola", "LogoMultisemillas", "LogoMultiriegos", "LogoFortius", "LogoAgroservicios"]

for i, lid in enumerate(l_ids):
    with l_cols[i]:
        for f in os.listdir("."):
            if f.lower().startswith(lid.lower()):
                try:
                    img_logo = Image.open(f)
                    # Forzamos altura uniforme de 60px para que no se apilen feo en movil
                    ratio = 60 / float(img_logo.size[1])
                    new_size = (int(img_logo.size[0] * ratio), 60)
                    st.image(img_logo.resize(new_size, Image.Resampling.LANCZOS))
                except: pass
                break

st.markdown("<p style='text-align:center; font-size:12px; color:#555; margin-top:20px;'>© 2026 GRUPO MULTIAGRO | República Dominicana</p>", unsafe_allow_html=True)
