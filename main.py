import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Multiagro App", layout="wide")

# --- 2. CONFIGURACIÓN IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except:
    st.error("Error en API Key.")

# --- 3. ESTILOS (RESTAURADOS) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAF8; }
    .product-card {
        background: white; padding: 20px; border-radius: 15px;
        text-align: center; border-top: 5px solid #1B5E20;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DEPURADOR DE ARCHIVOS (ESTO NOS DIRÁ LA VERDAD) ---
# Solo tú y yo veremos esto para arreglar los nombres
archivos_en_servidor = os.listdir(".")
st.sidebar.write("### 📂 Archivos detectados en el servidor:")
st.sidebar.write(archivos_en_servidor)

def mostrar_logo(nombre_buscado):
    # Buscamos el archivo ignorando mayúsculas/minúsculas
    for f in archivos_en_servidor:
        if f.lower() == nombre_buscado.lower():
            return st.image(f, use_container_width=True)
    return st.caption(f"❌ No hallado: {nombre_buscado}")

# --- 5. CABECERA ---
st.markdown("<h1 style='text-align:center; color:#1B5E20;'>GRUPO MULTIAGRO</h1>", unsafe_allow_html=True)
c_head1, c_head2, c_head3 = st.columns([1, 2, 1])
with c_head2:
    mostrar_logo("Grupo_Multiagro_Mesa de trabajo 1.png")

# --- 6. DIAGNÓSTICO ---
st.divider()
col_a, col_b = st.columns(2)
with col_a:
    cultivo = st.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
with col_b:
    opcion = st.radio("Método:", ["Subir Foto", "Usar Cámara"], horizontal=True)

img_input = None
if opcion == "Usar Cámara":
    img_input = st.camera_input("Capturar")
else:
    img_input = st.file_uploader("Galería", type=['jpg', 'png', 'jpeg'])

if img_input:
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Analizando..."):
            try:
                pil_img = Image.open(img_input)
                prompt = f"Como agrónomo en RD, analiza este {cultivo} e identifica plagas."
                res = model.generate_content([prompt, pil_img])
                st.success("Diagnóstico completado")
                st.write(res.text)
            except Exception as e:
                st.error(f"Error: {e}")

# --- 7. PRODUCTOS ---
st.divider()
items = [
    {"n": "Fungicida Elite", "p": "RD$ 2,800"},
    {"n": "Bio-Estimulante", "p": "RD$ 3,450"},
    {"n": "Herbicida Total", "p": "RD$ 1,200"},
    {"n": "Potasio Soluble", "p": "RD$ 1,950"}
]
p_cols = st.columns(4)
for i, item in enumerate(items):
    with p_cols[i]:
        st.markdown(f"<div class='product-card'><b>{item['n']}</b><br><small>{item['p']}</small></div>", unsafe_allow_html=True)
        txt_wa = urllib.parse.quote(
