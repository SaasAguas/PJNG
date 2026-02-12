import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import time

# ==========================================
# 1. CONFIGURACIÓN Y DATOS MAESTROS (REALES)
# ==========================================
st.set_page_config(page_title="La Jalisciense POS", page_icon="🥤", layout="centered")
TZ_CDMX = pytz.timezone('America/Mexico_City')

# --- CATÁLOGO REAL ---
SABORES_FRUTA = [
    "Jamaica", "Maracuya", "Ciruela", "Lima", "Fresa-Hierbabuena", "Fresa", 
    "Guayaba-Hierbabuena", "Guayaba-Fresa", "Piña-Alfalfa", "Guayaba", 
    "Lima-Albahaca", "Melon", "Hierbabuena-Limon", "Mango", "Limón-Alfalfa", 
    "Piña-Naranja", "Limón-Hierbabuena", "Piña-Hierbabuena", "Limon-Chia", 
    "Limon Con Pepino Y Hierbabuena", "Piña Naranja Hierbabuena", "Melon Citrico", "Lima-Stevia"
]
SABORES_CREMA = [
    "Horchata De Fresa", "Horchata Arroz", "Vainilla", "Mazapan", "Chai", 
    "Taro", "Coco Con Nuez", "Cebada", "Kalhua", "Crema Irlandesa"
]
PRODUCTOS_EXTRA = {
    "Paleta De Agua": 25, "Paleta De Leche": 30, "Sandwich": 20,
    "Campana": 20, "Frapuchino": 10, "Fresas Con Crema": 25
}

# Construcción del DataFrame Inicial con precios fijos para extras
datos = []
for s in SABORES_FRUTA: datos.append({"Sabor": s, "Categoría": "Fruta", "Stock": 50, "PrecioFijo": None})
for s in SABORES_CREMA: datos.append({"Sabor": s, "Categoría": "Crema", "Stock": 50, "PrecioFijo": None})
for p, precio in PRODUCTOS_EXTRA.items(): datos.append({"Sabor": p, "Categoría": "Extras", "Stock": 20, "PrecioFijo": precio})

CATALOGO_INICIAL = pd.DataFrame(datos)

