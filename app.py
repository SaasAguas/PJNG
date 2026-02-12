import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import time

# ==========================================
# 1. CONFIGURACIÓN Y DATOS REALES (ORDENADOS A-Z)
# ==========================================
st.set_page_config(page_title="La Jalisciense POS", page_icon="🥤", layout="centered")
TZ_CDMX = pytz.timezone('America/Mexico_City')

# --- LISTAS ORDENADAS ALFABÉTICAMENTE ---
SABORES_FRUTA = sorted([
    "Ciruela",
    "Fresa",
    "Fresa-Hierbabuena",
    "Guayaba",
    "Guayaba-Fresa",
    "Guayaba-Hierbabuena",
    "Hierbabuena-Limon",
    "Jamaica",
    "Lima",
    "Lima-Albahaca",
    "Lima-Stevia",
    "Limon Con Pepino Y Hierbabuena",
    "Limon-Chia",
    "Limón-Alfalfa",
    "Limón-Hierbabuena",
    "Mango",
    "Maracuya",
    "Melon",
    "Melon Citrico",
    "Piña Naranja Hierbabuena",
    "Piña-Alfalfa",
    "Piña-Hierbabuena",
    "Piña-Naranja"
])

SABORES_CREMA = sorted([
    "Cebada",
    "Chai",
    "Coco Con Nuez",
    "Crema Irlandesa",
    "Horchata Arroz",
    "Horchata De Fresa",
    "Kalhua",
    "Mazapan",
    "Taro",
    "Vainilla"
])

# Diccionario de Precios Fijos (Ordenaremos las llaves al crear el DF)
PRODUCTOS_EXTRA = {
    "Campana": 20,
    "Frapuchino": 10,
    "Fresas Con Crema": 25,
    "Paleta De Agua": 25,
    "Paleta De Leche": 30,
    "Sandwich": 20
}

# Construcción del DataFrame Inicial
datos = []
# 1. Frutas (Precio Variable)
for s in SABORES_FRUTA: 
    datos.append({"Sabor": s, "Categoría": "Fruta", "Stock": 50, "PrecioFijo": 0})
# 2. Cremas (Precio Variable)
for s in SABORES_CREMA: 
    datos.append({"Sabor": s, "Categoría": "Crema", "Stock": 50, "PrecioFijo": 0})
# 3. Paletas/Extras (Precio Fijo) - Ordenamos también aquí
for p in sorted(PRODUCTOS_EXTRA.keys()): 
    datos.append({"Sabor": p, "Categoría": "Paletas", "Stock": 20, "PrecioFijo": PRODUCTOS_EXTRA[p]})

CATALOGO_INICIAL = pd.DataFrame(datos)

# ==========================================
# 2. ESTILOS CSS (LIMPIO Y MODERNO)
# ==========================================
st.markdown("""
    <style>
    /* Forzar modo claro y fondo limpio */
    .stApp {
        background-color: #F8F5FA;
        color: #333;
    }
    h1 { color: #C2185B; font-weight: 900; text-align: center; margin-bottom: 0px; }
    
    /* Estilo de los Botones Grandes de Categoría */
    div.stButton > button[kind="secondary"] {
        background-color: white;
        color: #C2185B;
        border: 2px solid #C2185B;
        border-radius: 12px;
        height: 3.5em;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.2s;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #FCE4EC;
        border-color: #C2185B;
    }
    /* Estilo para botón activo (Simulado) */
    div.stButton > button[kind="secondary"]:focus {
         background-color: #C2185B;
         color: white;
    }

    /* Botón de Acción Principal (Cobrar/Agregar) */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #C2185B, #880E4F);
        color: white; border: none; border-radius: 12px;
        font-weight: 700; padding: 0.6rem 1rem; height: 3em;
    }

    /* Etiquetas y textos */
    .big-label { font-size: 1rem; font-weight: 700; color: #555; margin-bottom: -5px; display: block;}
    .stock-warning { color: #D32F2F; font-weight: bold; font-size: 0.9rem; }
    .stock-ok { color: #388E3C; font-weight: bold; font-size: 0.9rem; }

    /* Tarjetas de Carrito */
    .cart-item {
        background: white; padding: 12px; border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 8px;
        border-left: 5px solid #C2185B; display: flex; justify-content: space-between; align-items: center;
    }
    .cart-title { font-weight: 700; font-size: 1rem; }
    .cart-price { font-weight: 900; font-size: 1.2rem; color: #C2185B; }
    
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. GESTIÓN DEL ESTADO
# ==========================================
def init_session():
    if 'inventario' not in st.session_state:
        st.session_state.inventario = CATALOGO_INICIAL.copy()
    if 'carrito' not in st.session_state:
        st.session_state.carrito = []
    if 'caja' not in st.session_state:
        st.session_state.caja = {'dinero': 0.0, 'items': 0}
    if 'transacciones' not in st.session_state:
        st.session_state.transacciones = []
    if 'cat_activa' not in st.session_state:
        st.session_state.cat_activa = "Fruta" # Categoría inicial

init_session()

# ==========================================
# 4. INTERFAZ
# ==========================================
st.write("<h1>La Jalisciense <span style='font-size:1rem; color: #BDBDBD'>| POS</span></h1>", unsafe_allow_html=True)
tabs = st.tabs(["🛒 VENTA", "🏗️ PRODUCCIÓN", "📊 REPORTES"])

# --- TAB 1: VENTA ---
with tabs[0]:
    # 1. BOTONES GRANDES DE CATEGORÍA
    c1, c2, c3 = st.columns(3)
