import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse
import base64

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO DASHBOARD
st.set_page_config(page_title="Multiagro AgTech", layout="wide")

# ESTILO CSS AVANZADO (LÍNEA GRÁFICA MODERNA)
st.markdown("""
    <style>
    /* Fondo principal */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Tarjetas de Productos */
    .product-card {
        background-color: #1E1E26;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #3E3E4A;
        text-align: center;
        transition: transform 0.3s;
        margin-bottom: 20px;
    }
    .product-card:hover {
        transform: translateY(-5px);
        border-color: #007BFF;
    }
    
    /* Imágenes de productos */
    .product-img { 
        width: 100%; 
        height: 160px; 
        object-fit: contain; 
        background-color: white; 
        border-radius: 10px; 
        margin-bottom: 15px; 
    }
    
    /* Diagnóstico Box */
    .diag-box {
        background: rgba(255, 255, 255, 0.05);
        border-left: 5px solid #007BFF;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    
    /* Contenedor de logos */
    .logo-container { 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        height: 70px; 
        background: white;
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Botones personalizados */
    div.stButton > button {
        border-radius: 20px;
        font-weight: bold;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIO DE LÓGICA DE NEGOCIO (IGUAL A LA ANTERIOR) ---

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state: st.session_state.prods_filtrados = []

def get_odoo_prods():
    try:
        url, db = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"]
        user, key = st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 60})
            res = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price', 'image_128']})
            return res
    except: return None

# ... (Mantener funciones de registro y email intactas) ...

# 2. ENCABEZADO
st.markdown("<h1 style='text-align: center; color: #007BFF;'>GRUPO MULTIAGRO</h1>", unsafe_allow_html=True)
todos_los_prods = get_odoo_prods()

# 3. SECCIÓN: DIAGNÓSTICO EXPERTO
st.markdown("## 🔍 Diagnóstico Experto")
cultivo_info = st.text_input("¿Qué cultivo o planta estamos analizando?", placeholder="Ej: Tomate, Arroz...")

tab_gal, tab_cam = st.tabs(["📁 Galería", "📸 Cámara"])
with tab_gal: img_gal = st.file_uploader("Subir imagen", type=['png', 'jpg', 'jpeg'], key="uploader_gal")
with tab_cam: img_cam = st.camera_input("Tomar foto")

img = img_cam if img_cam else img_gal

if img is not None:
    if st.button("🚀 INICIAR ASESORÍA COMPLETA", use_container_width=True):
        with st.spinner("Analizando..."):
            try:
                nombres_inventario = [p['name'] for p in todos_los_prods] if todos_los_prods else []
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                
                prompt = f"RESPONDE 100% ESPAÑOL. Eres experto de Multiagro. Analiza el cultivo de {cultivo_info}. Identifica plaga/hongo con certeza, recomienda 4 productos de {nombres_inventario} en NEGRITAS, advierte leer etiquetas del fabricante para dosis, indica labores culturales y haz 2 preguntas."
                
                res = model.generate_content([prompt, Image.open(img)])
                st.session_state.chat_history = [{"role": "model", "parts": [res.text]}]
                
                # Filtrado de productos
                texto_ia_lower = res.text.lower()
                sugeridos, vistos = [], set()
                if todos_los_prods:
                    for p in todos_los_prods:
                        primera_palabra = p['name'].split()[0].lower()
                        if primera_palabra in texto_ia_lower and primera_palabra not in vistos and len(primera_palabra) > 3:
                            sugeridos.append(p)
                            vistos.add(primera_palabra)
                        if len(sugeridos) >= 4: break
                st.session_state.prods_filtrados = sugeridos
                st.rerun()
            except: st.error("Error en análisis.")

if st.session_state.chat_history:
    st.markdown(f"<div class='diag-box'>{st.session_state.chat_history[-1]['parts'][0]}</div>", unsafe_allow_html=True)

# 4. TIENDA DINÁMICA (DISEÑO DE TARJETAS)
st.divider()
st.markdown("### 🛒 Soluciones Sugeridas")
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else (todos_los_prods[:4] if todos_los_prods else [])

if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            img_html = ""
            if p.get('image_128'):
                img_html = f'<img src="data:image/png;base64,{p["image_128"]}" class="product-img">'
            
            st.markdown(f"""
                <div class="product-card">
                    {img_html}
                    <h4 style='font-size: 1rem;'>{p['name'].split('(')[0].strip()}</h4>
                    <p style='color: #007BFF; font-weight: bold;'>RD$ {p['list_price']:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            st.link_button("Cotizar WhatsApp", f"https://wa.me/18295624653?text=Info: {p['name']}", use_container_width=True)

# 5. REGISTRO Y 6. LOGOS (IGUAL A LA LÓGICA ANTERIOR)
# ... [Insertar aquí el bloque de registro de productor y logos que ya tienes] ...
