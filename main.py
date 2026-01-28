import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os, urllib.parse, time

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Multiagro AgTech", layout="wide")

# --- 2. FUNCIÓN DE CONEXIÓN ODOO (Depuración Activa) ---
def conectar_odoo():
    try:
        # Extraer datos de Secrets
        url = st.secrets["ODOO_URL"]
        db = st.secrets["ODOO_DB"]
        user = st.secrets["ODOO_USER"]
        key = st.secrets["ODOO_API_KEY"]
        
        # Intentar autenticación
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, user, key, {})
        
        if not uid:
            return "ERROR_AUTH", None
        
        # Intentar leer productos
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        ids = models.execute_kw(db, uid, key, 'product.template', 'search', 
                               [[['sale_ok', '=', True]]], {'limit': 4})
        
        prods = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price']})
        return "OK", [(p['name'], f"RD$ {p['list_price']:,.2f}") for p in prods]
    
    except Exception as e:
        return "ERROR_CONEXION", str(e)

# --- 3. CONFIGURACIÓN IA ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except:
    st.error("⚠️ Error en API Key de Gemini.")

# --- 4. DISEÑO Y CABECERA ---
st.markdown("<style>.stApp{background:#F8FAF8} .card{background:white;padding:20px;border-radius:15px;border-top:8px solid #1B5E20;box-shadow:0 4px 10px rgba(0,0,0,0.05)}</style>", unsafe_allow_html=True)

_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"):
            st.image(f, use_container_width=True)

st.markdown("<h1 style='text-align:center;color:#1B5E20;margin-top:-20px;'>Consultor Multiagro AgTech</h1>", unsafe_allow_html=True)

# --- 5. MÓDULO DE DIAGNÓSTICO IA ---
st.markdown("<div class='card'>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
cult = c1.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
opc = c2.radio("Entrada:", ["Cámara", "Galería"], horizontal=True)
img = st.camera_input("Foto") if opc == "Cámara" else st.file_uploader("Subir", type=['jpg','png','jpeg'])

if img and st.button("🚀 INICIAR ANÁLISIS"):
    with st.spinner("Analizando..."):
        try:
            res = model.generate_content([f"Agrónomo RD: analiza {cult}", Image.open(img)])
            st.success("✅ Diagnóstico listo")
            st.write(res.text)
        except:
            st.error("Límite de cuota IA alcanzado.")
st.markdown("</div>", unsafe_allow_html=True)

# --- 6. MÓDULO ODOO (Catálogo Real) ---
st.markdown("<h3 style='color:#1B5E20;margin-top:25px'>🛒 Inventario Real (Odoo)</h3>", unsafe_allow_html=True)

estado, resultado = conectar_odoo()

if estado == "OK":
    cols = st.columns(len(resultado))
    for i, (nombre, precio) in enumerate(resultado):
        with cols[i]:
            st.info(f"**{nombre}**\n\n{precio}")
            link = f"https://wa.me/18095551234?text=Interes en {nombre}"
            st.markdown(f"[💬 WhatsApp]({link})")
elif estado == "ERROR_AUTH":
    st.error("❌ Error de Autenticación: El Usuario o la API Key en Secrets son incorrectos.")
else:
    st.warning(f"⚠️ Error de Conexión. Verifique URL y Nombre de Base de Datos.")
    st.caption(f"Detalle técnico: {resultado}")

# --- 7. LOGOS EMPRESAS ---
st.divider()
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

st.markdown("<p style='text-align:center;font-size:12px;color:#aaa;margin-top:30px;'>© 2026 GRUPO MULTIAGRO | Conectado a Odoo Iterativo</p>", unsafe_allow_html=True)
