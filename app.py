import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import time

# ==========================================
# 1. CONFIGURACIÓN Y DATOS REALES
# ==========================================
st.set_page_config(page_title="La Jalisciense POS", page_icon="🍇", layout="centered")
TZ_CDMX = pytz.timezone('America/Mexico_City')

# --- LISTAS DE SABORES REALES ---
SABORES_FRUTA = [
    "Jamaica", "Maracuya", "Ciruela", "Lima", "Fresa-Hierbabuena", "Fresa", 
    "Guayaba-Hierbabuena", "Guayaba-Fresa", "Piña-Alfalfa", "Guayaba", 
    "Lima-Albahaca", "Melon", "Hierbabuena-Limon", "Mango", "Limón-Alfalfa", 
    "Piña-Naranja", "Limón-Hierbabuena", "Piña-Hierbabuena", "Limon-Chia", 
    "Limon Con Pepino Y Hierbabuena", "Piña Naranja Hierbabuena", 
    "Melon Citrico", "Lima-Stevia"
]

SABORES_CREMA = [
    "Horchata De Fresa", "Horchata Arroz", "Vainilla", "Mazapan", "Chai", 
    "Taro", "Coco Con Nuez", "Cebada", "Kalhua", "Crema Irlandesa"
]

PRODUCTOS_EXTRA = {
    "Paleta De Agua": 25,
    "Paleta De Leche": 30,
    "Sandwich": 20,
    "Campana": 20,
    "Frapuchino": 10,
    "Fresas Con Crema": 25
}

# Construimos el DataFrame Inicial
datos_lista = []
for s in SABORES_FRUTA: datos_lista.append({"Sabor": s, "Categoría": "Fruta", "Stock": 50, "Precio": 0})
for s in SABORES_CREMA: datos_lista.append({"Sabor": s, "Categoría": "Crema", "Stock": 50, "Precio": 0})
for p, precio in PRODUCTOS_EXTRA.items(): datos_lista.append({"Sabor": p, "Categoría": "Extras", "Stock": 20, "Precio": precio})

CATALOGO_INICIAL = pd.DataFrame(datos_lista)

