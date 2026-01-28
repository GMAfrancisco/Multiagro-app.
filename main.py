import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Multiagro IA", page_icon="🌱", layout="wide")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # CAMBIO CLAVE: Usamos la versión estable del modelo
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except:
    st.error("⚠️ Configure su API Key en los Secrets de Streamlit.")

# --- DISEÑO ---
st.markdown("<style>.stApp { background: #f0f4f0; } .product-card { background: white; padding: 15px; border-radius: 12px; border-left: 5px solid #1b5e20; margin-bottom: 10px; }</style>", unsafe_allow_html=True)

try:
    st.image("Grupo_Multiagro_Mesa de trabajo 1.png", width=320)
except:
    st.image("https://www.grupomultiagro.com/wp-content/uploads/2022/03/logo-multiagro-horizontal.png", width=300)

# --- DATOS ---
PROVINCIAS = ["Azua", "Baoruco", "Barahona", "Dajabón", "Duarte", "Elías Piña", "El Seibo", "Espaillat", "Hato Mayor", "Hermanas Mirabal", "Independencia", "La Altagracia", "La Romana", "La Vega", "María Trinidad Sánchez", "Monseñor Nouel", "Monte Cristi", "Monte Plata", "Pedernales", "Peravia", "Puerto Plata", "Samaná", "Sánchez Ramírez", "San Cristóbal", "San José de Ocoa", "San Juan", "San Pedro de Macorís", "Santiago", "Santiago Rodríguez", "Valverde", "Santo Domingo"]
CULTIVOS_DATA = {
    "Arroz": ["Urea Multiagro", "Pro-Arroz", "Zinc Foliar"],
    "Vegetales (Campo Abierto)": ["Bio-Safe", "Fertirriego Base", "Calcio-Boro"],
    "Vegetales (Invernadero)": ["Plástico Térmico", "Goteo Netafim", "Trampas Amarillas"],
    "Banano / Plátano": ["Sigatoka Elite", "Potasio Soluble"],
    "Cacao": ["Fungicida Cobre", "Fertilizante Floración"],
    "Café": ["Control Roya", "Abono Orgánico"]
}

# --- INTERFAZ ---
tab1, tab2 = st.tabs(["🔍 Diagnóstico IA", "🛒 Catálogo"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        cultivo_sel = st.selectbox("Cultivo", list(CULTIVOS_DATA.keys()))
    with c2:
        prov_sel = st.selectbox("Provincia", PROVINCIAS)

    st.markdown("### 📸 Imagen del Problema")
    f_cam = st.camera_input("Tomar foto")
    f_gal = st.file_uploader("O subir de la galería", type=["jpg", "jpeg", "png"])

    img_file = f_cam if f_cam is not None else f_gal

    if img_file is not None:
        img_view = Image.open(img_file)
        st.image(img_view, width=350, caption="Imagen seleccionada")
        
        if st.button("🚀 ANALIZAR CON IA MULTIAGRO"):
            with st.spinner("Analizando cultivo..."):
                try:
                    # Instrucción clara para la IA
                    prompt = f"Como agrónomo experto de Multiagro en RD, identifica el problema en este cultivo de {cultivo_sel} en {prov_sel} y sugiere una solución."
                    
                    # Llamada corregida
                    response = model.generate_content([prompt, img_view])
                    
                    st.markdown("### 📋 Diagnóstico Sugerido")
                    st.write(response.text)
                    
                    st.markdown("---")
                    st.subheader("🛒 Productos Multiagro")
                    for p in CULTIVOS_DATA.get(cultivo_sel, []):
                        st.markdown(f"<div class='product-card'><b>{p}</b></div>", unsafe_allow_html=True)
                        msg = urllib.parse.quote(f"Hola Multiagro, mi {cultivo_sel} tiene un problema. La IA sugirió: {response.text[:60]}... Me interesa: {p}")
                        st.markdown(f"[💬 Consultar por WhatsApp](https://wa.me/1809XXXXXXX?text={msg})")
                except Exception as e:
                    st.error(f"Error en el motor de IA: {e}")

with tab2:
    st.header("Catálogo")
    st.write("Sincronizando con Odoo 17...")
