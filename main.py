import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os

# 1. CONFIGURACION DE PAGINA
st.set_page_config(page_title="Grupo Multiagro | Consultor AgTech", layout="wide")

# 2. FUNCION ODOO
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

# 3. ESTILOS CSS AVANZADOS (CONTRASTE Y MOVIL)
st.markdown("""
    <style>
    /* Fondo general */
    .stApp {background-color: #F0F2F0;}
    
    /* Forzar color de texto para legibilidad */
    h1, h2, h3, p, span, label {
        color: #1A1A1A !important;
    }
    
    /* Tarjeta de Diagnóstico */
    .main-card {
        background: white; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 10px solid #1B5E20; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Eslogan en cursiva con mejor contraste */
    .eslogan {
        text-align: center;
        font-family: 'Georgia', serif;
        font-style: italic;
        color: #1B5E20 !important;
        font-size: 1.1rem;
        margin-top: -10px;
        padding-bottom: 20px;
    }

    /* Tarjetas de Producto optimizadas */
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
        font-size: 20px;
        font-weight: bold;
        display: block;
    }
    
    /* Ajuste para que los logos no se vean gigantes en movil */
    img {
        max-width: 100%;
        height: auto;
    }
    </style>
""", unsafe_allow_html=True)

# 4. ENCABEZADO
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"):
            st.image(f, use_container_width=True)
    st.markdown('<p class="eslogan">"Expertos en soluciones agrícolas"</p>', unsafe_allow_html=True)

# 5. BLOQUE 1: DIAGNOSTICO DE CULTIVOS
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.markdown("<h3 style='margin-top:0;'>🔍 Diagnóstico de Cultivos</h3>", unsafe_allow_html=True)
metodo = st.radio("Seleccione método:", ["📂 Galería", "📸 Cámara"], horizontal=True)

if metodo == "📂 Galería":
    img = st.file_uploader("Subir imagen de la planta", type=['jpg', 'jpeg', 'png'])
else:
    img = st.camera_input("Capturar muestra")

if img:
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Analizando con IA..."):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                prompt = "Analiza esta planta, identifica plagas y sugiere productos de Soluciones Multiagro."
                res = model.generate_content([prompt, Image.open(img)])
                st.markdown("#### ✅ Resultado del Análisis")
                st.write(res.text)
            except:
                st.error("Error al procesar la imagen.")
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# 6. BLOQUE 2: SOLUCIONES MULTIAGRO
st.markdown("### 🛒 Soluciones Multiagro")
prods = get_odoo_prods()

if prods:
    # En movil, st.columns se apilan. Usamos un contenedor con diseño limpio.
    for p in prods:
        st.markdown(f"""
            <div class="product-card">
                <span style="font-weight:bold; font-size:16px;">{p['name']}</span><br>
                <span class="price-tag">RD$ {p['list_price']:,.2f}</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"[💬 Cotizar por WhatsApp](https://wa.me/18095551234?text=Me%20interesa%20{p['name']})")
        st.write("---")
else:
    st.info("Sincronizando productos real-time...")

# 7. BLOQUE 3: LOGOS DE EMPRESAS (Pie de Página con Columnas Ajustadas)
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)

# Para evitar que se apilen uno encima de otro de forma fea, usamos columnas más pequeñas
l_cols = st.columns(5)
l_ids = ["LogoMundoAgricola", "LogoMultisemillas", "LogoMultiriegos", "LogoFortius", "LogoAgroservicios"]

for i, lid in enumerate(l_ids):
    with l_cols[i % 5]: # Distribuye en 5 columnas
        for f in os.listdir("."):
            if f.lower().startswith(lid.lower()):
                try:
                    img_l = Image.open(f)
                    # Forzamos un tamaño más pequeño para que quepan mejor en fila
                    img_l.thumbnail((150, 60)) 
                    st.image(img_l)
                except: pass
                break

st.markdown("<p style='text-align:center; font-size:12px; color:#555; margin-top:20px;'>© 2026 GRUPO MULTIAGRO | República Dominicana</p>", unsafe_allow_html=True)
