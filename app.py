import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import time

# ==========================================
# 1. CONFIGURACIÓN Y DATOS
# ==========================================
st.set_page_config(page_title="La Jalisciense POS", page_icon="🥤", layout="centered")
TZ_CDMX = pytz.timezone('America/Mexico_City')

# --- LISTAS EXACTAS PROPORCIONADAS ---
FRUTAS = [
    "Jamaica", "Maracuya", "Ciruela", "Lima", "Fresa-Hierbabuena", "Fresa", 
    "Guayaba-Hierbabuena", "Guayaba-Fresa", "Piña-Alfalfa", "Guayaba", 
    "Lima-Albahaca", "Melon", "Hierbabuena-Limon", "Mango", "Limón-Alfalfa", 
    "Piña-Naranja", "Limón-Hierbabuena", "Piña-Hierbabuena", "Limon-Chia", 
    "Limon Con Pepino Y Hierbabuena", "Piña Naranja Hierbabuena", 
    "Melon Citrico", "Lima-Stevia"
]

CREMAS = [
    "Horchata De Fresa", "Horchata Arroz", "Vainilla", "Mazapan", "Chai", 
    "Taro", "Coco Con Nuez", "Cebada", "Kalhua", "Crema Irlandesa"
]

# Diccionario con precios fijos
PALETAS_EXTRAS = {
    "Paleta De Agua": 25,
    "Paleta De Leche": 30,
    "Sandwich": 20,
    "Campana": 20,
    "Frapuchino": 10,
    "Fresas Con Crema": 25
}

# Crear DataFrame Maestro
data = []
for f in FRUTAS: data.append({"Sabor": f, "Categoría": "Fruta", "Stock": 50, "Precio": 0}) # Precio 0 = variable
for c in CREMAS: data.append({"Sabor": c, "Categoría": "Crema", "Stock": 50, "Precio": 0})
for p, costo in PALETAS_EXTRAS.items(): data.append({"Sabor": p, "Categoría": "Paletas", "Stock": 20, "Precio": costo})

CATALOGO_INICIAL = pd.DataFrame(data)

# ==========================================
# 2. ESTILOS VISUALES (FIX MODO OSCURO)
# ==========================================
st.markdown("""
    <style>
    /* 1. FORZAR MODO CLARO Y FONDO LAVANDA */
    [data-testid="stAppViewContainer"] {
        background-color: #E6E6FA;
        background-image: radial-gradient(#D1C4E9 20%, transparent 20%), radial-gradient(#D1C4E9 20%, transparent 20%);
        background-position: 0 0, 10px 10px;
        background-size: 20px 20px;
        color: #000000;
    }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
    [data-testid="stSidebar"] { background-color: #F3E5F5; }
    
    /* Textos siempre oscuros */
    h1, h2, h3, p, div, label, span { color: #4A148C !important; }
    
    /* 2. BOTONES DE CATEGORÍA GRANDES */
    .stButton button {
        height: 70px;
        width: 100%;
        border-radius: 15px;
        border: 2px solid #7B1FA2;
        background-color: #FFFFFF;
        color: #7B1FA2 !important;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 4px 0 #7B1FA2;
        transition: all 0.1s;
    }
    .stButton button:active {
        transform: translateY(4px);
        box-shadow: none;
    }
    .stButton button:hover {
        background-color: #F3E5F5;
        border-color: #4A148C;
        color: #4A148C !important;
    }

    /* 3. BOTÓN DE COBRAR (ESTILO DIFERENTE) */
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"] {
        background: linear-gradient(45deg, #8E24AA, #4A148C) !important;
        color: white !important;
        border: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    /* 4. TARJETAS DE PRODUCTO (CARRITO) */
    .ticket-card {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        border-left: 5px solid #7B1FA2;
        margin-bottom: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Ajustes generales */
    .block-container { padding-top: 1rem; }
    div[data-testid="stMetricValue"] { color: #4A148C !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE SESIÓN
# ==========================================
def init_session():
    if 'inventario' not in st.session_state:
        st.session_state.inventario = CATALOGO_INICIAL.copy()
    if 'carrito' not in st.session_state:
        st.session_state.carrito = []
    if 'transacciones' not in st.session_state:
        st.session_state.transacciones = []
    if 'caja' not in st.session_state:
        st.session_state.caja = {'dinero': 0.0, 'items': 0}
    if 'cat_activa' not in st.session_state:
        st.session_state.cat_activa = "Fruta" # Por defecto
    if 'seguridad_cierre' not in st.session_state:
        st.session_state.seguridad_cierre = False

init_session()

# ==========================================
# 4. INTERFAZ
# ==========================================
st.write("<h1>🍇 La Jalisciense</h1>", unsafe_allow_html=True)

tabs = st.tabs(["🛒 VENTA", "🏗️ PRODUCCIÓN", "📊 CORTE"])

# --- TAB 1: PUNTO DE VENTA ---
with tabs[0]:
    # BOTONES GRANDES DE CATEGORÍA
    c1, c2, c3 = st.columns(3)
    if c1.button("🍉 FRUTA"): st.session_state.cat_activa = "Fruta"
    if c2.button("🥛 CREMA"): st.session_state.cat_activa = "Crema"
    if c3.button("🍭 PALETAS"): st.session_state.cat_activa = "Paletas"
    
    st.markdown(f"<h3 style='text-align:center; margin-top:0;'>Sección: {st.session_state.cat_activa}</h3>", unsafe_allow_html=True)

    # AREA DE SELECCIÓN
    col_sel, col_opt = st.columns([1.5, 1])
    
    with col_sel:
        # Filtrar sabores
        df_view = st.session_state.inventario[st.session_state.inventario['Categoría'] == st.session_state.cat_activa]
        sabor = st.selectbox("Elegir Producto:", df_view['