# ==========================================
# 2. ESTILOS CSS (LIMPIO Y MODERNO)
# ==========================================
st.markdown("""
    <style>
    /* Forzar modo claro y fondo limpio */
    .stApp {
        background-color: #F8F5FA; /* Fondo muy suave casi blanco */
        color: #333;
    }
    h1 { color: #C2185B; font-weight: 900; text-align: center; margin-bottom: 0px; }
    
    /* Estilo de los Botones Grandes de Categoría */
    div.stButton > button[kind="secondary"] {
        background-color: white;
        color: #C2185B;
        border: 2px solid #C2185B;
        border-radius: 12px;
        height: 3.5em;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.2s;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #FCE4EC;
        border-color: #C2185B;
    }
    /* Estilo para botón activo (Simulado) */
    div.stButton > button[kind="secondary"]:focus {
         background-color: #C2185B;
         color: white;
    }

    /* Botón de Acción Principal (Cobrar/Agregar) */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #C2185B, #880E4F);
        color: white; border: none; border-radius: 12px;
        font-weight: 700; padding: 0.6rem 1rem; height: 3em;
    }

    /* Etiquetas y textos */
    .big-label { font-size: 1rem; font-weight: 700; color: #555; margin-bottom: -5px; display: block;}
    .stock-warning { color: #D32F2F; font-weight: bold; font-size: 0.9rem; }
    .stock-ok { color: #388E3C; font-weight: bold; font-size: 0.9rem; }

    /* Tarjetas de Carrito */
    .cart-item {
        background: white; padding: 12px; border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 8px;
        border-left: 5px solid #C2185B; display: flex; justify-content: space-between; align-items: center;
    }
    .cart-title { font-weight: 700; font-size: 1rem; }
    .cart-price { font-weight: 900; font-size: 1.2rem; color: #C2185B; }
    
    .block-container { padding-top: 2rem; }
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
    if 'transacciones' not in st.session_state:
        st.session_state.transacciones = []
    if 'cat_activa' not in st.session_state:
        st.session_state.cat_activa = "Fruta" # Categoría inicial

init_session()

# ==========================================
# 4. INTERFAZ
# ==========================================
st.write("<h1>La Jalisciense <span style='font-size:1rem; color: #BDBDBD'>| POS</span></h1>", unsafe_allow_html=True)
tabs = st.tabs(["🛒 VENTA", "🏗️ PRODUCCIÓN", "📊 REPORTES"])

# --- TAB 1: VENTA ---
with tabs[0]:
    # 1. BOTONES GRANDES DE CATEGORÍA
    c1, c2, c3 = st.columns(3)
    if c1.button("🍉 FRUTA", key="btn_fruta", use_container_width=True, type="secondary" if st.session_state.cat_activa != "Fruta" else "primary"): 
        st.session_state.cat_activa = "Fruta"
        st.rerun()
    if c2.button("🥛 CREMA", key="btn_crema", use_container_width=True, type="secondary" if st.session_state.cat_activa != "Crema" else "primary"): 
        st.session_state.cat_activa = "Crema"
        st.rerun()
    if c3.button("🍪 EXTRAS", key="btn_extras", use_container_width=True, type="secondary" if st.session_state.cat_activa != "Extras" else "primary"): 
        st.session_state.cat_activa = "Extras"
        st.rerun()
    
    st.divider()

    # 2. SELECCIÓN DE PRODUCTO
    col_sel, col_datos = st.columns([1.5, 1])
    
    # Filtrar inventario por la categoría activa
    df_filtro = st.session_state.inventario[st.session_state.inventario['Categoría'] == st.session_state.cat_activa]
    
    with col_sel:
        st.markdown(f'<span class="big-label">Seleccionar {st.session_state.cat_activa}:</span>', unsafe_allow_html=True)
        sabor_sel = st.selectbox("Sabor:", df_filtro['Sabor'], label_visibility="collapsed")
        
        # Stock Info
        item_data = df_filtro[df_filtro['Sabor'] == sabor_sel].iloc[0]
        stock_disp = item_data['Stock']
        if stock_disp < 15: st.markdown(f'<span class="stock-warning">⚠️ Quedan {stock_disp}</span>', unsafe_allow_html=True)
        else: st.markdown(f'<span class="stock-ok">✅ Stock: {stock_disp}</span>', unsafe_allow_html=True)

    with col_datos:
        # Lógica de Precios (Variable vs Fijo)
        if st.session_state.cat_activa == "Extras":
            st.markdown('<span class="big-label">Precio:</span>', unsafe_allow_html=True)
            precio_final = st.number_input("Precio Fijo", value=item_data['PrecioFijo'], disabled=True, label_visibility="collapsed")
            st.markdown('<span class="big-label">Piezas:</span>', unsafe_allow_html=True)
            cantidad = st.number_input("Cant:", min_value=1, value=1, label_visibility="collapsed")
            unidad = "Pza"
        else:
            st.markdown('<span class="big-label">Precio/Lt:</span>', unsafe_allow_html=True)
            precio_final = st.selectbox("Precio", [20, 16, 15], label_visibility="collapsed")
            st.markdown('<span class="big-label">Litros:</span>', unsafe_allow_html=True)
            cantidad = st.number_input("Litros:", min_value=1, value=1, label_visibility="collapsed")
            unidad = "Lt"

    if st.button("➕ AGREGAR AL PEDIDO", use_container_width=True, type="primary"):
        if stock_disp >= cantidad:
            st.session_state.carrito.append({
                "Producto": sabor_sel, "Cant": cantidad, "Unidad": unidad,
                "PrecioU": precio_final, "Total": cantidad * precio_final
            })
            st.toast(f"Agregado: {sabor_sel}")
        else:
            st.error("Stock insuficiente")

    # 3. CARRITO Y COBRO
    if st.session_state.carrito:
        st.divider()
        st.markdown("### 🧾 Pedido Actual")
        total_pedido = 0
        for item in st.session_state.carrito:
            total_pedido += item['Total']
            st.markdown(f"""
            <div class="cart-item">
                <div>
                    <div class="cart-title">{item['Producto']}</div>
                    <div style="color:#666; font-size:0.9rem;">{item['Cant']} {item['Unidad']} x ${item['PrecioU']}</div>
                </div>
                <div class="cart-price">${item['Total']}</div>
            </div>""", unsafe_allow_html=True)
        
        st.markdown(f"<div style='text-align:right; font-size:1.8rem; font-weight:900; color:#C2185B;'>Total: ${total_pedido}</div>", unsafe_allow_html=True)
        
        c_pay, c_del = st.columns([3, 1])
        if c_pay.button("✅ COBRAR AHORA", type="primary", use_container_width=True):
            hora = datetime.now(TZ_CDMX).strftime("%H:%M:%S")
            for item in st.session_state.carrito:
                idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == item['Producto']].index[0]
                st.session_state.inventario.at[idx, 'Stock'] -= item['Cant']
                st.session_state.caja['dinero'] += item['Total']
                st.session_state.caja['items'] += item['Cant']
                st.session_state.transacciones.append({"Hora": hora, "Tipo": "Venta", "Desc": f"{item['Cant']}{item['Unidad']} {item['Producto']}", "Monto": item['Total']})
            
            st.session_state.carrito = []
            st.balloons()
            st.success("¡Venta Cobrada!")
            time.sleep(0.5)
            st.rerun()

        if c_del.button("🗑️ Limpiar"):
            st.session_state.carrito = []
            st.rerun()

# --- TAB 2: PRODUCCIÓN ---
with tabs[1]:
    st.markdown("### 🏭 Entrada de Almacén")
    c_prod, c_cant = st.columns([1.5, 1])
    with c_prod:
        st.markdown('<span class="big-label">Producto:</span>', unsafe_allow_html=True)
        sabor_p = st.selectbox("Prod", st.session_state.inventario['Sabor'], label_visibility="collapsed")
    with c_cant:
        st.markdown('<span class="big-label">Cantidad Entrada:</span>', unsafe_allow_html=True)
        cant_p = st.number_input("Cant P", 1, 500, 50, label_visibility="collapsed")
        
    if st.button("📥 REGISTRAR ENTRADA", use_container_width=True, type="primary"):
        idx = st.session_state.inventario[st.session_state.inventario['Sabor'] == sabor_p].index[0]
        st.session_state.inventario.at[idx, 'Stock'] += cant_p
        hora = datetime.now(TZ_CDMX).strftime("%H:%M:%S")
        st.session_state.transacciones.append({"Hora": hora, "Tipo": "Producción", "Desc": f"{cant_p} Entrada {sabor_p}", "Monto": 0})
        st.success(f"Stock actualizado: {sabor_p}")

# --- TAB 3: REPORTES ---
with tabs[2]:
    st.markdown("### 📈 Corte del Día")
    k1, k2 = st.columns(2)
    k1.metric("Dinero en Caja", f"${st.session_state.caja['dinero']}")
    k2.metric("Items Vendidos", f"{st.session_state.caja['items']}")
    
    st.divider()
    
    c_hist, c_inv = st.columns(2)
    with c_hist:
        st.markdown("#### 📜 Historial")
        if st.session_state.transacciones:
            df_t = pd.DataFrame(st.session_state.transacciones)
            st.dataframe(df_t.iloc[::-1], use_container_width=True, hide_index=True, height=250)
            csv = df_t.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar CSV", csv, "corte.csv", "text/csv", use_container_width=True)
        else: st.info("Sin movimientos")
        
    with c_inv:
        st.markdown("#### 🧊 Inventario")
        st.dataframe(st.session_state.inventario[['Sabor', 'Stock']], use_container_width=True, hide_index=True, height=250)

    st.divider()
    with st.expander("🔐 Cierre Seguro de Caja"):
        st.warning("Requiere confirmación doble.")
        if st.checkbox("Estoy seguro de cerrar el turno"):
            if st.button("🔴 CONFIRMAR CIERRE FINAL", type="primary"):
                st.session_state.caja = {'dinero': 0.0, 'items': 0}
                st.session_state.transacciones = []
                st.success("Caja reiniciada a $0")
                time.sleep(1)
                st.rerun()
