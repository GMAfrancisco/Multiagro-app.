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
# 2. BLOQUE DE APARIENCIA (CSS)
# =========================================================================
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container { overflow-x: hidden !important; }
    
    .diag-box { background: #161B22; border-left: 8px solid #007BFF; padding: 25px; border-radius: 20px; margin-bottom: 30px; color: #FFFFFF !important; font-size: 1.05rem; line-height: 1.6; }
    .diag-box p, .diag-box span, .diag-box li, .diag-box div { color: #FFFFFF !important; }
    .diag-box strong, .diag-box b { color: #4DA3FF !important; }
    
    .product-card { background-color: #1E1E26; border-radius: 25px; padding: 20px; border: 1px solid #3E3E4A; text-align: center; margin-bottom: 20px; display: flex; flex-direction: column; justify-content: space-between; height: 100%; position: relative;}
    .product-img { width: 100%; height: 140px; object-fit: contain; background-color: white; border-radius: 20px; padding: 10px; margin-bottom: 15px; }
    
    .badge-fav { position: absolute; top: 10px; right: 10px; background-color: #FFD700; color: #000; font-size: 0.7rem; font-weight: bold; padding: 3px 8px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }

    hr { border: 0; height: 1px; background: linear-gradient(to right, transparent, #3E3E4A, transparent); margin: 40px 0; }
    .logo-container { display: flex; justify-content: center; align-items: center; height: 80px; background: #FFFFFF; border-radius: 15px; padding: 10px; margin-bottom: 15px; }
    .logo-container img { height: 50px; width: auto; object-fit: contain; }
    
    .hero-banner { background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url('https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=1600&q=80'); background-size: cover; background-position: center 30%; width: 100%; height: 220px; border-radius: 15px; margin-top: 15px; margin-bottom: 30px; display: flex; align-items: center; justify-content: center; }
    .hero-title { color: #FFFFFF !important; font-size: 3rem; font-weight: bold; margin: 0; text-shadow: 2px 2px 5px rgba(0,0,0,0.6); display: flex; align-items: center; gap: 15px; }
    .login-box { background-color: #1E1E26; border-radius: 25px; padding: 0px; border: 1px solid #3E3E4A; text-align: center; margin-top: 50px; box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.5); overflow: hidden; }
    
    .cart-box { background-color: #007BFF; color: white; padding: 15px; border-radius: 15px; text-align: center; font-weight: bold; margin-bottom: 20px; position: sticky; bottom: 10px; z-index: 999; box-shadow: 0px -5px 15px rgba(0,0,0,0.5); }
    </style>
    """, unsafe_allow_html=True)

# =========================================================================
# 3. VARIABLES DE SESIÓN Y CLASIFICACIÓN INMUNE A ERRORES
# =========================================================================
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state: st.session_state.prods_filtrados = []
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_tier" not in st.session_state: st.session_state.user_tier = "free"
if "todos_los_prods" not in st.session_state: st.session_state.todos_los_prods = [] 
if "carrito" not in st.session_state: st.session_state.carrito = []

kw_fito = ["ACIDO", "AMINOACIDO", "BACTERICIDA", "COADYUVANTE", "ENRAIZADOR", "FERTILIZANTE", "FUNGICIDA", "HERBICIDA", "HORMONA", "INOCULANTE", "INSECTICIDA", "NUTRICION", "FOLIAR"]
kw_semillas = ["AJI", "AROMATICA", "CALABAZA", "CILANTRO", "MAIZ", "PEPINO", "SANDIA", "TOMATE", "SEMILLA", "CEBOLLA", "LECHUGA", "MELON", "ZANAHORIA", "BERENJENA"]
kw_riego = ["ACCESORIO", "ASPERSOR", "CINTA", "CONECTOR", "BOMBEO", "FILTRAD", "LAYFLAT", "MICROASPERSOR", "RIEGO", "TUBERIA", "VALVULA", "GOTEO"]
kw_equipos = ["BANDEJA", "DAEWOO", "EQUIPO", "FUMIGADOR", "GERMINACION", "HERRAMIENTA", "LANZA", "LIQUIDACION", "JARDIN", "MALLA", "MATERIAL", "PIEZA", "PLASTICO", "SARAN", "SIRFRAN", "SUBSTRATO", "SUSTRATO"]

# =========================================================================
# 4. FUNCIONES DE BASE DE DATOS Y CONEXIÓN A ODOO (CON NOTAS INTERNAS)
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
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 200})
            
            productos = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price', 'image_128', 'categ_id', 'priority', 'description', 'description_sale']})
            
            def es_favorito(p):
                return 1 if str(p.get('priority', '0')) == '1' else 0
                
            productos.sort(key=es_favorito, reverse=True)
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
            st.session_state.chat_history.append({"role": "model", "parts": [f"❌ Ocurrió un error al consultar: {str(e)}"]})
        st.session_state.input_duda = ""

# =========================================================================
# 5. LÓGICA DE AUTENTICACIÓN (LOGIN)
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
                <h2 style='text-align: center; color: #FFFFFF; margin: 0; text-shadow: 2px 2px 5px rgba(0,0,0,0.9); font-weight: bold;'>Bienvenido a AgroDiagnóstico Multiagro</h2>
                <p style='text-align: center; color: #DDDDDD; margin-top: 10px; margin-bottom: 0; font-size: 1.1rem;'>Ingresa tu correo electrónico para acceder al Diagnóstico Experto con IA.</p>
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
                st.error("Por favor, ingresa un correo válido.")
        st.markdown('</div></div>', unsafe_allow_html=True)

else:
    # =========================================================================
    # 6. INICIO DE LA APLICACIÓN PRINCIPAL
    # =========================================================================
    
    # MENÚ LATERAL: Botón para forzar actualización de Odoo en vivo
    if st.session_state.user_tier == "collaborator": 
        st.sidebar.success(f"👑 Acceso Ilimitado (Staff)\n{st.session_state.user_email}")
    elif st.session_state.user_tier == "vip": 
        st.sidebar.success(f"🌟 Cliente VIP\n{st.session_state.user_email}")
    elif st.session_state.user_tier == "registered": 
        st.sidebar.info(f"✅ Usuario Registrado (5 Consultas)\n{st.session_state.user_email}")
    else: 
        st.sidebar.info(f"👤 Usuario Gratuito (2 Consultas)\n{st.session_state.user_email}")
        
    st.sidebar.divider()
    if st.sidebar.button("🔄 Actualizar Catálogo Odoo"):
        with st.spinner("Descargando productos y notas internas..."):
            st.session_state.todos_los_prods = get_odoo_prods() or []
        st.sidebar.success("¡Catálogo actualizado con éxito!")

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        for f in sorted(os.listdir(".")):
            if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"): 
                st.image(f, use_container_width=True)

    # AUTO-LIMPIADOR: Si la memoria vieja no tiene la palabra 'description' (notas), fuerza la descarga
    if not st.session_state.todos_los_prods or (st.session_state.todos_los_prods and 'description' not in st.session_state.todos_los_prods[0]):
        st.session_state.todos_los_prods = get_odoo_prods() or []

    prods_medicina = []
    prods_semillas = []
    prods_riego = []
    prods_equipos = []
    
    for p in st.session_state.todos_los_prods:
        categoria = p.get('categ_id')
        if isinstance(categoria, list) and len(categoria) > 1:
            cat_name = str(categoria[1]).upper() 
            
            if any(kw in cat_name for kw in kw_fito): prods_medicina.append(p)
            elif any(kw in cat_name for kw in kw_semillas): prods_semillas.append(p)
            elif any(kw in cat_name for kw in kw_riego): prods_riego.append(p)
            elif any(kw in cat_name for kw in kw_equipos): prods_equipos.append(p)

    st.markdown("""<div class="hero-banner"><h1 class="hero-title">🔍 Diagnóstico Experto</h1></div>""", unsafe_allow_html=True)
    
    cultivo_input = st.text_input("¿Qué cultivo o planta estamos analizando?", placeholder="Ej: Arroz, Tomate, Aguacate...")

    tab_gal, tab_cam = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
    with tab_gal: 
        img_gal = st.file_uploader("Subir imagen", type=['png', 'jpg', 'jpeg'], key="uploader_gal")
    with tab_cam: 
        img_cam = st.camera_input("Tomar foto")

    img = img_cam if img_cam else img_gal

    # =========================================================================
    # LÓGICA DE INTELIGENCIA ARTIFICIAL (CON NOTAS INTERNAS Y OBLIGACIÓN DE 4 PRODUCTOS)
    # =========================================================================
    if img is not None:
        if st.button("🚀 INICIAR ASESORÍA COMPLETA", type="primary", use_container_width=True):
            if not puede_consultar(st.session_state.user_email, st.session_state.user_tier):
                st.error("⚠️ Has alcanzado tu límite de diagnósticos por hoy.")
            else:
                with st.spinner("Analizando..."):
                    try:
                        inventario_ia = "INVENTARIO DISPONIBLE:\n"
                        for p in prods_medicina:
                            cat_nombre = p['categ_id'][1] if isinstance(p.get('categ_id'), list) and len(p['categ_id']) > 1 else "OTROS"
                            nota = str(p.get('description') or p.get('description_sale') or "Sin detalles").replace('\n', ' ').strip()
                            
                            inventario_ia += f"[{cat_nombre.upper()}] - Nombre Comercial: {p['name']} (Ingredientes/Notas: {nota})\n"

                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel('gemini-2.0-flash-lite')
                        
                        prompt = f"""
                        RESPONDE 100% EN ESPAÑOL. Eres Ing. Agrónomo y Fitopatólogo de Multiagro. 
                        Analiza la planta: {cultivo_input if cultivo_input else 'No especificado'}.
                        
                        1. DIAGNÓSTICO: Identifica la plaga, hongo, bacteria o deficiencia nutricional.
                        2. RECETA EXACTA: ESTÁS OBLIGADO a recomendar EXACTAMENTE 4 productos diferentes de la lista de abajo. 
                        REGLA VITAL: Lee atentamente los "Ingredientes/Notas" de cada producto en el inventario. Usa tu conocimiento científico para saber qué ingrediente activo de nuestra lista erradica el problema diagnosticado. Fíjate que la categoría entre corchetes coincida (ej. no recetes INSECTICIDA para un hongo).
                        
                        {inventario_ia}
                        
                        Escribe el Nombre Comercial de los 4 productos recomendados en NEGRITAS.
                        3. APLICACIÓN: Explica brevemente cómo el ingrediente activo actúa sobre el problema y da labores culturales.
                        """
                        
                        res = model.generate_content([prompt, Image.open(img)])
                        texto_ia_lower = res.text.lower()
                        sugeridos = []
                        vistos = set()
                        
                        palabras_ignoradas = ["fungicida", "insecticida", "herbicida", "fertilizante", "bactericida", "litro", "litros", "ml", "kg", "gr", "gramos", "galon", "galones", "sc", "ec", "sl", "wg", "wp", "agroquimico"]
                        
                        for p in prods_medicina:
                            nombre_limpio = p['name'].split('(')[0].strip().lower()
                            partes_nombre = nombre_limpio.split()
                            
                            palabra_clave = ""
                            for palabra in partes_nombre:
                                if palabra not in palabras_ignoradas and len(palabra) > 2:
                                    palabra_clave = palabra
                                    break
                            
                            if not palabra_clave and partes_nombre:
                                palabra_clave = partes_nombre[0]
                                
                            if palabra_clave and (palabra_clave in texto_ia_lower or nombre_limpio in texto_ia_lower):
                                if palabra_clave not in vistos:
                                    sugeridos.append(p)
                                    vistos.add(palabra_clave)
                                    
                            if len(sugeridos) >= 4: 
                                break
                        
                        st.session_state.chat_history = [
                            {"role": "user", "parts": [f"Contexto oculto: Analizaste {cultivo_input}. Debes recomendar 4 productos leyendo sus ingredientes activos: \n{inventario_ia}"]},
                            {"role": "model", "parts": [res.text]}
                        ]
                        
                        st.session_state.prods_filtrados = sugeridos
                        registrar_uso(st.session_state.user_email, st.session_state.user_tier)
                        st.rerun()
                        
                    except Exception as e:
                        if "rerun" not in str(e).lower(): 
                            st.error(f"Error: {e}")

    # =========================================================================
    # MOSTRAR EL CHAT Y LOS BOTONES
    # =========================================================================
    if st.session_state.chat_history:
        for i, msj in enumerate(st.session_state.chat_history):
            if i == 0: 
                continue 
                
            if msj["role"] == "model": 
                st.markdown(f"<div class='diag-box'>🤖 {msj['parts'][0]}</div>", unsafe_allow_html=True)
            else: 
                st.markdown(f"<div style='text-align: right; background-color: #007BFF; color: white; padding: 15px; border-radius: 20px; margin-bottom: 25px; margin-left: 15%;'>👤 <b>Tú:</b><br>{msj['parts'][0]}</div>", unsafe_allow_html=True)

        st.text_input("💬 Escribe tu duda sobre el manejo o el diagnóstico y presiona Enter:", key="input_duda", on_change=enviar_pregunta)
        st.markdown("<br>", unsafe_allow_html=True)
        
        mensaje_wa = urllib.parse.quote("Hola, acabo de usar la app AgroDiagnóstico Multiagro y necesito consultar a un técnico sobre un diagnóstico.")
        st.link_button("👨‍🌾 Consultar dudas a un técnico por WhatsApp", f"https://wa.me/18295624653?text={mensaje_wa}", type="secondary", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.prods_filtrados:
            st.markdown("<h4 style='color: #4DA3FF;'>🧪 Medicinas recomendadas para este caso:</h4>", unsafe_allow_html=True)
            cols_ia = st.columns(2) 
            
            for i, p in enumerate(st.session_state.prods_filtrados):
                with cols_ia[i % 2]:
                    img_b64 = f'<img src="data:image/png;base64,{p["image_128"]}" class="product-img">' if p.get('image_128') else ""
                    nombre_corto = p['name'].split('(')[0].strip()
                    badge = "<div class='badge-fav'>⭐ Destacado</div>" if str(p.get('priority', '0')) == '1' else ""
                    
                    st.markdown(f"<div class='product-card'>{badge}{img_b64}<h4 style='font-size: 0.85rem; margin-bottom: 5px;'>{nombre_corto}</h4></div>", unsafe_allow_html=True)
                    
                    if nombre_corto in st.session_state.carrito: 
                        st.button("✅ Agregado", key=f"rec_ok_{p['id']}", disabled=True)
                    else: 
                        st.button("➕ Agregar a Cotización", key=f"rec_{p['id']}", on_click=agregar_al_carrito, args=(nombre_corto,))

    # =========================================================================
    # CATÁLOGO E-COMMERCE (BUSCADOR SUPER POTENTE)
    # =========================================================================
    st.divider()
    st.markdown("<h2 style='text-align: center; color: #FFFFFF;'>🏪 Catálogo Multiagro</h2>", unsafe_allow_html=True)
    
    busqueda_catalogo = st.text_input("🔍 Buscar productos en el catálogo...", placeholder="Ej: Abono, Cinta, Manguera, Tomate, o Ingrediente...")
    st.markdown("<br>", unsafe_allow_html=True)

    tab_fito, tab_sem, tab_riego, tab_eq = st.tabs(["🧪 Fito & Nutrición", "🌱 Semillas", "💧 Riego", "🛠️ Equipos"])
    
    def mostrar_catalogo(lista_productos, tab_key, busqueda):
        # BUSCADOR MÁS PODEROSO: Busca en el Nombre, Notas Internas, y Categoría Literal
        if busqueda:
            q = busqueda.lower()
            lista_filtrada = [
                p for p in lista_productos 
                if q in p['name'].lower() 
                or q in str(p.get('description', '')).lower() 
                or q in str(p.get('description_sale', '')).lower()
                or (isinstance(p.get('categ_id'), list) and len(p['categ_id']) > 1 and q in p['categ_id'][1].lower())
            ]
        else:
            lista_filtrada = lista_productos
            
        if not lista_filtrada: 
            if busqueda:
                st.warning(f"No se encontraron productos relacionados con '{busqueda}' en esta pestaña.")
            else:
                st.info("No hay productos en esta categoría por el momento.")
        else:
            mostrar = lista_filtrada[:4]
            cols = st.columns(2)
            
            for i, p in enumerate(mostrar):
                with cols[i % 2]:
                    img_b64 = f'<img src="data:image/png;base64,{p["image_128"]}" class="product-img">' if p.get('image_128') else ""
                    nombre_corto = p['name'].split('(')[0].strip()
                    badge = "<div class='badge-fav'>⭐ Destacado</div>" if str(p.get('priority', '0')) == '1' else ""
                    
                    st.markdown(f"<div class='product-card'>{badge}{img_b64}<h4 style='font-size: 0.85rem; margin-bottom: 5px;'>{nombre_corto}</h4></div>", unsafe_allow_html=True)
                    
                    if nombre_corto in st.session_state.carrito: 
                        st.button("✅ Agregado", key=f"cat_ok_{tab_key}_{p['id']}", disabled=True)
                    else: 
                        st.button("➕ Agregar", key=f"cat_{tab_key}_{p['id']}", on_click=agregar_al_carrito, args=(nombre_corto,))

    with tab_fito: 
        mostrar_catalogo(prods_medicina, "fito", busqueda_catalogo)
    with tab_sem: 
        mostrar_catalogo(prods_semillas, "sem", busqueda_catalogo)
    with tab_riego: 
        mostrar_catalogo(prods_riego, "riego", busqueda_catalogo)
    with tab_eq: 
        mostrar_catalogo(prods_equipos, "eq", busqueda_catalogo)

    # =========================================================================
    # CARRITO DE WHATSAPP FLOTANTE
    # =========================================================================
    if st.session_state.carrito:
        st.markdown("<br><br><br>", unsafe_allow_html=True) 
        st.markdown('<div class="cart-box">', unsafe_allow_html=True)
        st.markdown(f"🛒 <b>Tu Cotización Actual ({len(st.session_state.carrito)} artículos)</b>", unsafe_allow_html=True)
        
        texto_ws = "Hola, estoy usando la app AgroDiagnóstico y me interesa cotizar estos productos:\n\n"
        for idx, item in enumerate(st.session_state.carrito): 
            texto_ws += f"{idx+1}. {item}\n"
            
        texto_ws += f"\nQuedo atento a disponibilidad y precios. Mi usuario es: {st.session_state.user_email}"
        mensaje_codificado = urllib.parse.quote(texto_ws)
        
        st.link_button("📲 Enviar Cotización a un Asesor", f"https://wa.me/18295624653?text={mensaje_codificado}", type="primary", use_container_width=True)
        
        if st.button("🗑️ Vaciar Carrito", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # FORMULARIO DE REGISTRO
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
    # LOGOS
    # =========================================================================
    st.divider()
    st.markdown("<h4 style='text-align: center; color: #007BFF; margin-bottom: 20px;'>Empresas Grupo Multiagro</h4>", unsafe_allow_html=True)
    
    logos_list = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
    cols1 = st.columns(3)
    cols2 = st.columns(2)
    
    for i, l_file in enumerate(logos_list[:3]):
        with cols1[i]:
            if os.path.exists(l_file):
                with open(l_file, "rb") as f: 
                    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}"></div>', unsafe_allow_html=True)
                    
    for i, l_file in enumerate(logos_list[3:]):
        with cols2[i]:
            if os.path.exists(l_file):
                with open(l_file, "rb") as f: 
                    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}"></div>', unsafe_allow_html=True)
                
    st.markdown("""
        <div style='text-align: center; color: #666666; font-size: 0.85rem; margin-top: 50px; padding-bottom: 20px;'>
            &copy; 2026 Grupo Multiagro.<br>Desarrollado con Inteligencia Artificial.
        </div>
    """, unsafe_allow_html=True)
