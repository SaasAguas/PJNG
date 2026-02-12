<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>La Jalisciense - Sistema de Gestión</title>
    <style>
        :root {
            --primary: #007bff;
            --success: #28a745;
            --danger: #dc3545;
            --warning: #ffc107;
            --dark: #343a40;
            --light: #f8f9fa;
        }
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background-color: #f4f6f9; }
        
        /* Navegación */
        nav { background-color: var(--dark); padding: 1rem; color: white; display: flex; justify-content: space-between; align-items: center; }
        .nav-links button { background: none; border: none; color: white; font-size: 1rem; margin-left: 15px; cursor: pointer; padding: 5px 10px; }
        .nav-links button:hover, .nav-links button.active { background-color: rgba(255,255,255,0.2); border-radius: 5px; }

        /* Contenedores */
        .container { padding: 20px; max-width: 1200px; margin: 0 auto; display: none; }
        .active-section { display: block; }

        /* Tarjetas y UI General */
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }
        h2 { margin-top: 0; border-bottom: 2px solid var(--primary); padding-bottom: 10px; color: var(--dark); }
        .btn { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; color: white; }
        .btn-success { background-color: var(--success); }
        .btn-danger { background-color: var(--danger); }
        .btn-primary { background-color: var(--primary); }
        .btn-warning { background-color: var(--warning); color: #000; }
        
        /* Punto de Venta */
        .pos-layout { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        .filters { margin-bottom: 15px; }
        .flavor-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; }
        .flavor-btn { padding: 15px; border: 1px solid #ddd; background: white; cursor: pointer; border-radius: 8px; text-align: center; transition: 0.2s; }
        .flavor-btn:hover { border-color: var(--primary); background-color: #e9f5ff; }
        .flavor-btn.low-stock { border-color: var(--danger); color: var(--danger); }
        
        .cart-panel { background: white; padding: 15px; border-radius: 8px; height: fit-content; border: 1px solid #ddd; }
        .cart-item { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #eee; }
        
        /* Controles de Precio y Cantidad */
        .controls-row { display: flex; gap: 10px; margin-bottom: 15px; align-items: center; flex-wrap: wrap; }
        .price-options label { margin-right: 10px; cursor: pointer; }
        .qty-control { display: flex; align-items: center; }
        .qty-control input { width: 50px; text-align: center; font-size: 1.1rem; padding: 5px; margin: 0 5px; }
        .qty-btn { width: 30px; height: 30px; background: #ddd; border: none; cursor: pointer; font-weight: bold; }

        /* Panel de Control */
        .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px; }
        .stat-box { background: var(--dark); color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-box h3 { margin: 0; font-size: 2rem; }
        .stat-box p { margin: 0; opacity: 0.8; }

        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }
        th { background-color: #f1f1f1; }
    </style>
</head>
<body>

    <nav>
        <h1>La Jalisciense 🍦</h1>
        <div class="nav-links">
            <button onclick="showSection('pos')" class="active" id="btn-pos">Punto de Venta</button>
            <button onclick="showSection('production')" id="btn-production">Producción</button>
            <button onclick="showSection('admin')" id="btn-admin">Control e Inventario</button>
        </div>
    </nav>

    <div id="pos" class="container active-section">
        <div class="pos-layout">
            <div>
                <div class="card">
                    <div class="controls-row">
                        <div class="price-options">
                            <strong>Precio:</strong>
                            <input type="radio" name="price" value="20" checked id="p20"><label for="p20">$20 (Std)</label>
                            <input type="radio" name="price" value="16" id="p16"><label for="p16">$16</label>
                            <input type="radio" name="price" value="15" id="p15"><label for="p15">$15</label>
                        </div>
                        <div class="qty-control">
                            <strong>Litros:</strong>
                            <button class="qty-btn" onclick="adjustQty(-1)">-</button>
                            <input type="number" id="qty-input" value="1" min="1">
                            <button class="qty-btn" onclick="adjustQty(1)">+</button>
                        </div>
                    </div>

                    <div class="filters">
                        <button class="btn btn-primary" onclick="filterFlavors('all')">Todos</button>
                        <button class="btn btn-warning" onclick="filterFlavors('crema')">Crema</button>
                        <button class="btn btn-success" onclick="filterFlavors('fruta')">Fruta</button>
                    </div>

                    <div id="flavor-container" class="flavor-grid">
                        </div>
                </div>
            </div>

            <div class="cart-panel">
                <h3>🛒 Cuenta Actual</h3>
                <div id="cart-items">
                    <p style="color:#666; text-align:center;">Carrito vacío</p>
                </div>
                <hr>
                <div style="display: flex; justify-content: space-between; font-size: 1.2rem; font-weight: bold;">
                    <span>Total:</span>
                    <span id="cart-total">$0.00</span>
                </div>
                <button class="btn btn-success" style="width: 100%; margin-top: 15px;" onclick="finalizeSale()">Cobrar</button>
            </div>
        </div>
    </div>

    <div id="production" class="container">
        <div class="card" style="max-width: 600px; margin: 0 auto;">
            <h2>🏭 Registro de Producción</h2>
            <p>Agrega los litros fabricados al inventario.</p>
            
            <label>Sabor:</label>
            <select id="prod-flavor" style="width: 100%; padding: 10px; margin-bottom: 15px;">
                </select>

            <label>Cantidad (Litros):</label>
            <input type="number" id="prod-qty" style="width: 100%; padding: 10px; margin-bottom: 15px;" placeholder="Ej. 20">

            <button class="btn btn-primary" style="width: 100%;" onclick="addProduction()">Registrar Producción</button>
        </div>
    </div>

    <div id="admin" class="container">
        
        <div class="stats-grid">
            <div class="stat-box">
                <h3 id="stat-cash">$0</h3>
                <p>Dinero en Caja</p>
            </div>
            <div class="stat-box" style="background-color: var(--primary);">
                <h3 id="stat-sold">0 L</h3>
                <p>Litros Vendidos</p>
            </div>
            <div class="stat-box" style="background-color: var(--warning); color: black;">
                <h3 id="stat-produced">0 L</h3>
                <p>Litros Fabricados</p>
            </div>
        </div>

        <div class="card">
            <div style="display: flex; justify-content: space-between;">
                <h2>📦 Inventario Actual</h2>
                <button class="btn btn-danger" onclick="closeRegister()">🔒 Cierre de Caja (Reiniciar Día)</button>
            </div>
            <table id="inventory-table">
                <thead>
                    <tr><th>Sabor</th><th>Tipo</th><th>Stock (L)</th><th>Estado</th></tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>

        <div class="card">
            <div style="display: flex; justify-content: space-between;">
                <h2>📜 Historial de Movimientos</h2>
                <button class="btn btn-success" onclick="downloadCSV()">⬇ Descargar Excel</button>
            </div>
            <div style="max-height: 300px; overflow-y: auto;">
                <table id="history-table">
                    <thead>
                        <tr><th>Hora</th><th>Acción</th><th>Detalle</th><th>Monto</th></tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // --- BASE DE DATOS INICIAL ---
        // Aquí simulamos 50 sabores (pondré algunos de ejemplo y generaré el resto)
        let initialFlavors = [
            { name: "Limón", type: "fruta", stock: 50 },
            { name: "Fresa", type: "fruta", stock: 40 },
            { name: "Mango", type: "fruta", stock: 30 },
            { name: "Nuez", type: "crema", stock: 25 },
            { name: "Chocolate", type: "crema", stock: 20 },
            { name: "Vainilla", type: "crema", stock: 20 },
            { name: "Piña", type: "fruta", stock: 35 },
            { name: "Coco", type: "crema", stock: 15 }
        ];

        // Rellenar hasta 50 para el ejemplo
        for(let i=1; i<=42; i++) {
            initialFlavors.push({ 
                name: `Sabor ${i}`, 
                type: i % 2 === 0 ? "crema" : "fruta", 
                stock: 0 
            });
        }

        // --- ESTADO DEL SISTEMA ---
        let db = {
            inventory: JSON.parse(localStorage.getItem('inventory')) || initialFlavors,
            salesHistory: JSON.parse(localStorage.getItem('salesHistory')) || [],
            cash: parseFloat(localStorage.getItem('cash')) || 0,
            soldLiters: parseInt(localStorage.getItem('soldLiters')) || 0,
            producedLiters: parseInt(localStorage.getItem('producedLiters')) || 0
        };

        let cart = [];

        // --- FUNCIONES DE NAVEGACIÓN ---
        function showSection(sectionId) {
            document.querySelectorAll('.container').forEach(el => el.classList.remove('active-section'));
            document.getElementById(sectionId).classList.add('active-section');
            
            // Actualizar clases de botones
            document.querySelectorAll('.nav-links button').forEach(b => b.classList.remove('active'));
            document.getElementById(`btn-${sectionId}`).classList.add('active');

            if(sectionId === 'admin') renderAdmin();
            if(sectionId === 'production') renderProduction();
        }

        function saveData() {
            localStorage.setItem('inventory', JSON.stringify(db.
