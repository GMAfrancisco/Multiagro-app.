import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Multiagro IA", page_icon="🌱", layout="wide")

# --- CONEXIÓN CON EL CEREBRO IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ Error de configuración: Verifique la API Key en Secrets.")

# --- DISEÑO VIVO (CSS) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #e8f5e9 0%, #ffffff 100%); }
    .product-card {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 15px;
        border-left: 6px solid #1b5e20;
    }
    h1 { color: #1b5e20; font-weight: 800; text-align: center; }
    .stButton>button {
        background: linear-gradient(90deg, #1b5e20 0%, #388e3c 100%);
        color: white; border-radius: 10px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO Y ENCABEZADO ---
try:
    st.image("Grupo_Multiagro_Mesa de trabajo 1.png", width=320)
except:
    st.image("https://www.grupomultiagro.com/wp-content/uploads/2022/03/logo-multiagro-horizontal.png", width=300)

st.markdown("<h1>Consultor Agrícola Inteligente</h1>", unsafe_allow_html=True)

# --- DATOS COMPLETOS RD ---
PROVINCIAS = [
    "Azua", "Baoruco", "Barahona", "Dajabón", "Distrito Nacional", "Duarte (SFM)", 
    "Elías Piña", "El Seibo", "Espaillat (Moca)", "Hato Mayor", "Hermanas Mirabal", 
    "Independencia", "La Altagracia (Higüey)", "La Romana", "La Vega", "María Trinidad Sánchez", 
    "Monseñor Nouel (Bonao)", "Monte Cristi", "Monte Plata", "Pedernales", "Peravia (Baní)", 
    "Puerto Plata", "Samaná", "Sánchez Ramírez (Cotuí)", "San Cristóbal", "San José de Ocoa", 
    "San Juan de la Maguana", "San Pedro de Macorís", "Santiago", "Santiago Rodríguez", 
    "Valverde (Mao)", "Santo Domingo"
]

CULTIVOS_DATA = {
    "Arroz": ["Herbicida Pro-Arroz", "Urea Multiagro 46%", "Zinc Foliar", "Insecticida Chinche"],
    "Banano / Plátano": ["Fungicida Sigatoka Elite", "Potasio Soluble", "Bolsas Protectoras"],
    "Cacao": ["Fungicida de Cobre", "Fertilizante Floración", "Podadoras Profesionales"],
    "Café": ["Control de Roya", "Abono Orgánico", "Insecticida Broca"],
    "Aguacate": ["Fungicida Fitóptora", "Reguladores de Crecimiento", "Microelementos"],
    "Vegetales (Invernadero)": ["Insecticida Bio", "Sistemas de Goteo Netafim", "Trampas Amarillas"],
    "Vegetales (Campo Abierto)": ["Control de Maleza", "Fertirriego Base", "Insecticidas Sistémicos"],
    "Tabaco": ["Control de Moho Azul", "Fertilizante Especial Tabaco", "Hilos de Amarre"],
    "Caña de Azúcar": ["Madurantes", "Herbicidas Pre-emergentes", "Fertilizante Cañero"],
    "Jardinería / Paisajismo": ["Tierra Negra Abonada", "Grama Bermuda", "Podadoras"]
}

# --- NAVEGACIÓN ---
tabs = st.tabs(["🔍 Diagnóstico IA", "🛒 Catálogo Multiagro", "📞 Asistencia"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        cultivo_sel = st.selectbox("Cultivo", list(CULTIVOS_DATA.keys()))
    with c2:
        prov_sel = st.selectbox("Provincia", PROVINCIAS)

    foto = st.camera_input("Capturar síntoma en la planta")

    if foto:
        img = Image.open(foto)
        st.image(img, width=400, caption="Imagen para análisis")
        
        with st.spinner("🧠 Analizando con IA de Multiagro..."):
            try:
                prompt = f"Actúa como agrónomo experto de Multiagro en RD. Analiza esta foto de {cultivo_sel} en {prov_sel}. Identifica la plaga o deficiencia y da una solución técnica corta."
                response = model.generate_content([prompt, img])
                
                st.markdown("### 📋 Diagnóstico Sugerido")
                st.write(response.text)
                
                st.markdown("---")
                st.subheader(f"🛒 Recomendados para {cultivo_sel}")
                recs = CULTIVOS_DATA.get(cultivo_sel, [])
                cols = st.columns(2)
                for i, prod in enumerate(recs):
                    with cols[i % 2]:
                        st.markdown(f"<div class='product-card'><b>{prod}</b><br><small>Disponible en Almacén</small></div>", unsafe_allow_html=True)
                        st.button(f"Comprar {prod}", key=f"btn_{prod}_{i}")
            except Exception as e:
                st.error("Error al procesar la IA. Verifique su API Key.")

with tabs[1]:
    st.header("Catálogo de Productos")
    st.text_input("🔍 Buscar entre las 2,500 referencias...")
    st.info("Sincronizando con Odoo 17 Enterprise...")

with tabs[2]:
    st.header("Contacto Técnico")
    st.write(f"Conectando con expertos en {prov_sel}...")
    st.button("📲 Iniciar Chat con Agrónomo")

st.sidebar.write(f"📍 Zona: {prov_sel}")
st.sidebar.write("© 2026 Grupo Multiagro")
