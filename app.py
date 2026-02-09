import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Aguas POS", layout="centered")

st.title("🥤 Sistema de Control - Aguas de Sabor")

# --- Lógica de Precios ---
# Si cantidad >= 100, precio = 15. Si no, precio = 20.
def calcular_precio(cantidad):
    return 15 if cantidad >= 100 else 20

# --- Simulación de Base de Datos (En la vida real usarías un archivo o SQL) ---
if 'inventario' not in st.session_state:
    st.session_state.inventario = pd.DataFrame({
        'Sabor': ['Limón', 'Fresa', 'Horchata', 'Coco'],
        'Stock': [100, 100, 100, 100]
    })

# --- MENU LATERAL ---
menu = st.sidebar.selectbox("Menú", ["Registrar Venta", "Registrar Producción", "Estado del Negocio"])

if menu == "Registrar Venta":
    st.header("🛒 Nueva Venta")
    sabor = st.selectbox("Selecciona el sabor", st.session_state.inventario['Sabor'])
    cantidad = st.number_input("Litros vendidos", min_value=1, step=1)
    
    precio_u = calcular_precio(cantidad)
    total = cantidad * precio_u
    
    st.subheader(f"Total a cobrar: ${total}")
    st.write(f"Precio por litro aplicado: ${precio_u}")

    if st.button("Confirmar Venta"):
        # Actualizar Stock
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == sabor].index
        st.session_state.inventario.at[idx[0], 'Stock'] -= cantidad
        st.success(f"Venta registrada. ¡Ganaste ${cantidad}! (Tu comisión de $1 por litro)")

elif menu == "Estado del Negocio":
    st.header("📊 Inventario y Alertas")
    st.table(st.session_state.inventario)
    
    # Alerta de Stock Bajo
    bajo_stock = st.session_state.inventario[st.session_state.inventario['Stock'] < 20]
    if not bajo_stock.empty:
        st.warning(f"⚠️ ¡Ojo! Queda poca agua de: {', '.join(bajo_stock['Sabor'])}")

