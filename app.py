import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Aguas POS", layout="centered")

st.title("🥤 Sistema de Control - Aguas de Sabor")

# --- Lógica de Precios ---
def calcular_precio(cantidad):
    return 15 if cantidad >= 100 else 20

# --- Base de Datos Temporal ---
if 'inventario' not in st.session_state:
    st.session_state.inventario = pd.DataFrame({
        'Sabor': ['Limón', 'Fresa', 'Horchata', 'Coco', 'Tamarindo'],
        'Stock': [100, 100, 100, 100, 100]
    })

# --- MENU LATERAL ---
menu = st.sidebar.selectbox("Menú", ["Registrar Venta", "Registrar Producción", "Estado del Negocio"])

# 1. SECCIÓN DE VENTAS
if menu == "Registrar Venta":
    st.header("🛒 Nueva Venta")
    sabor = st.selectbox("Selecciona el sabor", st.session_state.inventario['Sabor'])
    cantidad = st.number_input("Litros vendidos", min_value=1, step=1)
    
    precio_u = calcular_precio(cantidad)
    total = cantidad * precio_u
    
    st.subheader(f"Total a cobrar: ${total}")
    st.write(f"Precio: ${precio_u} por litro")

    if st.button("Confirmar Venta"):
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == sabor].index
        if st.session_state.inventario.at[idx[0], 'Stock'] >= cantidad:
            st.session_state.inventario.at[idx[0], 'Stock'] -= cantidad
            st.success(f"Venta registrada. ¡Ganaste ${cantidad}! (Tu comisión de $1)")
        else:
            st.error("❌ ¡No hay suficiente stock para esta venta!")

# 2. SECCIÓN DE PRODUCCIÓN (¡Ya con panel!)
elif menu == "Registrar Producción":
    st.header("🏗️ Registrar Producción")
    st.write("Usa este panel cuando terminen de fabricar nuevos litros.")
    
    sabor_p = st.selectbox("¿Qué sabor fabricaron?", st.session_state.inventario['Sabor'], key="prod_sabor")
    cantidad_p = st.number_input("¿Cuántos litros nuevos son?", min_value=1, step=1, key="prod_cant")
    
    if st.button("Sumar al Inventario"):
        # Buscamos el sabor en la tabla y le SUMAMOS
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == sabor_p].index
        st.session_state.inventario.at[idx[0], 'Stock'] += cantidad_p
        
        st.success(f"✅ ¡Excelente! Ahora tienes {st.session_state.inventario.at[idx[0], 'Stock']} litros de {sabor_p}.")
        st.balloons() # Unos globos para festejar la producción

# 3. ESTADO DEL NEGOCIO
elif menu == "Estado del Negocio":
    st.header("📊 Inventario y Alertas")
    st.table(st.session_state.inventario)
    
    # Alerta de Stock Bajo
    bajo_stock = st.session_state.inventario[st.session_state.inventario['Stock'] < 20]
    if not bajo_stock.empty:
        st.warning(f"⚠️ ¡Ojo! Queda poca agua de: {', '.join(bajo_stock['Sabor'])}")
    
