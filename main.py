import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Multiagro IA", page_icon="🌱", layout="wide")

# --- DISEÑO DE COLORES Y ESTILOS (VIVO) ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp {
        background: linear-gradient(to bottom, #f0f4f0, #ffffff);
    }
    /* Tarjetas de productos */
    .product-card {
        background-color: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-left: 8px solid #2e7d32;
        transition: transform 0.3s;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(46, 125, 50, 0.1);
    }
    /* Títulos y texto */
    h1 { color: #1b5e20; font-family: 'Helvetica', sans-serif; font-weight: 800; }
    h3 { color: #2e7d32; }
    /* Botones */
    .stButton>button {
        background: linear-gradient(90deg, #2e7d32 0%, #4caf50 100%);
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO CON LOGO ---
# Intentamos forzar la carga del logo desde tu web
st.image("https://www.grupomultiagro.com/wp-content/uploads/2022/03/logo-multiagro-horizontal.png", width=300)
st.markdown("<h1 style='text-align: center;'>Consultor Agrícola Inteligente</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Potenciando el campo en República Dominicana 🇩🇴</p>", unsafe_allow_html=True)

# --- BASE DE DATOS AMPLIADA (RD) ---
PROVINCIAS = [
    "La Vega", "Moca (Espaillat)", "Santiago", "Azua", "San Juan de la Maguana", 
    "Monte Cristi", "Valverde (Mao)", "Dajabón", "Duarte (SFM)", "Hermanas Mirabal",
    "Puerto Plata", "Bani (Peravia)", "Barahona", "Hato Mayor", "San Cristóbal"
]

CULTIVOS_DATA = {
    "Arroz": ["Herbicida Pro-Arroz", "Urea Multiagro 46%", "Zinc Foliar"],
    "Banano / Plátano": ["Control Sigatoka Elite", "Potasio Soluble", "Bolsas Protectoras"],
    "Cacao": ["Fungicida de Cobre", "Fertilizante Floración", "Podadoras Profesionales"],
    "Café": ["Control de Roya", "Abono Orgánico", "Mallas de Secado"],
    "Aguacate": ["Fungicida Fitóptora", "Reguladores de Crecimiento", "Injertos"],
    "Vegetales (Invernadero)": ["Insecticida Bio", "Sistemas de Goteo Netafim", "Calcio-Boro"],
    "Tabaco": ["Control de Moho Azul", "Fertilizante Especial Tabaco", "Hilos de Amarre"],
    "Jardinería": ["Tierra Negra Abonada", "Gramas", "Mangueras y Riego"]
}

# --- NAVEGACIÓN ---
menu = st.tabs(["🔍 Diagnóstico con IA", "🛒 Tienda Multiagro", "👨‍💼 Mi Asesor"])

# --- PESTAÑA 1: DIAGNÓSTICO ---
with menu[0]:
    st.markdown("### 📸 Análisis Instantáneo")
    col1, col2 = st.columns(2)
    with col1:
        cultivo_sel = st.selectbox("Seleccione su Cultivo", list(CULTIVOS_DATA.keys()))
    with col2:
        prov_sel = st.selectbox("Provincia", PROVINCIAS)

    foto = st.camera_input("Capturar síntoma de la planta")

    if foto:
        st.success("✅ Imagen recibida correctamente.")
        st.info(f"**Análisis de IA en curso para {cultivo_sel} en {prov_sel}...**")
        
        st.markdown("### 💡 Recomendación de Expertos")
        recs = CULTIVOS_DATA.get(cultivo_sel, ["Consulte con un técnico"])
        
        c_prod1, c_prod2 = st.columns(2)
        for i, prod in enumerate(recs):
            with (c_prod1 if i % 2 == 0 else c_prod2):
                st.markdown(f"""
                <div class="product-card">
                    <h4 style='margin:0;'>{prod}</h4>
                    <p style='color:#2e7d32; font-weight:bold; font-size:18px;'>Disponible</p>
                    <p style='font-size:13px; color:#777;'>Solución recomendada para {cultivo_sel}</p>
                </div>
                """, unsafe_allow_html=True)
                st.button(f"🛒 Comprar {prod}", key=f"btn_{prod}")

# --- PESTAÑA 2: TIENDA ---
with menu[1]:
    st.header("Explorar Catálogo de Insumos")
    st.text_input("Buscar por plaga, cultivo o producto...", placeholder="Ej: Control de maleza en arroz")
    
    st.markdown("#### Categorías Principales")
    st.columns(4)[0].button("Nutrición")
    st.columns(4)[1].button("Protección")
    st.columns(4)[2].button("Riego")
    st.columns(4)[3].button("Semillas")

# --- PESTAÑA 3: ASESOR ---
with menu[2]:
    st.header("Contacto Directo")
    st.write("¿Prefieres hablar con un técnico de tu zona?")
    st.button("📲 Contactar por WhatsApp")
    st.button("📞 Llamar a Oficina Central")

st.sidebar.markdown("---")
st.sidebar.write(f"🌐 [Web Oficial Grupo Multiagro](https://www.grupomultiagro.com)")
