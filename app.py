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

# --- LISTAS REALES ORDENADAS ---
SABORES_FRUTA = sorted([
    "Ciruela", "Fresa", "Fresa-Hierbabuena", "Guayaba", "Guayaba-Fresa", 
    "Guayaba-Hierbabuena", "Hierbabuena-Limon", "Jamaica", "Lima", 
    "Lima-Albahaca", "Lima-Stevia", "Limon Con Pepino Y Hierbabuena", 
    "Limon-Chia", "Limón-Alfalfa", "Limón-Hierbabuena", "Mango", 
    "Maracuya", "Melon", "Melon Citrico", "Piña Naranja Hierbabuena", 
    "Piña-Alfalfa", "Piña-Hierbabuena", "Piña-Naranja"
])

SABORES_CREMA = sorted([
    "Cebada", "Chai", "Coco Con Nuez", "Crema Irlandesa", "Horchata Arroz", 
    "Horchata De Fresa", "Kalhua", "Mazapan", "Taro", "Vainilla"
])

# Diccionario de Precios Fijos
PRODUCTOS_EXTRA = {
    "Campana": 20, "Frapuchino": 10, "Fresas Con Crema": 25,
    "Paleta De Agua": 25, "Paleta De Leche": 30, "Sandwich": 20
}

# Construcción del DataFrame Inicial
datos = []
for s in SABORES_FRUTA: datos.append({"Sabor": s, "Categoría": "Fruta", "Stock": 50, "PrecioFijo": 0})
for s in SABORES_CREMA: datos.append({"Sabor": s, "Categoría": "Crema", "Stock": 50, "PrecioFijo": 0})
for p in sorted(PRODUCTOS_EXTRA.keys()): datos.append({"Sabor": p, "Categoría": "Paletas", "Stock": 20, "PrecioFijo": PRODUCTOS_EXTRA[p]})

CATALOGO_INICIAL = pd.DataFrame(datos)

