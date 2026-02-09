import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="La Central POS", page_icon="🍇", layout="centered")

# --- ESTILOS CSS (TEMA MORADO Y COMPACTO) ---
st.markdown("""
    <style>
    /* Fondo General */
    .stApp {
        background-color: #F3E5F5;
    }
    /* Botones Morados */
    div.stButton > button {
        background-color: #7B1FA2;
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: bold;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #4A148C;
        color: white;
    }
    /* Títulos Centrados y Pequeños */
    h1 {
        color: #4A148C;
        text-align: center;
        font-size: 1.8rem !important;
        padding-bottom: 0px;
    }
    h2, h3 {
        color: #6A1B9A;
        text-align: center;
        font-size: 1.2rem !important;
        margin-top: 0px;
    }
    /* Métricas compactas */
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        color: #4A148C;
    }
    /* Reducir espacios */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS ---
if 'inventario' not in st.session_state:
    # Ahora incluimos la columna 'Categoría'
    data = {
        'Sabor': ['Limón', 'Jamaica', 'Mango', 'Piña', 'Fresa', 'Horchata', 'Nuez', 'Fresa con Crema', 'Coco'],
        'Categoría': ['Fruta', 'Fruta', 'Fruta', 'Fruta', 'Fruta', 'Crema', 'Crema', 'Crema', 'Crema'],
        'Stock': [100, 100, 100, 100, 100, 100, 100, 100, 100]
    }
    st.session_state.inventario = pd.DataFrame(data)

if 'carrito' not in st.session_state:
    st.session_state.carrito = []

if 'caja' not in st.session_state:
    st.session_state.caja = {'dinero': 0.0, 'litros': 0}

# --- TÍTULO ---
st.title("🍇 La Central - Control")

# --- MENÚ DE NAVEGACIÓN (TABS PARA AHORRAR ESPACIO) ---
tabs = st.tabs(["🛒 VENTA", "🏗️ PRODUCIR", "💰 CAJA"])

# ==========================================
# PESTAÑA 1: VENTA RÁPIDA
# ==========================================
with tabs[0]:
    # Fila 1: Filtros y Selección
    col_cat, col_sab = st.columns([1, 2])
    with col_cat:
        filtro = st.radio("Tipo:", ["Fruta", "Crema"], horizontal=True)
    with col_sab:
        # Filtrar sabores según categoría
        opciones = st.session_state.inventario[st.session_state.inventario['Categoría'] == filtro]['Sabor']
        sabor_sel = st.selectbox("Sabor:", opciones)

    # Fila 2: Cantidad (Input numérico) y Precio
    col_cant, col_precio = st.columns(2)
    with col_cant:
        # Aquí escribes "80" directo o usas flechas
        cantidad = st.number_input("Litros:", min_value=1, value=1, step=1)
    with col_precio:
        precio = st.selectbox("Precio/Lt:", [20, 16, 15], index=0)

    # Botón de Agregar (Compacto)
    if st.button("➕ AGREGAR AL CARRITO"):
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == sabor_sel].index[0]
        stock_actual = st.session_state.inventario.at[idx, 'Stock']
        
        if stock_actual >= cantidad:
            st.session_state.carrito.append({
                "Sabor": sabor_sel, "Litros": cantidad, "Total": cantidad * precio
            })
            st.toast("Agregado")
        else:
            st.error(f"Solo hay {stock_actual}L")

    st.divider()

    # Zona de Cobro (Compacta)
    if st.session_state.carrito:
        df_c = pd.DataFrame(st.session_state.carrito)
        st.dataframe(df_c, hide_index=True, use_container_width=True)
        
        total_pagar = df_c['Total'].sum()
        
        c_tot, c_btn = st.columns([1, 2])
        with c_tot:
            st.metric("Total", f"${total_pagar}")
        with c_btn:
            if st.button("✅ COBRAR AHORA"):
                for item in st.session_state.carrito:
                    # Descontar inventario
                    idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == item['Sabor']].index[0]
                    st.session_state.inventario.at[idx, 'Stock'] -= item['Litros']
                    # Sumar a caja
                    st.session_state.caja['dinero'] += item['Total']
                    st.session_state.caja['litros'] += item['Litros']
                
                st.session_state.carrito = []
                st.success("¡Venta Lista!")
                st.rerun()
            
            if st.button("🗑️ Borrar"):
                st.session_state.carrito = []
                st.rerun()

# ==========================================
# PESTAÑA 2: PRODUCCIÓN MASIVA
# ==========================================
with tabs[1]:
    st.subheader("Entrada de Producto")
    
    p_sabor = st.selectbox("Sabor Fabricado:", st.session_state.inventario['Sabor'])
    
    # Input numérico para entrada masiva (ej. 200 litros)
    p_cantidad = st.number_input("Litros Fabricados:", min_value=1, value=50, step=10)
    
    if st.button("📥 INGRESAR AL ALMACÉN"):
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == p_sabor].index[0]
        st.session_state.inventario.at[idx, 'Stock'] += p_cantidad
        st.success(f"Se agregaron {p_cantidad}L de {p_sabor}")

# ==========================================
# PESTAÑA 3: CORTE Y DATOS
# ==========================================
with tabs[2]:
    st.subheader("Resumen del Día")
    m1, m2 = st.columns(2)
    m1.metric("Ventas ($)", f"${st.session_state.caja['dinero']}")
    m2.metric("Litros Salida", f"{st.session_state.caja['litros']} L")
    
    st.markdown("---")
    st.caption("Inventario Actual")
    
    # Formato condicional (Rojo si < 15)
    def stock_bajo(val):
        return 'background-color: #ffcdd2; color: black' if val < 15 else ''

    st.dataframe(st.session_state.inventario[['Sabor', 'Stock']].style.applymap(stock_bajo, subset=['Stock']), use_container_width=True)
    
    if st.button("🔴 CERRAR DÍA (Reiniciar Caja)"):
        st.session_state.caja = {'dinero': 0.0, 'litros': 0}
        st.rerun()
                                            
