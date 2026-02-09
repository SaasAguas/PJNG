import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="La Central POS", page_icon="🍇", layout="centered")

# --- ESTILOS CSS REFORMADOS (MÁS COMPACTO) ---
st.markdown("""
    <style>
    .stApp { background-color: #F3E5F5; }
    div.stButton > button {
        background-color: #7B1FA2; color: white; border-radius: 10px;
        font-weight: bold; height: 2.5em; border: none;
    }
    h1 { color: #4A148C; text-align: center; font-size: 1.5rem !important; margin-bottom: 0px; }
    h2, h3 { color: #6A1B9A; text-align: center; font-size: 1.1rem !important; }
    
    /* Ajuste para que las tablas no se desborden en cel */
    .stDataFrame { width: 100%; }
    
    /* Métricas en una sola línea */
    div[data-testid="stMetricValue"] { font-size: 1.2rem !important; color: #4A148C; }
    
    /* Quitar espacio superior innecesario */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    
    /* Radio buttons horizontales centrados */
    div[data-testid="stMarkdownContainer"] > p { text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS ---
if 'inventario' not in st.session_state:
    data = {
        'Sabor': ['Limón', 'Jamaica', 'Mango', 'Piña', 'Fresa', 'Horchata', 'Nuez', 'Fresa con Crema', 'Coco'],
        'Categoría': ['Fruta', 'Fruta', 'Fruta', 'Fruta', 'Fruta', 'Crema', 'Crema', 'Crema', 'Crema'],
        'Stock': [100, 100, 100, 100, 100, 100, 100, 100, 100]
    }
    st.session_state.inventario = pd.DataFrame(data)

if 'carrito' not in st.session_state:
    st.session_state.carrito = []

if 'caja' not in st.session_state:
    st.session_state.caja = {'dinero': 0.0, 'litros': 0, 'prod': 0}

# --- TÍTULO PRINCIPAL ---
st.write("<h1>🍇 La Central</h1>", unsafe_allow_html=True)

# --- NAVEGACIÓN POR PESTAÑAS ---
tabs = st.tabs(["🛒 VENTA", "🏗️ PRODUCIR", "💰 CAJA"])

# ==========================================
# PESTAÑA 1: VENTA (PUNTO DE VENTA)
# ==========================================
with tabs[0]:
    # Selección de Tipo y Sabor en la misma fila
    c_cat, c_sab = st.columns([1, 1.5])
    with c_cat:
        filtro = st.radio("Tipo:", ["Fruta", "Crema"], horizontal=True)
    with c_sab:
        opciones = st.session_state.inventario[st.session_state.inventario['Categoría'] == filtro]['Sabor']
        sabor_sel = st.selectbox("Sabor:", opciones, label_visibility="collapsed")

    # Cantidad y Precio en la misma fila
    c_can, c_pre = st.columns(2)
    with c_can:
        cantidad = st.number_input("Litros:", min_value=1, value=1, step=1)
    with c_pre:
        precio = st.selectbox("$/Lt:", [20, 16, 15])

    if st.button("➕ AGREGAR"):
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == sabor_sel].index[0]
        if st.session_state.inventario.at[idx, 'Stock'] >= cantidad:
            st.session_state.carrito.append({"Sabor": sabor_sel, "Lts": cantidad, "Sub": cantidad * precio})
            st.toast(f"Añadido: {sabor_sel}")
        else:
            st.error("Stock insuficiente")

    # Carrito y Cobro
    if st.session_state.carrito:
        st.write("---")
        df_c = pd.DataFrame(st.session_state.carrito)
        st.dataframe(df_c, hide_index=True, use_container_width=True)
        
        total_p = df_c['Sub'].sum()
        
        col_t, col_b = st.columns([1, 1.5])
        col_t.metric("Total", f"${total_p}")
        
        if col_b.button("✅ COBRAR TODO"):
            for item in st.session_state.carrito:
                idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == item['Sabor']].index[0]
                st.session_state.inventario.at[idx, 'Stock'] -= item['Lts']
                st.session_state.caja['dinero'] += item['Sub']
                st.session_state.caja['litros'] += item['Lts']
            st.session_state.carrito = []
            st.success("¡Venta Exitosa!")
            st.rerun()
            
        if st.button("🗑️ Vaciar Carrito"):
            st.session_state.carrito = []
            st.rerun()

# ==========================================
# PESTAÑA 2: PRODUCCIÓN
# ==========================================
with tabs[1]:
    st.write("<h3>Entrada de Inventario</h3>", unsafe_allow_html=True)
    p_sabor = st.selectbox("Sabor fabricado:", st.session_state.inventario['Sabor'])
    p_cant = st.number_input("Cantidad fabricada (Lts):", min_value=1, value=50)
    
    if st.button("📥 SUMAR AL STOCK"):
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == p_sabor].index[0]
        st.session_state.inventario.at[idx, 'Stock'] += p_cant
        st.session_state.caja['prod'] += p_cant
        st.success("Inventario actualizado")

# ==========================================
# PESTAÑA 3: CORTE DE CAJA
# ==========================================
with tabs[2]:
    st.write("<h3>Resumen del Día</h3>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Caja", f"${st.session_state.caja['dinero']}")
    m2.metric("Venta", f"{st.session_state.caja['litros']}L")
    m3.metric("Prod", f"{st.session_state.caja['prod']}L")
    
    st.write("---")
    st.dataframe(st.session_state.inventario[['Sabor', 'Stock']], use_container_width=True, hide_index=True)
    
    if st.button("🔴 REINICIAR DÍA"):
        st.session_state.caja = {'dinero': 0.0, 'litros': 0, 'prod': 0}
        st.rerun()
