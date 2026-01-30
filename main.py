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

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Grupo Multiagro | AgTech", layout="wide")

st.markdown("""
    <style>
    .product-img { width: 100%; height: 180px; object-fit: contain; background-color: white; border-radius: 10px; padding: 5px; margin-bottom: 10px; }
    .logo-container { display: flex; justify-content: center; align-items: center; height: 80px; padding: 10px; }
    .logo-container img { max-height: 100%; max-width: 100%; object-fit: contain; }
    </style>
    """, unsafe_allow_html=True)

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state: st.session_state.prods_filtrados = []

# --- FUNCIONES DE INTEGRACIÓN ---
def get_odoo_prods():
    try:
        url, db = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"]
        user, key = st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 80})
            res = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price', 'image_128']})
            return res
    except: return None

todos_los_prods = get_odoo_prods()

# (Registro y Email omitidos para brevedad, mantener los mismos)

# 2. ENCABEZADO
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in sorted(os.listdir(".")):
        if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
            st.image(f, use_container_width=True)

# 3. SECCIÓN: DIAGNÓSTICO
st.markdown("### 🔍 Diagnóstico Experto")
img = None
tab_gal, tab_cam = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
with tab_gal: img_gal = st.file_uploader("Subir imagen", type=['png', 'jpg', 'jpeg'], key="uploader_gal")
with tab_cam: img_cam = st.camera_input("Tomar foto")

if img_cam: img = img_cam
elif img_gal: img = img_gal

if img is not None:
    if st.button("🚀 INICIAR ANÁLISIS PROFUNDO", type="primary", use_container_width=True):
        with st.spinner("Analizando y buscando soluciones..."):
            try:
                nombres_inventario = [p['name'] for p in todos_los_prods] if todos_los_prods else []
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                
                # Instrucción para asegurar que la IA mencione los productos exactos
                prompt = f"""
                RESPONDE 100% EN ESPAÑOL.
                Eres el Agrónomo Principal de Multiagro.
                1. Identifica el problema de la imagen (plaga, hongo, carencia).
                2. De esta lista de Odoo: {nombres_inventario}, menciona los 4 más adecuados.
                3. Escribe los nombres de los productos recomendados exactamente como aparecen en la lista y en NEGRITAS (ej: **Nombre Producto**).
                4. Explica el plan de acción.
                """
                
                res = model.generate_content([prompt, Image.open(img)])
                texto_analisis = res.text
                
                # --- LÓGICA DE FILTRADO REFORZADA ---
                texto_ia_lower = texto_analisis.lower()
                sugeridos = []
                vistos = set()
                
                if todos_los_prods:
                    for p in todos_los_prods:
                        # Buscamos si el nombre del producto o sus primeras dos palabras están en el texto
                        nombre_limpio = p['name'].split('(')[0].strip().lower()
                        primera_palabra = nombre_limpio.split()[0]
                        
                        if (nombre_limpio in texto_ia_lower or primera_palabra in texto_ia_lower) and primera_palabra not in vistos:
                            if len(primera_palabra) > 3: # Evitar palabras cortas genéricas
                                sugeridos.append(p)
                                vistos.add(primera_palabra)
                        if len(sugeridos) >= 4: break
                
                # Guardar en sesión ANTES del rerun
                st.session_state.chat_history = [{"role": "model", "parts": [texto_analisis]}]
                st.session_state.prods_filtrados = sugeridos
                st.rerun()
                
            except Exception as e:
                st.error(f"Aviso: La IA respondió, pero hubo un detalle al filtrar productos.")

if st.session_state.chat_history:
    st.markdown("---")
    st.info(st.session_state.chat_history[-1]["parts"][0])
    # ... (Chat input omitido para brevedad)

# 4. TIENDA DINÁMICA
st.divider()
st.markdown("### 🛒 Soluciones Recomendadas")
# Si hay productos filtrados, los mostramos. Si no, mostramos los destacados.
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else (todos_los_prods[:4] if todos_los_prods else [])

if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            if p.get('image_128'):
                st.markdown(f'<img src="data:image/png;base64,{p["image_128"]}" class="product-img">', unsafe_allow_html=True)
            else:
                st.image("https://cdn-icons-png.flaticon.com/512/1054/1054800.png", width=150)
            
            nombre_p = p['name'].split('(')[0].strip()
            st.markdown(f"**{nombre_p}**")
            st.write(f"RD$ {p['list_price']:,.2f}")
            link_p = f"https://wa.me/18295624653?text={urllib.parse.quote('Deseo cotizar: ' + p['name'])}"
            st.link_button("🛒 Cotizar", link_p, use_container_width=True)

# ... (Botón Técnico, Registro y Logos se mantienen igual)
# 6. LOGOS FINALES (CORRECCIÓN DE PROPORCIÓN)
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold; color:#555;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)
l_cols = st.columns(5)
logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
for i, l in enumerate(logos):
    with l_cols[i]:
        if os.path.exists(l):
            with open(l, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{b64}"></div>', unsafe_allow_html=True)
