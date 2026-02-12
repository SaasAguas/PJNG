import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import time

# ==========================================
# 1. CONFIGURACIÓN Y DATOS MAESTROS
# ==========================================
st.set_page_config(page_title="La Jalisciense POS", page_icon="🥤", layout="centered")

# Definir zona horaria (CDMX)
TZ_CDMX = pytz.timezone('America/Mexico_City')

# Catálogo Inicial
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
# 2. ESTILOS CSS REFINADOS (MODERNO)
# ==========================================
st.markdown("""
    <style>
    /* Tipografía y Fondo */
    .stApp { background-color: #FAFAFA; font-family: 'Segoe UI', sans-serif; }
    
    /* Encabezados */
    h1 { color: #D81B60; font-weight: 900; font-size: 2.2rem !important; text-align: center; margin-bottom: 0rem;}
    h3 { color: #880E4F; font-weight: 700; font-size: 1.3rem !important; margin-top: 1rem;}
    
    /* Botones */
    div.stButton > button {
        background: linear-gradient(135deg, #D81B60, #AD1457);
        color: white; border: none; border-radius: 12px;
        font-weight: 700; padding: 0.6rem 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    
    /* Textos Clave en Negrita */
    .big-label { font-size: 1.1rem; font-weight: 800; color: #37474F; }
    .price-tag { font-size: 1.5rem; font-weight: 900; color: #D81B60; }
    
    /* Tarjetas de Inventario (Moderno) */
    .inv-card {
        background-color: white; padding: 10px; border-radius: 10px;
        border-left: 5px solid #D81B60; margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Ajustes de espaciado */
    .block-container { padding-top: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. GESTIÓN DEL ESTADO
# ==========================================
def init_session():
    if 'inventario' not in st.session_state:
        st.session_state.inventario = pd.DataFrame(CATALOGO_INICIAL)
    if 'carrito' not in st.session_state:
        st.session_state.carrito = []
    if 'transacciones' not in st.session_state:
        st.session_state.transacciones = [] 
    if 'caja' not in st.session_state:
        st.session_state.caja = {'dinero': 0.0, 'litros_vendidos': 0, 'litros_producidos': 0}
    if 'cierre_confirmado' not in st.session_state:
        st.session_state.cierre_confirmado = False

init_session()

# ==========================================
# 4. INTERFAZ DE USUARIO
# ==========================================
st.write("<h1>La Jalisciense <span style='font-size:1rem; color: #BDBDBD'>| POS</span></h1>", unsafe_allow_html=True)

tabs = st.tabs(["🛒 PUNTO DE VENTA", "🏗️ PRODUCCIÓN", "📊 CORTE Y REPORTE"])

# --- TAB 1: VENTAS ---
with tabs[0]:
    col_left, col_right = st.columns([1, 1.1], gap="small")
    
    # Panel Izquierdo: Selección
    with col_left:
        st.markdown("### 🥤 Elegir Producto")
        
        # Filtros visuales
        tipo = st.radio("Categoría:", ["Fruta", "Crema"], horizontal=True, label_visibility="collapsed")
        
        df_filtrado = st.session_state.inventario[st.session_state.inventario['Categoría'] == tipo]
        
        # Selector de Sabor Estilizado
        st.markdown('<p class="big-label">Sabor:</p>', unsafe_allow_html=True)
        sabor = st.selectbox("Sabor:", df_filtrado['Sabor'], label_visibility="collapsed")
        
        # Stock Visual
        stock_disp = df_filtrado[df_filtrado['Sabor'] == sabor]['Stock'].values[0]
        if stock_disp < 15:
            st.error(f"⚠️ ¡Solo quedan {stock_disp} L!")
        else:
            st.success(f"Stock: {stock_disp} L disponibles")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<p class="big-label">Litros:</p>', unsafe_allow_html=True)
            qty = st.number_input("Litros", 1, 100, 1, label_visibility="collapsed")
        with c2:
            st.markdown('<p class="big-label">Precio:</p>', unsafe_allow_html=True)
            price = st.selectbox("Precio", [20, 16, 15], label_visibility="collapsed")
        
        if st.button("➕ AGREGAR", use_container_width=True):
            if stock_disp >= qty:
                st.session_state.carrito.append({
                    "Sabor": sabor, "Litros": qty, "Precio": price, "Subtotal": qty * price
                })
                st.toast(f"✅ Agregado: {sabor}")
            else:
                st.error("❌ Stock insuficiente")

    # Panel Derecho: Carrito Moderno (Lista, no tabla excel)
    with col_right:
        st.markdown("### 🧾 Cuenta Actual")
        
        if st.session_state.carrito:
            total_cuenta = 0
            for i, item in enumerate(st.session_state.carrito):
                total_cuenta += item['Subtotal']
                # Diseño de Ticket Individual
                st.markdown(f"""
                <div style="background: white; padding: 8px; border-radius: 8px; margin-bottom: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: bold; color: #333;">{item['Litros']}L {item['Sabor']}</div>
                        <div style="font-size: 0.8rem; color: #777;">${item['Precio']}/L</div>
                    </div>
                    <div style="font-weight: 900; color: #D81B60;">${item['Subtotal']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"<div style='text-align: right; font-size: 1.8rem; font-weight: 900; color: #D81B60;'>Total: ${total_cuenta}</div>", unsafe_allow_html=True)
            
            c_pay, c_del = st.columns([3, 1])
            if c_pay.button("✅ COBRAR", type="primary", use_container_width=True):
                # PROCESAR
                hora_actual = datetime.now(TZ_CDMX).strftime("%H:%M:%S")
                for item in st.session_state.carrito:
                    idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == item['Sabor']].index[0]
                    st.session_state.inventario.at[idx, 'Stock'] -= item['Litros']
                    
                    st.session_state.transacciones.append({
                        "Hora": hora_actual, "Tipo": "Venta", "Desc": f"{item['Litros']}L {item['Sabor']}", "Monto": item['Subtotal']
                    })
                    st.session_state.caja['dinero'] += item['Subtotal']
                    st.session_state.caja['litros_vendidos'] += item['Litros']

                st.session_state.carrito = []
                st.balloons()
                st.success("¡Venta Cobrada!")
                time.sleep(1)
                st.rerun()

            if c_del.button("🗑️", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()
        else:
            st.info("Carrito vacío. Agrega productos.")

# --- TAB 2: PRODUCCIÓN ---
with tabs[1]:
    st.markdown("### 🏭 Registro de Fabricación")
    
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        st.markdown('<p class="big-label">Sabor Producido:</p>', unsafe_allow_html=True)
        sabor_prod = st.selectbox("Sabor Prod", st.session_state.inventario['Sabor'], label_visibility="collapsed")
    with col_p2:
        st.markdown('<p class="big-label">Cantidad (L):</p>', unsafe_allow_html=True)
        cant_prod = st.number_input("Cant Prod", 1, 500, 50, label_visibility="collapsed")
    
    if st.button("📥 INGRESAR AL ALMACÉN", use_container_width=True):
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == sabor_prod].index[0]
        st.session_state.inventario.at[idx, 'Stock'] += cant_prod
        
        hora_actual = datetime.now(TZ_CDMX).strftime("%H:%M:%S")
        st.session_state.transacciones.append({
            "Hora": hora_actual, "Tipo": "Producción", "Desc": f"{cant_prod}L {sabor_prod}", "Monto": 0
        })
        st.session_state.caja['litros_producidos'] += cant_prod
        st.success(f"✅ Stock actualizado: {sabor_prod} (+{cant_prod}L)")

