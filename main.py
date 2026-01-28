def traer_datos_odoo():
    try:
        url = st.secrets["ODOO_URL"]
        db = st.secrets["ODOO_DB"]
        user = st.secrets["ODOO_USER"]
        key = st.secrets["ODOO_API_KEY"]
        
        # 1. Intentar Autenticación
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, user, key, {})
        
        if not uid:
            return "ERROR_AUTH" # Usuario o Clave API mal puestos
        
        # 2. Intentar lectura de productos
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        ids = models.execute_kw(db, uid, key, 'product.template', 'search', 
                               [[['sale_ok', '=', True]]], {'limit': 4})
        
        prods = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price']})
        return [(p['name'], f"RD$ {p['list_price']:,.2f}") for p in prods]
    except Exception as e:
        return f"ERROR_TECNICO: {str(e)}"

# --- LÓGICA DE VISUALIZACIÓN ---
resultado = traer_datos_odoo()

if resultado == "ERROR_AUTH":
    st.error("❌ Error de Autenticación: El usuario o la API Key no son correctos.")
elif isinstance(resultado, str) and "ERROR_TECNICO" in resultado:
    st.warning(f"⚠️ Error de Conexión: Verifique que la URL '{st.secrets['ODOO_URL']}' y la DB '{st.secrets['ODOO_DB']}' sean correctas.")
    st.caption(f"Detalle: {resultado}")
elif resultado:
    # Mostrar productos (igual que el código anterior)
    cols = st.columns(len(resultado))
    for i, (nombre, precio) in enumerate(resultado):
        with cols[i]:
            st.info(f"**{nombre}**\n\n{precio}")
            st.markdown(f"[💬 WhatsApp](https://wa.me/18095551234?text=Info:{nombre})")
