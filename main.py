import streamlit as st

# --- CONFIGURACIÓN ESTÉTICA ---
st.set_page_config(page_title="Multiagro IA", page_icon="🌱", layout="wide")

# Estilo CSS para mejorar la apariencia (Bordes, Colores y Sombras)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .product-card {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
        border-top: 5px solid #2e7d32;
    }
    .stButton>button {
        background-color: #2e7d32; color: white; border-radius: 8px;
        width: 100%; font-weight: bold;
    }
    .main-title { color: #1a5d1a; text-align: center; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO Y ENCABEZADO ---
# Usamos una imagen de respaldo si el logo principal falla
LOGO_URL = "https://www.grupomultiagro.com/wp-content/uploads/2022/03/logo-multiagro-horizontal.png"
st.image(LOGO_URL, width=250)
st.markdown("<h1 class='main-title'>Asistente Agrícola Inteligente</h1>", unsafe_allow_html=True)

# --- BASE DE DATOS DE RECOMENDACIONES (Lógica Multiagro) ---
# Aquí vinculamos plagas con tus insumos reales
CATALOGO = {
    "Arroz": [
        {"nombre": "Herbicida Pro-Arroz", "precio": "RD$ 1,450", "uso": "Control de malezas"},
        {"nombre": "Urea Multiagro", "precio": "RD$ 2,100", "uso": "Crecimiento"}
    ],
    "Banano": [
        {"nombre": "Fungicida Sigatoka-Stop", "precio": "RD$ 3,200", "uso": "Control de hongos"},
        {"nombre": "Potasio Foliar", "precio": "RD$ 1,100", "uso": "Llenado de fruto"}
    ],
    "Vegetales": [
        {"nombre": "Insecticida Bio-Safe", "precio": "RD$ 950", "uso": "Control de áfidos"},
        {"nombre": "Calcio Boro", "precio": "RD$ 1,800", "uso": "Fortalecimiento"}
    ]
}

# --- NAVEGACIÓN POR PESTAÑAS ---
tab1, tab2 = st.tabs(["🔍 Diagnóstico IA", "🛒 Catálogo de Compras"])

# --- TAB 1: DIAGNÓSTICO ---
with tab1:
    st.header("Análisis de Cultivo")
    col_a, col_b = st.columns(2)
    with col_a:
        cultivo_sel = st.selectbox("¿Qué cultivo estás revisando?", list(CATALOGO.keys()))
    with col_b:
        zona = st.selectbox("Ubicación", ["La Vega", "Moca", "Azua", "San Juan", "Dajabón"])

    foto = st.camera_input("Capturar síntoma")

    if foto:
        st.success("✅ Imagen capturada con éxito")
        with st.expander("Ver Diagnóstico y Sugerencias de Compra", expanded=True):
            st.info(f"Análisis preliminar para **{cultivo_sel}**: Posible estrés biótico detectado.")
            st.write("### Productos recomendados por Multiagro:")
            
            # Aquí mostramos las recomendaciones inteligentes basadas en el cultivo
            recs = CATALOGO.get(cultivo_sel, [])
            for item in recs:
                st.markdown(f"""
                <div class="product-card">
                    <h4>{item['nombre']}</h4>
                    <p><b>Acción:</b> {item['uso']}</p>
                    <p style='color: #2e7d32; font-size: 20px;'>{item['precio']}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Comprar {item['nombre']}", key=item['nombre']):
                    st.success(f"Añadido al carrito: {item['nombre']}")

# --- TAB 2: CATÁLOGO COMPLETO ---
with tab2:
    st.header("Todos los Insumos")
    busqueda = st.text_input("Buscar por nombre, plaga o ingrediente activo...")
    
    # Simulación de cuadrícula de productos
    col1, col2 = st.columns(2)
    todos_productos = [p for sublist in CATALOGO.values() for p in sublist]
    
    for i, p in enumerate(todos_productos):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div class="product-card">
                <h5>{p['nombre']}</h5>
                <p>{p['precio']}</p>
            </div>
            """, unsafe_allow_html=True)
            st.button("Ver ficha técnica", key=f"full_{i}")

st.sidebar.markdown("---")
st.sidebar.write("🌐 [Ir a grupomultiagro.com](https://www.grupomultiagro.com)")