# ==========================================
# 2. ESTILOS CSS REFINADOS (MODERNO & LIMPIO)
# ==========================================
st.markdown("""
    <style>
    /* Tipografía y Fondo */
    .stApp { background-color: #F8F5FA; font-family: 'Segoe UI', sans-serif; color: #333; }
    
    /* Encabezados */
    h1 { color: #C2185B; font-weight: 900; font-size: 2.2rem !important; text-align: center; margin-bottom: 0rem;}
    h3 { color: #880E4F; font-weight: 700; font-size: 1.3rem !important; margin-top: 1rem;}
    
    /* Botones de Categoría (Estilo Secundario) */
    div.stButton > button[kind="secondary"] {
        background-color: white; color: #C2185B; border: 2px solid #C2185B;
        border-radius: 12px; height: 3.5em; font-weight: bold;
    }
    div.stButton > button[kind="secondary"]:hover { background-color: #FCE4EC; }

    /* Botones de Acción (Estilo Primario) */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #C2185B, #880E4F);
        color: white; border: none; border-radius: 12px;
        font-weight: 700; padding: 0.6rem 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    
    /* Textos Clave */
    .big-label { font-size: 1rem; font-weight: 800; color: #555; margin-bottom: -5px; display: block;}
    .stock-warning { color: #D32F2F; font-weight: bold; font-size: 0.9rem; }
    .stock-ok { color: #388E3C; font-weight: bold; font-size: 0.9rem; }
    
    /* Tarjetas de Carrito */
    .cart-item {
        background: white; padding: 10px; border-radius: 10px;
        border-left: 5px solid #C2185B; margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center;
    }
    .cart-title { font-weight: 700; color: #333; }
    
    /* Ajustes de espaciado */
    .block-container { padding-top: 1.5rem; }
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
    if 'transacciones' not in st.session_state:
        st.session_state.transacciones = [] 
    if 'caja' not in st.session_state:
        st.session_state.caja = {'dinero': 0.0, 'litros_vendidos': 0, 'litros_producidos': 0}
    if 'cat_activa' not in st.session_state:
        st.session_state.cat_activa = "Fruta" # Categoría por defecto

init_session()

# ==========================================
# 4. INTERFAZ DE USUARIO
# ==========================================
st.write("<h1>La Jalisciense <span style='font-size:1rem; color: #BDBDBD'>| POS</span></h1>", unsafe_allow_html=True)

tabs = st.tabs(["🛒 PUNTO DE VENTA", "🏗️ PRODUCCIÓN", "📊 CORTE Y REPORTE"])

# --- TAB 1: VENTAS ---
with tabs[0]:
    # 1. BOTONES GRANDES DE CATEGORÍA
    c1, c2, c3 = st.columns(3)
    # El botón activo se ve "lleno" (primary), los inactivos "con borde" (secondary)
    if c1.button("🍉 FRUTA", key="btn_fruta", use_container_width=True, type="secondary" if st.session_state.cat_activa != "Fruta" else "primary"): 
        st.session_state.cat_activa = "Fruta"
        st.rerun()
    if c2.button("🥛 CREMA", key="btn_crema", use_container_width=True, type="secondary" if st.session_state.cat_activa != "Crema" else "primary"): 
        st.session_state.cat_activa = "Crema"
        st.rerun()
    if c3.button("🍭 PALETAS", key="btn_paletas", use_container_width=True, type="secondary" if st.session_state.cat_activa != "Paletas" else "primary"): 
        st.session_state.cat_activa = "Paletas"
        st.rerun()
    
    st.divider()

    # 2. SELECCIÓN DE PRODUCTO
    col_sel, col_datos = st.columns([1.5, 1], gap="small")
    
    # Filtramos por categoría activa
    df_filtrado = st.session_state.inventario[st.session_state.inventario['Categoría'] == st.session_state.cat_activa]
    
    with col_sel:
        st.markdown(f'<span class="big-label">Sabor ({st.session_state.cat_activa}):</span>', unsafe_allow_html=True)
        sabor = st.selectbox("Sabor:", df_filtrado['Sabor'], label_visibility="collapsed")
        
        # Stock Visual
        item_data = df_filtrado[df_filtrado['Sabor'] == sabor].iloc[0]
        stock_disp = item_data['Stock']
        if stock_disp < 15:
            st.markdown(f'<span class="stock-warning">⚠️ Quedan {stock_disp}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="stock-ok">✅ Stock: {stock_disp}</span>', unsafe_allow_html=True)

    with col_datos:
        # LÓGICA DE PRECIOS AUTOMÁTICA
        if st.session_state.cat_activa == "Paletas":
            # Precio Fijo
            st.markdown('<span class="big-label">Precio:</span>', unsafe_allow_html=True)
            price = st.number_input("Precio", value=float(item_data['PrecioFijo']), disabled=True, label_visibility="collapsed")
            st.markdown('<span class="big-label">Piezas:</span>', unsafe_allow_html=True)
            qty = st.number_input("Cant:", min_value=1, value=1, label_visibility="collapsed")
            unidad = "Pza"
        else:
            # Precio Variable (Aguas)
            st.markdown('<span class="big-label">Precio/Lt:</span>', unsafe_allow_html=True)
            price = st.selectbox("Precio", [20, 16, 15], label_visibility="collapsed")
            st.markdown('<span class="big-label">Litros:</span>', unsafe_allow_html=True)
            qty = st.number_input("Cant:", min_value=1, value=1, label_visibility="collapsed")
            unidad = "Lt"
        
    if st.button("➕ AGREGAR AL PEDIDO", use_container_width=True, type="primary"):
        if stock_disp >= qty:
            st.session_state.carrito.append({
                "Sabor": sabor, "Litros": qty, "Unidad": unidad,
                "Precio": price, "Subtotal": qty * price
            })
            st.toast(f"✅ Agregado: {sabor}")
        else:
            st.error("❌ Stock insuficiente")

    # 3. CARRITO VISUAL
    if st.session_state.carrito:
        st.divider()
        st.markdown("### 🧾 Cuenta Actual")
        total_cuenta = 0
        for item in st.session_state.carrito:
            total_cuenta += item['Subtotal']
            st.markdown(f"""
            <div class="cart-item">
                <div>
                    <div class="cart-title">{item['Litros']} {item['Unidad']} - {item['Sabor']}</div>
                    <div style="font-size: 0.8rem; color: #777;">${item['Precio']} c/u</div>
                </div>
                <div style="font-weight: 900; color: #D81B60;">${item['Subtotal']}</div>
            </div>""", unsafe_allow_html=True)
        
        st.markdown(f"<div style='text-align: right; font-size: 1.8rem; font-weight: 900; color: #D81B60;'>Total: ${total_cuenta}</div>", unsafe_allow_html=True)
        
        c_pay, c_del = st.columns([3, 1])
        if c_pay.button("✅ COBRAR", type="primary", use_container_width=True):
            hora_actual = datetime.now(TZ_CDMX).strftime("%H:%M:%S")
            for item in st.session_state.carrito:
                idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == item['Sabor']].index[0]
                st.session_state.inventario.at[idx, 'Stock'] -= item['Litros']
                
                st.session_state.transacciones.append({
                    "Hora": hora_actual, "Tipo": "Venta", "Desc": f"{item['Litros']}{item['Unidad']} {item['Sabor']}", "Monto": item['Subtotal']
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

# --- TAB 2: PRODUCCIÓN ---
with tabs[1]:
    st.markdown("### 🏭 Registro de Fabricación")
    
    col_p1, col_p2 = st.columns([1.5, 1])
    with col_p1:
        st.markdown('<p class="big-label">Producto:</p>', unsafe_allow_html=True)
        # Ordenamos la lista para encontrar rápido
        sabor_prod = st.selectbox("Sabor Prod", sorted(st.session_state.inventario['Sabor'].unique()), label_visibility="collapsed")
    with col_p2:
        st.markdown('<p class="big-label">Entrada:</p>', unsafe_allow_html=True)
        cant_prod = st.number_input("Cant Prod", 1, 500, 50, label_visibility="collapsed")
    
    if st.button("📥 INGRESAR AL ALMACÉN", use_container_width=True, type="primary"):
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == sabor_prod].index[0]
        st.session_state.inventario.at[idx, 'Stock'] += cant_prod
        
        hora_actual = datetime.now(TZ_CDMX).strftime("%H:%M:%S")
        st.session_state.transacciones.append({
            "Hora": hora_actual, "Tipo": "Producción", "Desc": f"{cant_prod} Entrada {sabor_prod}", "Monto": 0
        })
        st.session_state.caja['litros_producidos'] += cant_prod
        st.success(f"✅ Stock actualizado: {sabor_prod} (+{cant_prod})")

# --- TAB 3: CORTE Y REPORTE ---
with tabs[2]:
    st.markdown("### 📈 Panel de Control")
    
    k1, k2, k3 = st.columns(3)
    k1.markdown(f"<div style='text-align:center; background:#FFF; padding:10px; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1)'><div style='font-size:0.9rem; color:#777'>Caja</div><div style='font-size:1.4rem; font-weight:bold; color:#D81B60'>${st.session_state.caja['dinero']:,.0f}</div></div>", unsafe_allow_html=True)
    k2.markdown(f"<div style='text-align:center; background:#FFF; padding:10px; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1)'><div style='font-size:0.9rem; color:#777'>Ventas</div><div style='font-size:1.4rem; font-weight:bold; color:#333'>{st.session_state.caja['litros_vendidos']}</div></div>", unsafe_allow_html=True)
    k3.markdown(f"<div style='text-align:center; background:#FFF; padding:10px; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1)'><div style='font-size:0.9rem; color:#777'>Prod</div><div style='font-size:1.4rem; font-weight:bold; color:#333'>{st.session_state.caja['litros_producidos']}</div></div>", unsafe_allow_html=True)
    
    st.divider()
    
    c_inv, c_hist = st.columns(2)
    
    with c_inv:
        st.markdown("#### 🧊 Inventario Visual")
        for index, row in st.session_state.inventario.sort_values('Sabor').iterrows():
            percent = min(100, row['Stock'])
            color_bar = "#D81B60" if row['Stock'] > 20 else "#E53935"
            st.markdown(f"""
            <div style="margin-bottom: 8px;">
                <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:0.8rem;">
                    <span>{row['Sabor']}</span>
                    <span>{row['Stock']}</span>
                </div>
                <div style="width:100%; background-color:#EEE; height:6px; border-radius:4px;">
                    <div style="width:{percent}%; background-color:{color_bar}; height:6px; border-radius:4px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)
        
    with c_hist:
        st.markdown("#### 📜 Historial de Ventas")
        if st.session_state.transacciones:
            df_trans = pd.DataFrame(st.session_state.transacciones)
            st.dataframe(df_trans.iloc[::-1], use_container_width=True, hide_index=True, height=300)
            
            csv = df_trans.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar CSV", data=csv, file_name=f"corte_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)
        else:
            st.info("Sin movimientos.")

    # ZONA DE CIERRE SEGURA (LÓGICA ANTERIOR MANTENIDA)
    st.markdown("---")
    with st.expander("🔐 Zona de Cierre de Caja"):
        st.warning("Para cerrar caja, primero descarga el reporte.")
        
        confirmar_seguridad = st.checkbox("Entiendo que al cerrar se reinicia el dinero a $0")
        
        if confirmar_seguridad:
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
                    st.session_state.caja = {'dinero': 0.0, 'litros_vendidos': 0, 'litros_producidos': 0}
                    st.session_state.transacciones = []
                    st.session_state.intento_cierre = False
                    st.success("✅ Día cerrado y caja reiniciada.")
                    time.sleep(1.5)
                    st.rerun()
                
                if col_cancel.button("Cancelar"):
                    st.session_state.intento_cierre = False
                    st.rerun()