# ==========================================
# 2. ESTILOS LAVENDER & ANTI-DARK MODE
# ==========================================
st.markdown("""
    <style>
    /* FORZAR TEMA CLARO (Anti-Dark Mode) */
    :root {
        --primary-color: #7B1FA2;
        --background-color: #E6E6FA;
        --secondary-background-color: #F3E5F5;
        --text-color: #2c0e3a;
        --font: "Segoe UI", sans-serif;
    }
    
    /* Fondo Lavanda con Burbujas (CSS Puro) */
    .stApp {
        background-color: #E6E6FA;
        background-image: radial-gradient(#D1C4E9 20%, transparent 20%),
                          radial-gradient(#D1C4E9 20%, transparent 20%);
        background-position: 0 0, 50px 50px;
        background-size: 100px 100px;
        color: #2c0e3a !important;
    }

    /* Títulos */
    h1 { color: #4A148C !important; font-weight: 900; text-align: center; text-shadow: 2px 2px 0px #FFF; }
    h3 { color: #6A1B9A !important; font-weight: 700; }
    
    /* BOTONES DE CATEGORÍA (Grandes) */
    .stButton button {
        background: white !important;
        border: 2px solid #7B1FA2 !important;
        color: #7B1FA2 !important;
        font-size: 1.2rem !important;
        height: 80px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 0px #7B1FA2 !important;
        transition: all 0.1s;
    }
    .stButton button:active {
        transform: translateY(4px) !important;
        box-shadow: 0 0px 0px #7B1FA2 !important;
    }
    
    /* BOTÓN DE COBRAR (Diferente) */
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"] {
        background: linear-gradient(135deg, #8E24AA, #4A148C) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
    }

    /* Textos y Etiquetas */
    .big-label { font-size: 1.2rem; font-weight: 800; color: #4A148C; margin-bottom: -10px;}
    div[data-testid="stMetricValue"] { color: #4A148C !important; }
    
    /* Tarjetas de Producto */
    .product-card {
        background: white; padding: 10px; border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 8px;
        border-left: 6px solid #8E24AA;
    }
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
    if 'categoria_activa' not in st.session_state:
        st.session_state.categoria_activa = "Fruta" # Default

init_session()

# ==========================================
# 4. INTERFAZ VISUAL
# ==========================================
st.write("<h1>🍇 La Jalisciense</h1>", unsafe_allow_html=True)

tabs = st.tabs(["🛒 VENTA", "🏗️ PRODUCCIÓN", "📊 CAJA"])

# --- TAB 1: PUNTO DE VENTA ---
with tabs[0]:
    # 1. BOTONES DE CATEGORÍA GIGANTES
    c1, c2, c3 = st.columns(3)
    if c1.button("🍉\nFrutas"): st.session_state.categoria_activa = "Fruta"
    if c2.button("🥛\nCremas"): st.session_state.categoria_activa = "Crema"
    if c3.button("🍪\nExtras"): st.session_state.categoria_activa = "Extras"

    st.markdown(f"### Mostrando: {st.session_state.categoria_activa}")

    # 2. SELECCIÓN DE PRODUCTO
    col_sel, col_detalles = st.columns([1.5, 1])
    
    with col_sel:
        # Filtramos la lista según el botón presionado
        df_filtro = st.session_state.inventario[st.session_state.inventario['Categoría'] == st.session_state.categoria_activa]
        sabor_sel = st.selectbox("Selecciona Producto:", df_filtro['Sabor'])
        
        # Info del producto seleccionado
        info_prod = df_filtro[df_filtro['Sabor'] == sabor_sel].iloc[0]
        st.caption(f"Stock disponible: {info_prod['Stock']}")

    with col_detalles:
        # Lógica de Precios Automática
        if st.session_state.categoria_activa == "Extras":
            # Si es extra, el precio es fijo (sacado de la lista)
            precio_fijo = info_prod['Precio']
            precio_final = st.number_input("Precio:", value=precio_fijo, disabled=True)
            cantidad = st.number_input("Cant:", min_value=1, value=1)
            medida = "Pza"
        else:
            # Si es agua, el precio es variable
            cantidad = st.number_input("Litros:", min_value=1, value=1)
            precio_final = st.selectbox("Precio/Lt:", [20, 16, 15])
            medida = "Lt"

    # Botón Agregar
    if st.button("➕ AGREGAR AL CARRITO", use_container_width=True):
        st.session_state.carrito.append({
            "Producto": sabor_sel, 
            "Cant": cantidad, 
            "Medida": medida,
            "Total": cantidad * precio_final
        })
        st.toast(f"✅ {sabor_sel} agregado")

    # 3. CARRITO DE COMPRAS (Visual)
    st.markdown("---")
    if st.session_state.carrito:
        st.markdown("### 🧾 Tu Pedido")
        total_acumulado = 0
        
        for item in st.session_state.carrito:
            total_acumulado += item['Total']
            st.markdown(f"""
            <div class="product-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-weight:bold; font-size:1.1rem;">{item['Producto']}</div>
                        <div style="color:#666;">{item['Cant']} {item['Medida']}</div>
                    </div>
                    <div style="font-size:1.3rem; font-weight:900; color:#4A148C;">${item['Total']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        col_total, col_cobrar = st.columns([1, 2])
        col_total.metric("TOTAL", f"${total_acumulado}")
        
        if col_cobrar.button("✅ COBRAR AHORA", type="primary", use_container_width=True):
            # Aquí actualizamos el inventario local
            for item in st.session_state.carrito:
                idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == item['Producto']].index[0]
                st.session_state.inventario.at[idx, 'Stock'] -= item['Cant']
                st.session_state.caja['dinero'] += item['Total']
                st.session_state.caja['items'] += item['Cant']
            
            st.session_state.carrito = []
            st.balloons()
            st.success("¡Cobrado!")
            time.sleep(1)
            st.rerun()
            
        if st.button("🗑️ Limpiar Carrito"):
            st.session_state.carrito = []
            st.rerun()

# --- TAB 2: PRODUCCIÓN ---
with tabs[1]:
    st.markdown("### 📥 Entrada de Inventario")
    sabor_prod = st.selectbox("Producto a rellenar:", st.session_state.inventario['Sabor'])
    cant_prod = st.number_input("Cantidad a agregar:", min_value=1, value=50)
    
    if st.button("GUARDAR ENTRADA"):
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == sabor_prod].index[0]
        st.session_state.inventario.at[idx, 'Stock'] += cant_prod
        st.success(f"Stock actualizado: {sabor_prod}")

# --- TAB 3: CAJA ---
with tabs[2]:
    st.markdown("### 💰 Corte del Día")
    m1, m2 = st.columns(2)
    m1.metric("Dinero en Caja", f"${st.session_state.caja['dinero']}")
    m2.metric("Productos Vendidos", f"{st.session_state.caja['items']}")
    
    st.markdown("---")
    st.dataframe(st.session_state.inventario[['Sabor', 'Stock']], use_container_width=True, hide_index=True)
    
    with st.expander("🔴 Opciones de Cierre"):
        if st.button("Confirmar Cierre de Caja"):
            st.session_state.caja = {'dinero': 0.0, 'items': 0}
            st.rerun()
