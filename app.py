import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Punto de Venta - La Central", page_icon="🥤", layout="centered")

# Estilos CSS para botones grandes en celular
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold;}
    .big-font { font-size: 20px !important; }
    div[data-testid="stMetricValue"] { font-size: 2rem; color: #00b4d8; }
    </style>
    """, unsafe_allow_html=True)

st.title("🥤 La Central POS")

# --- INICIALIZACIÓN DE VARIABLES (ESTADO) ---
if 'inventario' not in st.session_state:
    # Simulación inicial de tus 50 sabores (aquí puse algunos de ejemplo)
    datos_iniciales = {
        'Sabor': ['Limón', 'Fresa', 'Horchata', 'Jamaica', 'Mango', 'Tamarindo', 'Nuez', 'Coco'],
        'Stock': [100, 100, 100, 100, 100, 100, 100, 100]
    }
    st.session_state.inventario = pd.DataFrame(datos_iniciales)

# Variables para el corte del día
if 'caja_dia' not in st.session_state:
    st.session_state.caja_dia = 0.0 # Dinero total
if 'litros_vendidos' not in st.session_state:
    st.session_state.litros_vendidos = 0
if 'litros_producidos' not in st.session_state:
    st.session_state.litros_producidos = 0

# Carrito de compras temporal
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- NAVEGACIÓN ---
menu = st.sidebar.radio("Menú", ["🛒 Venta (Caja)", "🏗️ Producción", "💰 Corte de Caja"])

# ==========================================
# 1. SECCIÓN DE VENTA (CON CARRITO)
# ==========================================
if menu == "🛒 Venta (Caja)":
    st.header("Nueva Venta")

    # --- Paso 1: Agregar productos al carrito ---
    with st.container():
        c1, c2 = st.columns([2, 1])
        with c1:
            sabor_selec = st.selectbox("Sabor", st.session_state.inventario['Sabor'])
        with c2:
            stock_actual = st.session_state.inventario.loc[st.session_state.inventario['Sabor'] == sabor_selec, 'Stock'].values[0]
            st.caption(f"Stock: {stock_actual}")

        c3, c4 = st.columns(2)
        with c3:
            cantidad = st.number_input("Litros", min_value=1, value=1, step=1)
        with c4:
            # Selector de precio manual como pediste
            precio_selec = st.selectbox("Precio", [20, 16, 15], index=0)

        if st.button("➕ Agregar al Carrito"):
            if stock_actual >= cantidad:
                # Agregar a la lista del carrito
                item = {
                    "Sabor": sabor_selec,
                    "Litros": cantidad,
                    "Precio Unitario": precio_selec,
                    "Subtotal": cantidad * precio_selec
                }
                st.session_state.carrito.append(item)
                st.toast(f"{cantidad}L de {sabor_selec} agregados.")
            else:
                st.error(f"❌ No hay suficiente stock. Solo quedan {stock_actual}L.")

    st.divider()

    # --- Paso 2: Ver Carrito y Cobrar ---
    if len(st.session_state.carrito) > 0:
        st.subheader("📋 En el carrito:")
        df_carrito = pd.DataFrame(st.session_state.carrito)
        st.table(df_carrito)

        total_venta = df_carrito['Subtotal'].sum()
        total_litros_orden = df_carrito['Litros'].sum()

        st.metric("Total a Cobrar", f"${total_venta} MXN")

        col_cobrar, col_limpiar = st.columns([2, 1])
        
        with col_cobrar:
            if st.button("✅ COBRAR AHORA", type="primary"):
                # Procesar la venta
                for item in st.session_state.carrito:
                    # 1. Descontar de Inventario
                    idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == item['Sabor']].index
                    st.session_state.inventario.at[idx[0], 'Stock'] -= item['Litros']
                    
                    # 2. Sumar a contadores del día
                    st.session_state.caja_dia += item['Subtotal']
                    st.session_state.litros_vendidos += item['Litros']

                # 3. Limpiar carrito
                st.session_state.carrito = []
                st.success("¡Venta registrada con éxito!")
                st.rerun()
        
        with col_limpiar:
            if st.button("🗑️ Borrar"):
                st.session_state.carrito = []
                st.rerun()
    else:
        st.info("El carrito está vacío. Agrega productos arriba.")

# ==========================================
# 2. SECCIÓN DE PRODUCCIÓN
# ==========================================
elif menu == "🏗️ Producción":
    st.header("Registrar Producción")
    
    sabor_prod = st.selectbox("¿Qué sabor fabricaron?", st.session_state.inventario['Sabor'])
    cant_prod = st.number_input("Litros fabricados", min_value=1, step=1)
    
    if st.button("Ingresar al Inventario"):
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == sabor_prod].index
        st.session_state.inventario.at[idx[0], 'Stock'] += cant_prod
        
        # Sumar al reporte de producción del día
        st.session_state.litros_producidos += cant_prod
        
        st.balloons()
        st.success(f"Listo. {cant_prod} litros de {sabor_prod} agregados.")

# ==========================================
# 3. CORTE DE CAJA (ADMIN)
# ==========================================
elif menu == "💰 Corte de Caja":
    st.header("Corte del Día")
    st.markdown("Resumen de movimientos de hoy.")

    # Métricas Grandes
    c1, c2, c3 = st.columns(3)
    c1.metric("Dinero en Caja", f"${st.session_state.caja_dia}")
    c2.metric("Litros Vendidos", f"{st.session_state.litros_vendidos} L")
    c3.metric("Litros Producidos", f"{st.session_state.litros_producidos} L")

    st.divider()
    
    st.subheader("Inventario Actual")
    
    # Función para resaltar stock bajo
    def resaltar_bajo(val):
        color = '#ffcccb' if val < 15 else ''
        return f'background-color: {color}; color: black'

    st.dataframe(st.session_state.inventario.style.applymap(resaltar_bajo, subset=['Stock']), use_container_width=True)

    st.divider()
    
    # Botón de peligro para reiniciar el día
    with st.expander("Opciones Avanzadas (Cierre de Día)"):
        st.write("Esto pondrá el dinero y contadores del día en CERO. El inventario se mantiene.")
        if st.button("🔴 CERRAR DÍA Y REINICIAR CAJA"):
            st.session_state.caja_dia = 0.0
            st.session_state.litros_vendidos = 0
            st.session_state.litros_producidos = 0
            st.success("Día cerrado. La caja está en $0.")
            st.rerun()

