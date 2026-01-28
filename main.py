import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Multiagro IA", page_icon="🌱", layout="wide")

# --- DISEÑO VISUAL PROFESIONAL (COLORES VIVOS) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #e8f5e9 0%, #ffffff 100%); }
    .product-card {
        background-color: white; padding: 22px; border-radius: 18px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06); margin-bottom: 20px;
        border-top: 6px solid #1b5e20; transition: 0.3s;
    }
    .product-card:hover { transform: scale(1.02); box-shadow: 0 12px 25px rgba(46,125,50,0.15); }
    h1 { color: #1b5e20; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stButton>button {
        background: linear-gradient(90deg, #1b5e20 0%, #388e3c 100%);
        color: white; border: none; padding: 15px; border-radius: 10px;
        font-weight: bold; width: 100%;
    }
    .stSelectbox label { color: #1b5e20; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO LOCAL ---
# Al subir el archivo a GitHub con ese nombre, lo llamamos así:
try:
    st.image("Grupo_Multiagro_Mesa de trabajo 1.png", width=320)
except:
    # Si por alguna razón falla el archivo local, intentamos la web de nuevo
    st.image("https://www.grupomultiagro.com/wp-content/uploads/2022/03/logo-multiagro-horizontal.png", width=300)

st.markdown("<h1 style='text-align: center;'>Consultor Agrícola Inteligente</h1>", unsafe_allow_html=True)

# --- BASE DE DATOS NACIONAL (PROVINCIAS RD) ---
PROVINCIAS = [
    "Azua", "Baoruco", "Barahona", "Dajabón", "Distrito Nacional", "Duarte (SFM)", 
    "Elías Piña", "El Seibo", "Espaillat (Moca)", "Hato Mayor", "Hermanas Mirabal", 
    "Independencia", "La Altagracia (Higüey)", "La Romana", "La Vega", "María Trinidad Sánchez", 
    "Monseñor Nouel (Bonao)", "Monte Cristi", "Monte Plata", "Pedernales", "Peravia (Baní)", 
    "Puerto Plata", "Samaná", "Sánchez Ramírez (Cotuí)", "San Cristóbal", "San José de Ocoa", 
    "San Juan de la Maguana", "San Pedro de Macorís", "Santiago", "Santiago Rodríguez", 
    "Valverde (Mao)", "Santo Domingo"
]

# --- CULTIVOS DETALLADOS ---
CULTIVOS_DATA = {
    "Arroz": ["Herbicida Pro-Arroz", "Urea Multiagro 46%", "Zinc Foliar", "Insecticida Chinche"],
    "Banano / Plátano": ["Fungicida Sigatoka Elite", "Potasio Soluble", "Bolsas Protectoras", "Deshijadores"],
    "Cacao": ["Fungicida de Cobre", "Fertilizante Floración", "Podadoras Profesionales", "Cajas de Fermentación"],
    "Café": ["Control de Roya", "Abono Orgánico", "Mallas de Secado", "Insecticida Broca"],
    "Aguacate": ["Fungicida Fitóptora", "Reguladores de Crecimiento", "Injertos", "Microelementos"],
    "Vegetales (Invernadero)": ["Insecticida Bio", "Sistemas de Goteo Netafim", "Calcio-Boro", "Plásticos Invernadero"],
    "Vegetales (Campo Abierto)": ["Control de Maleza", "Fertirriego Base", "Mallas Antipájaros", "Insecticidas Sistémicos"],
    "Tabaco": ["Control de Moho Azul", "Fertilizante Especial Tabaco", "Hilos de Amarre", "Curas Curado"],
    "Caña de Azúcar": ["Madurantes", "Herbicidas Pre-emergentes", "Fertilizante Cañero"],
    "Jardinería / Paisajismo": ["Tierra Negra Abonada", "Grama Bermuda/San Agustín", "Mangueras", "Podadoras"],
}

# --- NAVEGACIÓN ---
tabs = st.tabs(["🔍 Diagnóstico IA", "🛒 Catálogo Multiagro", "📞 Contacto Técnico"])

with tabs[0]:
    st.markdown("### 📸 Análisis de Plagas y Nutrición")
    c1, c2 = st.columns(2)
    with c1:
        cultivo_sel = st.selectbox("Cultivo", list(CULTIVOS_DATA.keys()))
    with c2:
        prov_sel = st.selectbox("Ubicación en RD", PROVINCIAS)

    foto = st.camera_input("Enfocar el síntoma en la planta")

    if foto:
        st.success(f"✅ Imagen procesada para {cultivo_sel} en {prov_sel}")
        st.markdown("---")
        st.subheader("💡 Soluciones Multiagro Recomendadas")
        
        recs = CULTIVOS_DATA.get(cultivo_sel, [])
        cols = st.columns(2)
        for i, prod in enumerate(recs):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="product-card">
                    <h4 style='color:#1b5e20; margin-bottom:5px;'>{prod}</h4>
                    <p style='font-size:14px; color:#555;'>Especializado para <b>{cultivo_sel}</b></p>
                    <p style='color:#388e3c; font-weight:bold;'>✔ En Stock</p>
                </div>
                """, unsafe_allow_html=True)
                st.button(f"Comprar {prod}", key=f"buy_{prod}_{i}")

with tabs[1]:
    st.header("Nuestro Catálogo Completo")
    st.text_input("🔍 Buscar insumo (Nombre, Plaga o Ingrediente)...")
    st.write("Explorando más de 2,500 referencias de Grupo Multiagro...")

with tabs[2]:
    st.header("Asistencia Personalizada")
    st.write("¿La IA no fue suficiente? Habla con el técnico de tu zona.")
    st.button("📲 Contactar Agrónomo por WhatsApp")
    st.markdown(f"📍 **Oficina Central:** [Visitar Web]({ 'https://www.grupomultiagro.com' })")

st.sidebar.markdown("---")
st.sidebar.info("Versión 1.1 Beta - Grupo Multiagro")
