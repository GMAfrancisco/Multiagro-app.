import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from datetime import date, datetime, timedelta
from supabase import create_client, Client
import streamlit.components.v1 as components

# =========================================================================
# 1. CONFIGURACIÓN DE PÁGINA
# =========================================================================
st.set_page_config(page_title="Grupo Multiagro | AgTech", layout="wide")

components.html("""
    <script>
    let tiempoOculto;
    document.addEventListener("visibilitychange", () => {
        if (document.hidden) { tiempoOculto = new Date().getTime(); } 
        else {
            if (tiempoOculto) {
                let tiempoFuera = new Date().getTime() - tiempoOculto;
                if (tiempoFuera > 900000) { window.parent.location.reload(); }
            }
        }
    });
    </script>
""", height=0, width=0)

# =========================================================================
# 2. BLOQUE DE APARIENCIA (CSS DEL CÓDIGO VIEJO)
# =========================================================================
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    [data-testid="stFileUploadDropzone"] { background-color: #F0F2F6 !important; border-radius: 20px; border: 2px dashed #007BFF !important; }
    [data-testid="stFileUploadDropzone"] * { color: #000000 !important; }

    [data-testid="stBaseButton-secondary"] p, [data-testid="stBaseButton-primary"] p, .stButton button p, .stFormSubmitButton button p { color: #000000 !important; font-weight: bold !important; margin-bottom: 0px !important; }
    div.stButton > button, div.stFormSubmitButton > button, a[data-testid="stBaseButton-secondary"], a[data-testid="stBaseButton-primary"] { background-color: #007BFF !important; color: #000000 !important; border-radius: 30px !important; font-weight: bold !important; border: none !important; height: 45px !important; }

    .product-card { background-color: #1E1E26; border-radius: 25px; padding: 25px; border: 1px solid #3E3E4A; text-align: center; margin-bottom: 20px; transition: transform 0.3s ease; position: relative; display: flex; flex-direction: column; justify-content: space-between; height: 100%;}
    .product-card:hover { transform: translateY(-5px); } 
    .product-card h4 { color: #FFFFFF !important; font-size: 0.9rem; margin-top: 10px; margin-bottom: 5px;}
    .product-img { width: 100%; height: 140px; object-fit: contain; background-color: white; border-radius: 20px; padding: 10px; margin-bottom: 15px; }
    
    .badge-fav { position: absolute; top: 10px; right: 10px; background-color: #FFD700; color: #000; font-size: 0.7rem; font-weight: bold; padding: 3px 8px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }

    .diag-box { background: #161B22; border-left: 8px solid #007BFF; padding: 25px; border-radius: 20px; margin-bottom: 30px; color: white !important;}
    .diag-box p, .diag-box li, .diag-box span { color: white !important; }
    .diag-box strong, .diag-box b { color: #4DA3FF !important; }

    hr { border: 0; height: 1px; background: linear-gradient(to right, transparent, #3E3E4A, transparent); margin: 40px 0; }
    .logo-container { display: flex; justify-content: center; align-items: center; height: 100px; background: #FFFFFF; border-radius: 20px; padding: 15px; margin-bottom: 15px;}
    .logo-container img { height: 60px; width: auto; object-fit: contain; }
    
    label, .stMarkdown, p, span { color: #FFFFFF !important; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div { background-color: #161B22; color: white; border-radius: 15px; }

    .hero-banner { background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url('https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=1600&q=80'); background-size: cover; background-position: center 30%; width: 100%; height: 220px; border-radius: 15px; margin-top: 15px; margin-bottom: 30px; display: flex; align-items: center; justify-content: center; }
    .hero-title { color: #FFFFFF !important; font-size: 3rem; font-weight: bold; margin: 0; text-shadow: 2px 2px 5px rgba(0,0,0,0.6); display: flex; align-items: center; gap: 15px; }
    
    .login-box { background-color: #1E1E26; border-radius: 25px; padding: 0px; border: 1px solid #3E3E4A; text-align: center; margin-top: 50px; box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.5); overflow: hidden; }
    
    .cart-box { background-color: #007BFF; color: white; padding: 20px; border-radius: 20px; text-align: center; font-weight: bold; margin-bottom: 20px; position: sticky; bottom: 10px; z-index: 999; box-shadow: 0px -5px 15px rgba(0,0,0,0.5); }
    .cart-box p, .cart-box b, .cart-box h3 { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# =========================================================================
# 3. INICIALIZACIÓN DE VARIABLES DE SESIÓN
# =========================================================================
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state: st.session_state.prods_filtrados = []
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_tier" not in st.session_state: st.session_state.user_tier = "free"
if "inventario_odoo" not in st.session_state: st.session_state.inventario_odoo = [] 
if "carrito" not in st.session_state: st.session_state.carrito = []

kw_fito = ["ACIDO", "AMINOACIDO", "BACTERICIDA", "COADYUVANTE", "ENRAIZADOR", "FERTILIZANTE", "FUNGICIDA", "HERBICIDA", "HORMONA", "INOCULANTE", "INSECTICIDA", "NUTRICION", "FOLIAR"]
kw_semillas = ["AJI", "AROMATICA", "CALABAZA", "CILANTRO", "MAIZ", "PEPINO", "SANDIA", "TOMATE", "SEMILLA", "CEBOLLA", "LECHUGA", "MELON", "ZANAHORIA", "BERENJENA"]
kw_riego = ["ACCESORIO", "ASPERSOR", "CINTA", "CONECTOR", "BOMBEO", "FILTRAD", "LAYFLAT", "MICROASPERSOR", "RIEGO", "TUBERIA", "VALVULA", "GOTEO"]
kw_equipos = ["BANDEJA", "DAEWOO", "EQUIPO", "FUMIGADOR", "GERMINACION", "HERRAMIENTA", "LANZA", "LIQUIDACION", "JARDIN", "MALLA", "MATERIAL", "PIEZA", "PLASTICO", "SARAN", "SIRFRAN", "SUBSTRATO", "SUSTRATO"]

# =========================================================================
# 4. FUNCIONES DE INTEGRACIÓN SUPABASE Y ODOO
# =========================================================================
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_supabase()

def puede_consultar(email, tier):
    if tier in ["collaborator", "vip"]: return True 
    hoy = str(date.today())
    try:
        res = supabase.table("uso_diario").select("*").eq("email", email).execute()
        if not res.data:
            supabase.table("uso_diario").insert({"email": email, "conteo": 0, "fecha_ultimo_uso": hoy}).execute()
            conteo, fecha = 0, hoy
        else:
            conteo, fecha = res.data[0]["conteo"], res.data[0]["fecha_ultimo_uso"]
            
        if fecha != hoy:
            conteo = 0
            supabase.table("uso_diario").update({"conteo": 0, "fecha_ultimo_uso": hoy}).eq("email", email).execute()
            
        limite = 5 if tier == "registered" else 2
        return conteo < limite
    except: return True

def registrar_uso(email, tier):
    if tier in ["collaborator", "vip"]: return
    try:
        res = supabase.table("uso_diario").select("conteo").eq("email", email).execute()
        if res.data:
            nuevo_conteo = res.data[0]["conteo"] + 1
            supabase.table("uso_diario").update({"conteo": nuevo_conteo}).eq("email", email).execute()
    except: pass

def get_odoo_prods():
    try:
        url, db, user, key = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"], st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 2000})
            productos = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price', 'image_128', 'categ_id', 'priority', 'description']})
            productos.sort(key=lambda x: 1 if str(x.get('priority', '0')) == '1' else 0, reverse=True)
            return productos
    except: return None

def registrar_cliente_odoo(nombre, email, telefono, lugar):
    try:
        url, db, user, key = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"], st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            return models.execute_kw(db, uid, key, 'res.partner', 'create', [{'name': nombre, 'email': email, 'phone': telefono, 'comment': f'App AgTech Multiagro | Provincia: {lugar}'}])
    except: return None

def es_cliente_vip_odoo(email):
    try:
        url, db, user, key = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"], st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            partner_ids = models.execute_kw(db, uid, key, 'res.partner', 'search', [[['email', '=', email]]])
            if not partner_ids: return False
            fecha_hace_60_dias = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d %H:%M:%S')
            order_ids = models.execute_kw(db, uid, key, 'sale.order', 'search', [['partner_id', 'in', partner_ids], ['state', 'in', ['sale', 'done']], ['date_order', '>=', fecha_hace_60_dias]])
            return len(order_ids) > 0
    except: return False

def enviar_aviso_email(nombre, email, tel, lugar):
    try:
        rem, pas = st.secrets["EMAIL_SENDER"], st.secrets["EMAIL_PASSWORD"]
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = rem, st.secrets["EMAIL_RECEIVER"], f"🚀 Nuevo Registro: {nombre}"
        msg.attach(MIMEText(f"Nombre: {nombre}\nEmail: {email}\nTel: {tel}\nProvincia: {lugar}", 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls(); server.login(rem, pas); server.send_message(msg); server.quit()
        return True
    except: return False

def agregar_al_carrito(nombre_producto):
    if nombre_producto not in st.session_state.carrito:
        st.session_state.carrito.append(nombre_producto)

def enviar_pregunta():
    duda = st.session_state.input_duda
    if duda:
        st.session_state.chat_history.append({"role": "user", "parts": [duda]})
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            respuesta = model.generate_content(st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "model", "parts": [respuesta.text]})
        except Exception as e:
            st.session_state.chat_history.append({"role": "model", "parts": [f"❌ Ocurrió un error al consultar: {str(e)}"]})
        st.session_state.input_duda = ""

# =========================================================================
# 5. LOGICA DE AUTENTICACIÓN
# =========================================================================
if not st.session_state.authenticated:
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        for f in sorted(os.listdir(".")):
            if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
                st.image(f, use_container_width=True)
        
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center; background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=800&q=80'); background-size: cover; background-position: center; padding: 40px 20px; border-bottom: 1px solid #3E3E4A;">
                <h2 style='text-align: center; color: #FFFFFF; margin: 0; text-shadow: 2px 2px 5px rgba(0,0,0,0.9); font-weight: bold;'>Bienvenido a AgTech Multiagro</h2>
                <p style='text-align: center; color: #DDDDDD; margin-top: 10px; margin-bottom: 0; text-shadow: 1px 1px 3px rgba(0,0,0,0.9); font-size: 1.1rem;'>Ingresa tu correo electrónico para acceder al Diagnóstico Experto con IA.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="padding: 30px; padding-top: 15px;">', unsafe_allow_html=True)
        email_input = st.text_input("Correo Electrónico", placeholder="ejemplo@correo.com", label_visibility="collapsed")
        
        if st.button("Ingresar a la Plataforma", use_container_width=True):
            if email_input and "@" in email_input and "." in email_input:
                email_lower = email_input.lower().strip()
                st.session_state.user_email = email_lower
                st.session_state.authenticated = True
                
                with st.spinner("Verificando credenciales..."):
                    dominio = email_lower.split('@')[-1]
                    if dominio in ["grupomultiagro.com", "mundoagricola.net"]:
                        st.session_state.user_tier = "collaborator"
                    elif es_cliente_vip_odoo(email_lower):
                        st.session_state.user_tier = "vip"
                    else:
                        st.session_state.user_tier = "free"
                st.rerun()
            else:
                st.error("Por favor, ingresa un correo electrónico válido.")
        st.markdown('</div></div>', unsafe_allow_html=True)

else:
    # =========================================================================
    # 6. INICIO DEL CÓDIGO MAESTRO DE LA APP
    # =========================================================================
    
    if st.session_state.user_tier == "collaborator":
        st.sidebar.success(f"👑 Acceso Ilimitado (Staff)\n{st.session_state.user_email}")
    elif st.session_state.user_tier == "vip":
        st.sidebar.success(f"🌟 Cliente VIP (Ilimitado)\n¡Gracias por preferir a Grupo Multiagro!\n{st.session_state.user_email}")
    elif st.session_state.user_tier == "registered":
        st.sidebar.info(f"✅ Usuario Registrado (5 Consultas)\n{st.session_state.user_email}")
    else:
        st.sidebar.info(f"👤 Usuario Gratuito (2 Consultas)\n{st.session_state.user_email}")
        
    st.sidebar.divider()
    if st.sidebar.button("🔄 Actualizar Catálogo Odoo"):
        with st.spinner("Descargando catálogo..."):
            st.session_state.inventario_odoo = get_odoo_prods() or []
        st.sidebar.success("¡Actualizado!")

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        for f in sorted(os.listdir(".")):
            if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
                st.image(f, use_container_width=True)

    if not st.session_state.inventario_odoo:
        st.session_state.inventario_odoo = get_odoo_prods() or []

    # Clasificación robusta
    p_med, p_sem, p_rie, p_equ = [], [], [], []
    for p in st.session_state.inventario_odoo:
        cat = p.get('categ_id')
        if isinstance(cat, list) and len(cat) > 1:
            cn = str(cat[1]).upper() 
            if any(k in cn for k in kw_fito): p_med.append(p)
            elif any(k in cn for k in kw_semillas): p_sem.append(p)
            elif any(k in cn for k in kw_riego): p_rie.append(p)
            elif any(k in cn for k in kw_equipos): p_equ.append(p)

    st.markdown("""
        <div class="hero-banner">
            <h1 class="hero-title">🔍 Diagnóstico Experto</h1>
        </div>
    """, unsafe_allow_html=True)

    cultivo_input = st.text_input("¿Qué cultivo o planta estamos analizando?", placeholder="Ej: Arroz, Tomate, Aguacate...")

    tab_gal, tab_cam = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
    with tab_gal: img_gal = st.file_uploader("Subir imagen", type=['png', 'jpg', 'jpeg'], key="uploader_gal")
    with tab_cam: img_cam = st.camera_input("Tomar foto")

    img = img_cam if img_cam else img_gal

    # LÓGICA DE IA MEJORADA (CON INGREDIENTES ACTIVOS)
    if img is not None:
        if st.button("🚀 INICIAR ASESORÍA COMPLETA", type="primary", use_container_width=True):
            if not puede_consultar(st.session_state.user_email, st.session_state.user_tier):
                st.error("⚠️ Has alcanzado tu límite de diagnósticos por hoy.")
                if st.session_state.user_tier == "free":
                    st.info("💡 Desliza hacia abajo y regístrate como Productor para obtener **5 consultas diarias** gratis.")
            else:
                with st.spinner("Analizando químicamente..."):
                    try:
                        inv_ia = ""
                        for p in p_med:
                            nota = str(p.get('description') or "Sin detalles").replace('\n', ' ').strip()
                            inv_ia += f"[{str(p.get('categ_id', [''])[1]).upper()}] - {p['name']} (Ingrediente: {nota})\n"

                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel('gemini-2.0-flash-lite')
                        
                        prompt = f"""
                        RESPONDE 100% EN ESPAÑOL. Eres Fitopatólogo y Entomólogo de Multiagro. 
                        CULTIVO: {cultivo_input if cultivo_input else 'No especificado'}.
                        1. IDENTIFICACIÓN POSITIVA: Nombre común y técnico de la plaga/hongo.
                        2. MANEJO QUÍMICO: RECOMIENDA EXACTAMENTE 4 productos diferentes de esta lista basándote en que su "Ingrediente" actúe contra el problema: \n{inv_ia[:4000]}
                        Pon nombres comerciales en NEGRITAS.
                        3. SEGURIDAD: Advierte leer la etiqueta del fabricante.
                        4. LABORES CULTURALES: Describe labores de campo específicas.
                        """
                        
                        res = model.generate_content([prompt, Image.open(img)])
                        texto_ia_lower = res.text.lower()
                        sugeridos, vistos = [], set()
                        
                        ignorar = ["fungicida", "insecticida", "herbicida", "fertilizante", "litro", "galon", "sc", "ec"]
                        for p in p_med:
                            nl = p['name'].split('(')[0].strip().lower()
                            pclave = next((w for w in nl.split() if w not in ignorar and len(w)>2), nl.split()[0] if nl else "")
                            if pclave and (pclave in texto_ia_lower or nl in texto_ia_lower) and pclave not in vistos:
                                sugeridos.append(p); vistos.add(pclave)
                            if len(sugeridos) >= 4: break
                        
                        st.session_state.chat_history = [
                            {"role": "user", "parts": [f"Contexto oculto: Realizaste análisis inicial de {cultivo_input}."]},
                            {"role": "model", "parts": [res.text]}
                        ]
                        st.session_state.prods_filtrados = sugeridos
                        registrar_uso(st.session_state.user_email, st.session_state.user_tier)
                        st.rerun()
                    except Exception as e:
                        if "rerun" not in str(e).lower(): st.error(f"Error: {e}")

    # RENDERIZADO VISUAL DEL CHAT
    if st.session_state.chat_history:
        for i, msj in enumerate(st.session_state.chat_history):
            if i == 0: continue 
            if msj["role"] == "model":
                st.markdown(f"<div class='diag-box'>🤖 {msj['parts'][0]}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: right; background-color: #007BFF; color: white; padding: 15px; border-radius: 20px; margin-bottom: 25px; margin-left: 15%; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);'>👤 <b>Tú:</b><br>{msj['parts'][0]}</div>", unsafe_allow_html=True)
        
        st.text_input("💬 Escribe tu duda sobre el manejo o el diagnóstico y presiona Enter:", key="input_duda", on_change=enviar_pregunta)
        
        # =====================================================================
        # SOLUCIÓN WHATSAPP EXACTA AL CÓDIGO VIEJO (Texto plano, sin quote)
        # =====================================================================
        enlace_wa_tecnico = "https://wa.me/18295624653?text=Hola, necesito consultar a un tecnico sobre un diagnostico en la app"
        st.link_button("👨‍🌾 Consultar dudas a un técnico por WhatsApp", enlace_wa_tecnico, type="secondary", use_container_width=True)

        if st.session_state.prods_filtrados:
            st.markdown("<h4 style='color: #007BFF; margin-top:20px;'>🛒 Soluciones Sugeridas</h4>", unsafe_allow_html=True)
            cols = st.columns(2)
            for i, p in enumerate(st.session_state.prods_filtrados):
                with cols[i % 2]:
                    img_b64 = f'<img src="data:image/png;base64,{p["image_128"]}" class="product-img">' if p.get('image_128') else ""
                    nc = p['name'].split('(')[0].strip()
                    st.markdown(f"""
                        <div class="product-card">
                            {img_b64}
                            <h4>{nc}</h4>
                            <p style='color: #007BFF; font-weight: bold; margin: 0;'>RD$ {p['list_price']:,.2f}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if nc in st.session_state.carrito: st.button("✅ Agregado", key=f"rec_ok_{p['id']}", disabled=True)
                    else: st.button("➕ Agregar a Cotización", key=f"rec_{p['id']}", on_click=agregar_al_carrito, args=(nc,))

    # =========================================================================
    # 7. CATÁLOGO E-COMMERCE (PESTAÑAS + CARRITO + BUSCADOR)
    # =========================================================================
    st.divider()
    st.markdown("<h2 style='text-align: center; color: #FFFFFF;'>🏪 Catálogo Multiagro</h2>", unsafe_allow_html=True)
    busqueda = st.text_input("🔍 Buscar por nombre o ingrediente activo...")
    
    t1, t2, t3, t4 = st.tabs(["🧪 Fito/Nutri", "🌱 Semillas", "💧 Riego", "🛠️ Equipos"])
    
    def render_cat(lista, q):
        if q:
            q = q.lower()
            lf = [p for p in lista if q in p['name'].lower() or q in str(p.get('description','')).lower()]
        else: lf = lista
        
        if not lf: st.info("No hay productos.")
        else:
            cols = st.columns(2)
            for idx, p in enumerate(lf[:4]):
                with cols[idx % 2]:
                    img_b64 = f'<img src="data:image/png;base64,{p["image_128"]}" class="product-img">' if p.get('image_128') else ""
                    badge = '<div class="badge-fav">⭐ Destacado</div>' if str(p.get('priority','0')) == '1' else ""
                    nc = p['name'].split('(')[0].strip()
                    st.markdown(f"""
                        <div class="product-card">
                            {badge}
                            {img_b64}
                            <h4>{nc}</h4>
                            <p style='color: #007BFF; font-weight: bold; margin: 0;'>RD$ {p['list_price']:,.2f}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if nc in st.session_state.carrito: st.button("✅ Agregado", key=f"c_ok_{p['id']}", disabled=True)
                    else: st.button("➕ Agregar", key=f"c_{p['id']}", on_click=agregar_al_carrito, args=(nc,))

    with t1: render_cat(p_med, busqueda)
    with t2: render_cat(p_sem, busqueda)
    with t3: render_cat(p_rie, busqueda)
    with t4: render_cat(p_equ, busqueda)

    # CARRITO DE COMPRAS FLOTANTE
    if st.session_state.carrito:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="cart-box">', unsafe_allow_html=True)
        st.markdown(f"<h3>🛒 Tu Cotización ({len(st.session_state.carrito)})</h3>", unsafe_allow_html=True)
        
        # =====================================================================
        # SOLUCIÓN WHATSAPP EXACTA AL CÓDIGO VIEJO (Texto plano, 1 sola línea)
        # =====================================================================
        productos_unidos = " - ".join(st.session_state.carrito)
        enlace_wa_carrito = f"https://wa.me/18295624653?text=Hola Multiagro, deseo cotizar los siguientes productos: {productos_unidos}"
        
        st.link_button("📲 ENVIAR COTIZACIÓN A WHATSAPP", enlace_wa_carrito, type="primary", use_container_width=True)
        
        if st.button("🗑️ Vaciar Carrito", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # 8. REGISTRO
    # =========================================================================
    st.divider()
    st.markdown("### 👤 Registro de Productor")

    provincias_rd = ["Azua", "Baoruco", "Barahona", "Dajabón", "Distrito Nacional", "Duarte", "Elías Piña", "El Seibo", "Espaillat", "Hato Mayor", "Hermanas Mirabal", "Independencia", "La Altagracia", "La Romana", "La Vega", "María Trinidad Sánchez", "Monseñor Nouel", "Monte Cristi", "Monte Plata", "Pedernales", "Peravia", "Puerto Plata", "Samaná", "Sánchez Ramírez", "San Cristóbal", "San José de Ocoa", "San Juan", "San Pedro de Macorís", "Santiago", "Santiago Rodríguez", "Santo Domingo", "Valverde"]

    if 'reg_ok' not in st.session_state:
        if st.session_state.user_tier in ["free", "registered"]:
            with st.form("form_registro"):
                nom = st.text_input("Nombre completo *")
                ema = st.text_input("Correo electrónico", value=st.session_state.user_email)
                tel = st.text_input("WhatsApp / Teléfono *")
                lugar = st.selectbox("Lugar (Provincia) *", provincias_rd)
                
                if st.form_submit_button("✅ Regístrame (Sube a 5 consultas/día)"):
                    if nom and tel and lugar:
                        if registrar_cliente_odoo(nom, ema, tel, lugar):
                            enviar_aviso_email(nom, ema, tel, lugar)
                            st.session_state['reg_ok'] = nom
                            st.session_state.user_tier = "registered"
                            st.rerun()
        else: 
            st.success("¡Tu cuenta tiene acceso ilimitado! No necesitas registrarte.")
    else: 
        st.success(f"Bienvenido, {st.session_state['reg_ok']}! Tienes tus consultas diarias activadas.")

    # =========================================================================
    # 9. LOGOS FINALES (DISEÑO ORIGINAL DE 5 COLUMNAS)
    # =========================================================================
    st.divider()
    st.markdown("<h4 style='text-align: center; color: #007BFF; margin-bottom: 20px;'>Empresas Grupo Multiagro</h4>", unsafe_allow_html=True)

    l_cols = st.columns(5)
    logos_list = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
    for i, l_file in enumerate(logos_list):
        with l_cols[i]:
            if os.path.exists(l_file):
                with open(l_file, "rb") as f: 
                    b64_logo = base64.b64encode(f.read()).decode()
                st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{b64_logo}"></div>', unsafe_allow_html=True)
                
    st.markdown("""
        <div style='text-align: center; color: #666666; font-size: 0.85rem; margin-top: 50px; padding-bottom: 20px;'>
            &copy; 2026 Grupo Multiagro.<br>Desarrollado con Inteligencia Artificial.
        </div>
    """, unsafe_allow_html=True)
