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
from datetime import date, datetime, timedelta
from supabase import create_client, Client
import streamlit.components.v1 as components

# =========================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y ANTI-ERROR 500
# =========================================================================
st.set_page_config(
    page_title="AgroDiagnóstico Multiagro", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# Script de persistencia para evitar cierres de sesión por inactividad
components.html("""
    <script>
    let tiempoOculto;
    document.addEventListener("visibilitychange", () => {
        if (document.hidden) { 
            tiempoOculto = new Date().getTime(); 
        } else {
            if (tiempoOculto) {
                let tiempoFuera = new Date().getTime() - tiempoOculto;
                if (tiempoFuera > 900000) { 
                    window.parent.location.reload(); 
                }
            }
        }
    });
    </script>
""", height=0, width=0)

# =========================================================================
# 2. BLOQUE DE APARIENCIA (CSS COMPLETO Y PERFECCIONADO)
# =========================================================================
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container { overflow-x: hidden !important; }
    
    .diag-box { background: #161B22; border-left: 8px solid #007BFF; padding: 25px; border-radius: 20px; margin-bottom: 30px; color: #FFFFFF !important; font-size: 1.05rem; line-height: 1.6; }
    .diag-box p, .diag-box span, .diag-box li, .diag-box div { color: #FFFFFF !important; }
    .diag-box strong, .diag-box b { color: #4DA3FF !important; }
    
    .product-card { 
        background-color: #1E1E26; 
        border-radius: 25px; 
        padding: 20px; 
        border: 1px solid #3E3E4A; 
        text-align: center; 
        margin-bottom: 20px; 
        display: flex; 
        flex-direction: column; 
        justify-content: space-between; 
        height: 100%; 
        position: relative;
    }
    .product-card h4 { color: #FFFFFF !important; font-size: 0.85rem; margin-top: 10px; margin-bottom: 5px; }
    .product-img { width: 100%; height: 140px; object-fit: contain; background-color: white; border-radius: 20px; padding: 10px; margin-bottom: 15px; }
    
    .badge-fav { position: absolute; top: 10px; right: 10px; background-color: #FFD700; color: #000; font-size: 0.7rem; font-weight: bold; padding: 3px 8px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }

    hr { border: 0; height: 1px; background: linear-gradient(to right, transparent, #3E3E4A, transparent); margin: 40px 0; }
    
    .logo-container { display: flex; justify-content: center; align-items: center; height: 80px; background: #FFFFFF; border-radius: 15px; padding: 10px; margin-bottom: 15px; border: 1px solid #DDD; }
    .logo-container img { height: 50px; width: auto; object-fit: contain; }
    
    .hero-banner { background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url('https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=1600&q=80'); background-size: cover; background-position: center 30%; width: 100%; height: 220px; border-radius: 15px; margin-top: 15px; margin-bottom: 30px; display: flex; align-items: center; justify-content: center; }
    .hero-title { color: #FFFFFF !important; font-size: 2.5rem; font-weight: bold; margin: 0; text-shadow: 2px 2px 5px rgba(0,0,0,0.6); text-align: center; }
    
    .login-box { background-color: #1E1E26; border-radius: 25px; padding: 0px; border: 1px solid #3E3E4A; text-align: center; margin-top: 50px; box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.5); overflow: hidden; }
    
    .cart-box { background-color: #007BFF; color: white; padding: 15px; border-radius: 15px; text-align: center; font-weight: bold; margin-bottom: 20px; position: sticky; bottom: 10px; z-index: 999; box-shadow: 0px -5px 15px rgba(0,0,0,0.5); }
    </style>
    """, unsafe_allow_html=True)

# =========================================================================
# 3. VARIABLES DE SESIÓN Y DICCIONARIOS DE CLASIFICACIÓN
# =========================================================================
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state: st.session_state.prods_filtrados = []
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_tier" not in st.session_state: st.session_state.user_tier = "free"
if "inventario_odoo" not in st.session_state: st.session_state.inventario_odoo = [] 
if "carrito" not in st.session_state: st.session_state.carrito = []

# Clasificación Multiagro basada en raíces de palabras
kw_fito = ["ACIDO", "AMINOACIDO", "BACTERICIDA", "COADYUVANTE", "ENRAIZADOR", "FERTILIZANTE", "FUNGICIDA", "HERBICIDA", "HORMONA", "INOCULANTE", "INSECTICIDA", "NUTRICION", "FOLIAR"]
kw_semillas = ["AJI", "AROMATICA", "CALABAZA", "CILANTRO", "MAIZ", "PEPINO", "SANDIA", "TOMATE", "SEMILLA", "CEBOLLA", "LECHUGA", "MELON", "ZANAHORIA", "BERENJENA"]
kw_riego = ["ACCESORIO", "ASPERSOR", "CINTA", "CONECTOR", "BOMBEO", "FILTRAD", "LAYFLAT", "MICROASPERSOR", "RIEGO", "TUBERIA", "VALVULA", "GOTEO"]
kw_equipos = ["BANDEJA", "DAEWOO", "EQUIPO", "FUMIGADOR", "GERMINACION", "HERRAMIENTA", "LANZA", "LIQUIDACION", "JARDIN", "MALLA", "MATERIAL", "PIEZA", "PLASTICO", "SARAN", "SIRFRAN", "SUBSTRATO", "SUSTRATO"]

# =========================================================================
# 4. FUNCIONES DE BASE DE DATOS Y CONEXIÓN A ODOO
# =========================================================================
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

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
            supabase.table("uso_diario").update({"conteo": res.data[0]["conteo"] + 1}).eq("email", email).execute()
    except: pass

def get_odoo_prods():
    try:
        url, db, user, key = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"], st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            # Aumentamos a 2000 el límite para traer todo el catálogo
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 2000})
            productos = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price', 'image_128', 'categ_id', 'priority', 'description', 'description_sale']})
            # Favoritos primero
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
            return models.execute_kw(db, uid, key, 'res.partner', 'create', [{'name': nombre, 'email': email, 'phone': telefono, 'comment': f'App AgroDiagnóstico | Prov: {lugar}'}])
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
        server.starttls()
        server.login(rem, pas)
        server.send_message(msg)
        server.quit()
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
            st.session_state.chat_history.append({"role": "model", "parts": [f"❌ Error: {str(e)}"]})
        st.session_state.input_duda = ""

# =========================================================================
# 5. LÓGICA DE LOGIN
# =========================================================================
if not st.session_state.authenticated:
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center; background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=800&q=80'); background-size: cover; background-position: center; padding: 40px 20px;">
                <h2 style='color: #FFFFFF; font-weight: bold;'>Multiagro IA</h2>
                <p style='color: #DDDDDD;'>Diagnóstico Agronómico Profesional</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="padding: 30px;">', unsafe_allow_html=True)
        email_input = st.text_input("Correo Electrónico", placeholder="ejemplo@correo.com")
        
        if st.button("Entrar a la Plataforma", use_container_width=True):
            if email_input and "@" in email_input:
                st.session_state.user_email = email_input.lower().strip()
                st.session_state.authenticated = True
                with st.spinner("Verificando usuario..."):
                    dominio = st.session_state.user_email.split('@')[-1]
                    if dominio in ["grupomultiagro.com", "mundoagricola.net"]: 
                        st.session_state.user_tier = "collaborator"
                    elif es_cliente_vip_odoo(st.session_state.user_email): 
                        st.session_state.user_tier = "vip"
                    else: 
                        st.session_state.user_tier = "free"
                st.rerun()
            else: st.error("Ingresa un correo válido.")
        st.markdown('</div></div>', unsafe_allow_html=True)

else:
    # =========================================================================
    # 6. APP PRINCIPAL (VUELTA AL PODER TOTAL)
    # =========================================================================
    
    # Barra lateral VIP
    st.sidebar.title("👨‍🌾 Mi Perfil")
    if st.session_state.user_tier == "collaborator": st.sidebar.success(f"⭐ Staff Multiagro")
    elif st.session_state.user_tier == "vip": st.sidebar.success(f"🌟 Cliente VIP")
    else: st.sidebar.info(f"👤 Usuario Estándar")
    st.sidebar.write(st.session_state.user_email)
    
    if st.sidebar.button("🔄 Actualizar Productos Odoo"):
        st.session_state.inventario_odoo = get_odoo_prods()
        st.sidebar.success("¡Catálogo sincronizado!")

    # Carga de inventario
    if not st.session_state.inventario_odoo:
        with st.spinner("Conectando con Odoo..."):
            st.session_state.inventario_odoo = get_odoo_prods() or []

    # Clasificación maestra
    p_med, p_sem, p_rie, p_equ = [], [], [], []
    for p in st.session_state.inventario_odoo:
        cat_data = p.get('categ_id')
        if isinstance(cat_data, list) and len(cat_data) > 1:
            cn = str(cat_data[1]).upper()
            if any(k in cn for k in kw_fito): p_med.append(p)
            elif any(k in cn for k in kw_semillas): p_sem.append(p)
            elif any(k in cn for k in kw_riego): p_rie.append(p)
            elif any(k in cn for k in kw_equipos): p_equ.append(p)

    st.markdown('<div class="hero-banner"><h1 class="hero-title">Diagnóstico Experto</h1></div>', unsafe_allow_html=True)
    
    cultivo_input = st.text_input("¿Qué cultivo estás analizando?", placeholder="Ej: Tomate, Aguacate, Arroz...")

    img = st.camera_input("Captura la plaga o enfermedad")

    # --- LÓGICA IA CON INGREDIENTES ACTIVOS ---
    if img is not None:
        if st.button("🚀 ANALIZAR CON INTELIGENCIA ARTIFICIAL", type="primary", use_container_width=True):
            if not puede_consultar(st.session_state.user_email, st.session_state.user_tier):
                st.error("Límite diario alcanzado. Regístrate para obtener más.")
            else:
                with st.spinner("IA analizando ingredientes activos..."):
                    try:
                        inv_ia_contexto = ""
                        for p in p_med:
                            desc = str(p.get('description') or p.get('description_sale') or "").replace('\n', ' ').strip()
                            inv_ia_contexto += f"- {p['name']} (Química: {desc})\n"

                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel('gemini-2.0-flash-lite')
                        
                        prompt = f"""
                        Eres Fitopatólogo de Multiagro. Analiza el cultivo de {cultivo_input}.
                        1. DIAGNÓSTICO: Identifica la plaga, hongo o bacteria.
                        2. RECETA: RECOMIENDA EXACTAMENTE 4 productos de esta lista basándote en que su ingrediente activo sea el ideal para el problema:
                        {inv_ia_contexto[:4000]}
                        Escribe los nombres de los 4 productos en NEGRITAS.
                        3. TRATAMIENTO: Explica dosis y frecuencia.
                        """
                        
                        res = model.generate_content([prompt, Image.open(img)])
                        
                        # Extraer los productos citados por la IA para las tarjetas
                        txt_ia = res.text.lower()
                        sug_final = []
                        vistos = set()
                        for p in p_med:
                            if p['name'].lower() in txt_ia and p['name'] not in vistos:
                                sug_final.append(p); vistos.add(p['name'])
                            if len(sug_final) >= 4: break

                        st.session_state.chat_history = [{"role": "user", "parts": ["Diagnóstico solicitado."]}, {"role": "model", "parts": [res.text]}]
                        st.session_state.prods_filtrados = sug_final
                        registrar_uso(st.session_state.user_email, st.session_state.user_tier)
                        st.rerun()
                    except Exception as e: st.error(f"Error IA: {e}")

    # --- CHAT Y TARJETAS RECOMENDADAS ---
    if st.session_state.chat_history:
        for i, msj in enumerate(st.session_state.chat_history):
            if i == 0: continue 
            if msj["role"] == "model": st.markdown(f"<div class='diag-box'>🤖 <b>Respuesta Multiagro:</b><br><br>{msj['parts'][0]}</div>", unsafe_allow_html=True)
            else: st.markdown(f"<div style='text-align: right; background-color: #007BFF; color: white; padding: 15px; border-radius: 20px; margin-bottom: 25px; margin-left: 15%;'>👤 <b>Tú:</b><br>{msj['parts'][0]}</div>", unsafe_allow_html=True)

        st.text_input("💬 Haz una pregunta adicional sobre el diagnóstico:", key="input_duda", on_change=enviar_pregunta)
        
        # Botón de consulta humana
        msg_wa_tec = urllib.parse.quote("Hola, necesito ayuda con este diagnóstico de la app Multiagro.")
        st.link_button("👨‍🌾 Hablar con un Técnico Real (WhatsApp)", f"https://wa.me/18295624653?text={msg_wa_tec}", type="secondary", use_container_width=True)

        if st.session_state.prods_filtrados:
            st.markdown("<h4 style='color: #4DA3FF; margin-top:20px;'>🧪 Productos sugeridos por IA:</h4>", unsafe_allow_html=True)
            c_ia = st.columns(2)
            for i, p in enumerate(st.session_state.prods_filtrados):
                with c_ia[i % 2]:
                    img_b64 = f'<img src="data:image/png;base64,{p["image_128"]}" class="product-img">' if p.get('image_128') else ""
                    st.markdown(f"<div class='product-card'>{img_b64}<h4>{p['name'].split('(')[0]}</h4></div>", unsafe_allow_html=True)
                    if st.button("➕ Cotizar", key=f"sug_btn_{p['id']}"): 
                        agregar_al_carrito(p['name'])
                        st.toast("Añadido!")

    # =========================================================================
    # 7. CATÁLOGO MAESTRO (4 PRODUCTOS + BUSCADOR POTENTE)
    # =========================================================================
    st.divider()
    st.markdown("<h2 style='text-align: center; color: white;'>🏪 Catálogo Multiagro</h2>", unsafe_allow_html=True)
    busqueda_global = st.text_input("🔍 Buscar por nombre o ingrediente activo (Ej: Abamectina)", placeholder="¿Qué estás buscando?")
    
    t1, t2, t3, t4 = st.tabs(["🧪 Fito & Nutri", "🌱 Semillas", "💧 Riego", "🛠️ Equipos"])
    
    def render_tab(lista, bq):
        if bq:
            q = bq.lower()
            lf = [p for p in lista if q in p['name'].lower() or q in str(p.get('description','')).lower()]
        else: lf = lista
        
        if not lf: st.info("No se encontraron productos.")
        else:
            cols = st.columns(2)
            for idx, p in enumerate(lf[:4]): # Límite de 4 productos
                with cols[idx % 2]:
                    img_html = f'<img src="data:image/png;base64,{p["image_128"]}" class="product-img">' if p.get('image_128') else ""
                    fav_badge = '<div class="badge-fav">⭐</div>' if str(p.get('priority','0')) == '1' else ""
                    
                    st.markdown(f"""
                        <div class="product-card">
                            {fav_badge}
                            {img_html}
                            <h4>{p['name'].split('(')[0]}</h4>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Añadir", key=f"cat_btn_{p['id']}"):
                        agregar_al_carrito(p['name'])
                        st.toast("Agregado al carrito")
                        st.rerun()

    with t1: render_tab(p_med, busqueda_global)
    with t2: render_tab(p_sem, busqueda_global)
    with t3: render_tab(p_rie, busqueda_global)
    with t4: render_tab(p_equ, busqueda_global)

    # =========================================================================
    # 8. CARRITO Y REGISTRO
    # =========================================================================
    if st.session_state.carrito:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="cart-box">', unsafe_allow_html=True)
        st.markdown(f"🛒 **Tu Cotización ({len(st.session_state.carrito)} productos)**")
        
        txt_cart = "Hola Multiagro, cotización para " + st.session_state.user_email + ":\n" + "\n".join([f"- {i}" for i in st.session_state.carrito])
        url_wa_cart = f"https://wa.me/18295624653?text={urllib.parse.quote(txt_cart)}"
        
        st.link_button("📲 ENVIAR COTIZACIÓN (1 CLIC)", url_wa_cart, type="primary", use_container_width=True)
        
        if st.button("🗑️ Vaciar Carrito"): 
            st.session_state.carrito = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Registro de productor
    st.divider()
    st.markdown("### 👤 Registro de Productor")
    if 'reg_ok' not in st.session_state:
        with st.form("registro"):
            n = st.text_input("Nombre completo")
            t = st.text_input("WhatsApp")
            l = st.selectbox("Provincia", ["Azua", "Baoruco", "Barahona", "Dajabón", "Distrito Nacional", "Duarte", "Elías Piña", "El Seibo", "Espaillat", "Hato Mayor", "Hermanas Mirabal", "Independencia", "La Altagracia", "La Romana", "La Vega", "María Trinidad Sánchez", "Monseñor Nouel", "Monte Cristi", "Monte Plata", "Pedernales", "Peravia", "Puerto Plata", "Samaná", "Sánchez Ramírez", "San Cristóbal", "San José de Ocoa", "San Juan", "San Pedro de Macorís", "Santiago", "Santiago Rodríguez", "Santo Domingo", "Valverde"])
            if st.form_submit_button("✅ Activar Beneficios"):
                if n and t:
                    registrar_cliente_odoo(n, st.session_state.user_email, t, l)
                    enviar_aviso_email(n, st.session_state.user_email, t, l)
                    st.session_state['reg_ok'] = n
                    st.rerun()
    else: st.success(f"¡Bienvenido {st.session_state['reg_ok']}! Nivel de consultas aumentado.")

    # LOGOS DE EMPRESAS
    st.divider()
    st.markdown("<h4 style='text-align: center; color: #007BFF;'>Empresas Grupo Multiagro</h4>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png"]
    for i, logo in enumerate(logos):
        if os.path.exists(logo):
            with open(logo, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                with [col1, col2, col3][i]:
                    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{b64}"></div>', unsafe_allow_html=True)

    st.markdown("<p style='text-align:center; color:#666; font-size:0.8rem; margin-top:40px;'>© 2026 Grupo Multiagro | Desarrollado con IA</p>", unsafe_allow_html=True)
