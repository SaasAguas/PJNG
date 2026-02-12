import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# ==========================================
# 1. CONFIGURACIÓN Y DATOS MAESTROS
# ==========================================
st.set_page_config(page_title="La Central POS", page_icon="🍇", layout="centered")

# Definir zona horaria (CDMX)
TZ_CDMX = pytz.timezone('America/Mexico_City')

# Catálogo Inicial (Fácil de editar aquí arriba)
CATALOGO_INICIAL = [
    {"Sabor": "Limón", "Categoría": "Fruta", "Stock": 100},
    {"Sabor": "Jamaica", "Categoría": "Fruta", "Stock": 100},
    {"Sabor": "Mango", "Categoría": "Fruta", "Stock": 100},
    {"Sabor": "Piña", "Categoría": "Fruta", "Stock": 100},
    {"Sabor": "Fresa", "Categoría": "Fruta", "Stock": 100},
    {"Sabor": "Horchata", "Categoría": "Crema", "Stock": 100},
    {"Sabor": "Nuez", "Categoría": "Crema", "Stock": 100},
    {"Sabor": "Fresa con Crema", "Categoría": "Crema", "Stock": 100},
    {"Sabor": "Coco", "Categoría": "Crema", "Stock": 100},
]

# ==========================================
# 2. ESTILOS CSS PROFESIONALES
# ==========================================
st.markdown("""
    <style>
    /* Tipografía y Fondo */
    .stApp { background-color: #F8F9FA; font-family: 'Helvetica Neue', sans-serif; }
    
    /* Encabezados */
    h1 { color: #4A148C; font-weight: 800; font-size: 2rem !important; text-align: center; margin-bottom: 0rem;}
    h3 { color: #6A1B9A; font-weight: 600; font-size: 1.2rem !important; margin-top: 1rem;}
    
    /* Botones Interactivos */
    div.stButton > button {
        background: linear-gradient(45deg, #6A1B9A, #8E24AA);
        color: white; border: none; border-radius: 8px;
        font-weight: 600; padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Métricas (Cards) */
    div[data-testid="stMetricValue"] { font-size: 1.6rem !important; color: #4A148C; font-weight: bold; }
    div[data-testid="metric-container"] {
        background-color: white; padding: 10px; border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center;
    }
    
    /* Tablas limpias */
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    
    /* Ajustes de espaciado */
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. GESTIÓN DEL ESTADO (SESSION STATE)
# ==========================================
def init_session():
    if 'inventario' not in st.session_state:
        st.session_state.inventario = pd.DataFrame(CATALOGO_INICIAL)
    
    if 'carrito' not in st.session_state:
        st.session_state.carrito = []
        
    if 'transacciones' not in st.session_state:
        st.session_state.transacciones = [] # Log de auditoría

    if 'caja' not in st.session_state:
        st.session_state.caja = {'dinero': 0.0, 'litros_vendidos': 0, 'litros_producidos': 0}

init_session()

# ==========================================
# 4. INTERFAZ DE USUARIO
# ==========================================
st.write("<h1>🍇 La Central <span style='font-size:1rem; color: #9E9E9E'>| Sistema POS</span></h1>", unsafe_allow_html=True)

tabs = st.tabs(["🛒 PUNTO DE VENTA", "🏗️ PRODUCCIÓN", "📊 CORTE Y REPORTE"])

# --- TAB 1: VENTAS ---
with tabs[0]:
    col_left, col_right = st.columns([1, 1.2], gap="medium")
    
    # Panel Izquierdo: Selección
    with col_left:
        st.markdown("### 🛍️ Agregar Producto")
        tipo = st.radio("Categoría:", ["Fruta", "Crema"], horizontal=True, label_visibility="collapsed")
        
        # Filtrado inteligente
        df_filtrado = st.session_state.inventario[st.session_state.inventario['Categoría'] == tipo]
        sabor = st.selectbox("Sabor:", df_filtrado['Sabor'])
        
        # Mostrar stock disponible en tiempo real
        stock_disp = df_filtrado[df_filtrado['Sabor'] == sabor]['Stock'].values[0]
        if stock_disp < 10:
            st.caption(f"⚠️ ¡Poco Stock! Quedan {stock_disp} L")
        else:
            st.caption(f"Stock disponible: {stock_disp} L")

        c1, c2 = st.columns(2)
        qty = c1.number_input("Litros:", 1, 100, 1)
        price = c2.selectbox("Precio:", [20, 16, 15])
        
        if st.button("➕ Agregar al Pedido", use_container_width=True):
            if stock_disp >= qty:
                st.session_state.carrito.append({
                    "Sabor": sabor, "Litros": qty, "Precio": price, "Subtotal": qty * price
                })
                st.toast(f"✅ {qty}L de {sabor} agregados", icon="🛒")
            else:
                st.error(f"❌ Stock insuficiente. Solo hay {stock_disp}L")

    # Panel Derecho: Carrito y Cobro
    with col_right:
        st.markdown("### 🧾 Cuenta Actual")
        if st.session_state.carrito:
            df_cart = pd.DataFrame(st.session_state.carrito)
            # Tabla estilizada
            st.dataframe(
                df_cart, 
                column_config={
                    "Subtotal": st.column_config.NumberColumn(format="$%d")
                },
                hide_index=True, use_container_width=True
            )
            
            total = df_cart['Subtotal'].sum()
            st.markdown(f"<div style='text-align: right; font-size: 1.5rem; font-weight: bold; color: #4A148C;'>Total: ${total}</div>", unsafe_allow_html=True)
            
            col_pay, col_del = st.columns([2, 1])
            if col_pay.button("✅ COBRAR", type="primary", use_container_width=True):
                # PROCESAR VENTA
                hora_actual = datetime.now(TZ_CDMX).strftime("%H:%M:%S")
                
                for item in st.session_state.carrito:
                    # 1. Descontar Inventario
                    idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == item['Sabor']].index[0]
                    st.session_state.inventario.at[idx, 'Stock'] -= item['Litros']
                    
                    # 2. Registrar Transacción (Log)
                    st.session_state.transacciones.append({
                        "Hora": hora_actual,
                        "Tipo": "Venta",
                        "Descripción": f"{item['Litros']}L {item['Sabor']}",
                        "Monto": item['Subtotal']
                    })
                    
                    # 3. Actualizar Caja
                    st.session_state.caja['dinero'] += item['Subtotal']
                    st.session_state.caja['litros_vendidos'] += item['Litros']

                st.session_state.carrito = []
                st.balloons()
                st.success("Venta registrada exitosamente")
                st.rerun()

            if col_del.button("🗑️", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()
        else:
            st.info("El carrito está vacío.")

# --- TAB 2: PRODUCCIÓN ---
with tabs[1]:
    st.markdown("### 🏭 Registro de Fabricación")
    
    col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
    sabor_prod = col_p1.selectbox("Sabor Producido:", st.session_state.inventario['Sabor'])
    cant_prod = col_p2.number_input("Cantidad (L):", 1, 500, 50)
    
    # Botón grande para facilitar la entrada
    if st.button("📥 INGRESAR AL ALMACÉN", use_container_width=True):
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == sabor_prod].index[0]
        st.session_state.inventario.at[idx, 'Stock'] += cant_prod
        
        # Log
        hora_actual = datetime.now(TZ_CDMX).strftime("%H:%M:%S")
        st.session_state.transacciones.append({
            "Hora": hora_actual,
            "Tipo": "Producción",
            "Descripción": f"{cant_prod}L {sabor_prod}",
            "Monto": 0 # Producción no genera dinero inmediato en caja
        })
        
        st.session_state.caja['litros_producidos'] += cant_prod
        st.success(f"✅ Stock actualizado: {sabor_prod} (+{cant_prod}L)")

# --- TAB 3: CORTE Y ADMIN ---
with tabs[2]:
    st.markdown("### 📈 Panel de Control")
    
    # KPIs
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Dinero en Caja", f"${st.session_state.caja['dinero']:,.2f}")
    kpi2.metric("Ventas (L)", f"{st.session_state.caja['litros_vendidos']} L")
    kpi3.metric("Producción (L)", f"{st.session_state.caja['litros_producidos']} L")
    
    st.divider()
    
    # Tablas de detalle
    c_inv, c_hist = st.columns(2)
    
    with c_inv:
        st.markdown("#### 🧊 Inventario Actual")
        st.dataframe(
            st.session_state.inventario[['Sabor', 'Stock']], 
            use_container_width=True, 
            hide_index=True,
            column_config={"Stock": st.column_config.ProgressColumn(format="%d L", min_value=0, max_value=200)}
        )
        
    with c_hist:
        st.markdown("#### 📜 Últimos Movimientos")
        if st.session_state.transacciones:
            df_trans = pd.DataFrame(st.session_state.transacciones)
            st.dataframe(
                df_trans.iloc[::-1], # Mostrar lo más nuevo arriba
                use_container_width=True, 
                hide_index=True,
                height=300
            )
            
            # Botón de Descarga (CSV)
            csv = df_trans.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Descargar Reporte del Día (CSV)",
                data=csv,
                file_name="corte_caja_aguas.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No hay movimientos hoy.")

    # Zona de peligro
    with st.expander("🔴 Opciones de Cierre"):
        st.warning("Al cerrar el día, el dinero en caja volverá a $0. El inventario se mantiene.")
        if st.button("Confirmar Cierre de Caja"):
            st.session_state.caja = {'dinero': 0.0, 'litros_vendidos': 0, 'litros_producidos': 0}
            st.session_state.transacciones = []
            st.success("Día cerrado correctamente.")
            st.rerun()
        