# --- TAB 3: CORTE Y REPORTE ---
with tabs[2]:
    st.markdown("### 📈 Panel de Control")
    
    # KPIs Estilizados
    k1, k2, k3 = st.columns(3)
    k1.markdown(f"<div style='text-align:center; background:#FFF; padding:10px; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1)'><div style='font-size:0.9rem; color:#777'>Caja</div><div style='font-size:1.4rem; font-weight:bold; color:#D81B60'>${st.session_state.caja['dinero']:,.0f}</div></div>", unsafe_allow_html=True)
    k2.markdown(f"<div style='text-align:center; background:#FFF; padding:10px; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1)'><div style='font-size:0.9rem; color:#777'>Ventas</div><div style='font-size:1.4rem; font-weight:bold; color:#333'>{st.session_state.caja['litros_vendidos']} L</div></div>", unsafe_allow_html=True)
    k3.markdown(f"<div style='text-align:center; background:#FFF; padding:10px; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1)'><div style='font-size:0.9rem; color:#777'>Prod</div><div style='font-size:1.4rem; font-weight:bold; color:#333'>{st.session_state.caja['litros_producidos']} L</div></div>", unsafe_allow_html=True)
    
    st.divider()
    
    c_inv, c_hist = st.columns(2)
    
    with c_inv:
        st.markdown("#### 🧊 Inventario Visual")
        # Renderizado de Inventario Moderno (Barras)
        for index, row in st.session_state.inventario.iterrows():
            percent = min(100, row['Stock'])
            color_bar = "#D81B60" if row['Stock'] > 20 else "#E53935"
            st.markdown(f"""
            <div style="margin-bottom: 8px;">
                <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:0.9rem;">
                    <span>{row['Sabor']}</span>
                    <span>{row['Stock']}L</span>
                </div>
                <div style="width:100%; background-color:#EEE; height:8px; border-radius:4px;">
                    <div style="width:{percent}%; background-color:{color_bar}; height:8px; border-radius:4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
    with c_hist:
        st.markdown("#### 📜 Historial de Ventas")
        if st.session_state.transacciones:
            df_trans = pd.DataFrame(st.session_state.transacciones)
            st.dataframe(df_trans.iloc[::-1], use_container_width=True, hide_index=True, height=300)
            
            # Botón de Descarga OBLIGATORIO
            csv = df_trans.to_csv(index=False).encode('utf-8')
            descargado = st.download_button(
                "📥 Descargar Reporte (CSV)",
                data=csv,
                file_name=f"corte_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_descarga"
            )
        else:
            st.info("Sin movimientos.")

    # ZONA DE CIERRE SEGURA
    st.markdown("---")
    with st.expander("🔐 Zona de Cierre de Caja"):
        st.warning("Para cerrar caja, primero descarga el reporte.")
        
        # Checkbox de seguridad
        confirmar_seguridad = st.checkbox("Entiendo que al cerrar se reinicia el dinero a $0")
        
        if confirmar_seguridad:
            # Botón con cuenta regresiva simulada (Lógica de 2 pasos)
            if 'intento_cierre' not in st.session_state:
                st.session_state.intento_cierre = False
                
            if not st.session_state.intento_cierre:
                if st.button("🔴 INICIAR CIERRE DE CAJA"):
                    st.session_state.intento_cierre = True
                    st.rerun()
            else:
                st.error("⚠️ ¿Estás seguro? Presiona otra vez para confirmar.")
                col_conf, col_cancel = st.columns(2)
                
                if col_conf.button("🔴 CONFIRMAR CIERRE AHORA"):
                    # Resetear todo
                    st.session_state.caja = {'dinero': 0.0, 'litros_vendidos': 0, 'litros_producidos': 0}
                    st.session_state.transacciones = []
                    st.session_state.intento_cierre = False
                    st.success("✅ Día cerrado y caja reiniciada.")
                    time.sleep(1.5)
                    st.rerun()
                
                if col_cancel.button("Cancelar"):
                    st.session_state.intento_cierre = False
                    st.rerun()
