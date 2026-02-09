import streamlit as st
import pandas as pd

# Configuración chida de la página
st.set_page_config(page_title="La Central - Punto de Venta", page_icon="🥤", layout="centered")

# Estilo personalizado para que se vea más pro
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #00b4d8; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🥤 La Central - Control de Aguas")

# --- BASE DE DATOS DE SABORES (Aquí puedes meter los 50 poco a poco) ---
if 'inventario' not in st.session_state:
    sabores_iniciales = {
        'Sabor': ['Limón', 'Fresa', 'Horchata', 'Fresa con Crema', 'Nuez', 'Mango', 'Jamaica', 'Tamarindo'],
        'Categoría': ['Fruta', 'Fruta', 'Crema', 'Crema', 'Crema', 'Fruta', 'Fruta', 'Fruta'],
        'Stock': [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
    }
    st.session_state.inventario = pd.DataFrame(sabores_iniciales)

if 'ganancia_yo' not in st.session_state:
    st.session_state.ganancia_yo = 0.0

# --- LÓGICA DE PRECIOS ---
def obtener_precio(cantidad):
    return 15 if cantidad >= 100 else 20

# --- NAVEGACIÓN ---
menu = st.sidebar.radio("Ir a:", ["🛒 Punto de Venta", "🏗️ Producción", "📊 Reportes y Dueño"])

# 1. PUNTO DE VENTA
if menu == "🛒 Punto de Venta":
    st.header("Nueva Venta")
    
    col1, col2 = st.columns(2)
    with col1:
        cat_filtro = st.selectbox("Categoría", ["Todas", "Fruta", "Crema"])
    with col2:
        if cat_filtro == "Todas":
            opciones = st.session_state.inventario['Sabor']
        else:
            opciones = st.session_state.inventario[st.session_state.inventario['Categoría'] == cat_filtro]['Sabor']
        sabor_v = st.selectbox("Sabor", opciones)

    cantidad_v = st.number_input("Litros a vender", min_value=1, step=1)
    
    precio_u = obtener_precio(cantidad_v)
    total_v = cantidad_v * precio_u
    
    st.info(f"**Total a cobrar: ${total_v} MXN** (Precio: ${precio_u}/lt)")

    if st.button("Finalizar Venta"):
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == sabor_v].index
        stock_actual = st.session_state.inventario.at[idx[0], 'Stock']
        
        if stock_actual >= cantidad_v:
            st.session_state.inventario.at[idx[0], 'Stock'] -= cantidad_v
            # Aquí sumamos tu ganancia de $1 por litro vendido
            st.session_state.ganancia_yo += cantidad_v 
            st.success(f"✅ Venta registrada. ¡Llevas ${st.session_state.ganancia_yo} ganados hoy!")
        else:
            st.error(f"❌ No alcanzas, solo quedan {stock_actual} litros.")

# 2. PRODUCCIÓN
elif menu == "🏗️ Producción":
    st.header("Registro de Producción")
    st.write("Anota los litros nuevos que salieron de cocina.")
    
    sabor_p = st.selectbox("Sabor producido", st.session_state.inventario['Sabor'])
    cantidad_p = st.number_input("Cantidad de litros nuevos", min_value=1, step=1)

    if st.button("Ingresar al Almacén"):
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == sabor_p].index
        st.session_state.inventario.at[idx[0], 'Stock'] += cantidad_p
        st.balloons()
        st.success(f"✅ Stock actualizado: {sabor_p} ahora tiene {st.session_state.inventario.at[idx[0], 'Stock']} lts.")

# 3. REPORTES Y DUEÑO
elif menu == "📊 Reportes y Dueño":
    st.header("Dashboard del Negocio")
    
    # Métricas clave arriba
    c1, c2 = st.columns(2)
    c1.metric("Tu Ganancia ($1/lt)", f"${st.session_state.ganancia_yo} MXN")
    total_stock = st.session_state.inventario['Stock'].sum()
    c2.metric("Litros en Inventario", f"{total_stock} Lts")

    st.subheader("Estado por Sabor")
    # Colorear si el stock es bajo
    def color_stock(val):
        color = 'red' if val < 20 else 'black'
        return f'color: {color}'

    st.dataframe(st.session_state.inventario.style.applymap(color_stock, subset=['Stock']))

    if st.button("Simular cierre de día (Borrar Ganancia)"):
        st.session_state.ganancia_yo = 0
        st.rerun()
