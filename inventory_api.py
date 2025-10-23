from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
import uuid
from datetime import datetime
from decimal import Decimal

# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)  # Permitir CORS para el frontend

# Configuración de la base de datos SQL Server
DB_CONFIG = {
    'server': 'DESKTOP-T14SCLD\\SQLEXPRESS',
    'database': 'InventarioDB',
    'trusted_connection': 'yes',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

def get_db_connection():
    """Crear conexión a la base de datos"""
    try:
        connection_string = f"""
        DRIVER={DB_CONFIG['driver']};
        SERVER={DB_CONFIG['server']};
        DATABASE={DB_CONFIG['database']};
        Trusted_Connection={DB_CONFIG['trusted_connection']};
        """
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def init_database():
    """Verificar conexión a la base de datos"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Categorias")
            count = cursor.fetchone()[0]
            print(f"✅ Conexión exitosa a InventarioDB. Categorías encontradas: {count}")
            conn.close()
            return True
        except Exception as e:
            print(f"Error verificando base de datos: {e}")
            conn.close()
            return False
    return False

# Inicializar la base de datos al arrancar
init_database()

# ==================== ENDPOINTS DE CATEGORÍAS ====================

@app.route('/')
def root():
    """Endpoint de bienvenida"""
    return jsonify({
        "message": "¡Bienvenido al Sistema de Gestión de Inventario!",
        "version": "1.0.0",
        "database": "SQL Server - InventarioDB"
    })

@app.route('/categorias', methods=['GET'])
def get_categorias():
    """Obtener todas las categorías"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, descripcion, fecha_creacion FROM Categorias ORDER BY nombre")
        
        categorias = []
        for row in cursor.fetchall():
            categorias.append({
                'id': row[0],
                'nombre': row[1],
                'descripcion': row[2] or '',
                'fecha_creacion': row[3].isoformat()
            })
        
        conn.close()
        return jsonify(categorias)
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error obteniendo categorías: {str(e)}"}), 500

@app.route('/categorias', methods=['POST'])
def create_categoria():
    """Crear una nueva categoría"""
    data = request.get_json()
    
    if not data or 'nombre' not in data:
        return jsonify({"error": "Nombre es requerido"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Categorias (nombre, descripcion)
            VALUES (?, ?)
        """, data['nombre'], data.get('descripcion', ''))
        
        conn.commit()
        
        # Obtener el ID de la categoría insertada usando el nombre
        cursor.execute("""
            SELECT TOP 1 id FROM Categorias 
            WHERE nombre = ?
            ORDER BY id DESC
        """, data['nombre'])
        result = cursor.fetchone()
        categoria_id = result[0] if result else None
        
        # Obtener la categoría creada
        cursor.execute("SELECT id, nombre, descripcion, fecha_creacion FROM Categorias WHERE id = ?", categoria_id)
        row = cursor.fetchone()
        
        categoria = {
            'id': row[0],
            'nombre': row[1],
            'descripcion': row[2] or '',
            'fecha_creacion': row[3].isoformat()
        }
        
        conn.close()
        return jsonify(categoria), 201
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error creando categoría: {str(e)}"}), 500

@app.route('/categorias/<int:categoria_id>', methods=['DELETE'])
def delete_categoria(categoria_id):
    """Eliminar una categoría (marcar como inactiva)"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verificar si la categoría existe
        cursor.execute("SELECT COUNT(*) FROM Categorias WHERE id = ?", categoria_id)
        if cursor.fetchone()[0] == 0:
            conn.close()
            return jsonify({"error": "Categoría no encontrada"}), 404
        
        # Verificar si hay productos usando esta categoría
        cursor.execute("SELECT COUNT(*) FROM Productos WHERE categoria_id = ? AND activo = 1", categoria_id)
        productos_count = cursor.fetchone()[0]
        
        if productos_count > 0:
            conn.close()
            return jsonify({"error": f"No se puede eliminar la categoría. Hay {productos_count} productos activos usando esta categoría."}), 400
        
        # Eliminar físicamente (temporal hasta agregar campo activo)
        cursor.execute("DELETE FROM Categorias WHERE id = ?", categoria_id)
        conn.commit()
        
        conn.close()
        return jsonify({"message": "Categoría eliminada exitosamente"})
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error eliminando categoría: {str(e)}"}), 500

# ==================== ENDPOINTS DE PROVEEDORES ====================

@app.route('/proveedores', methods=['GET'])
def get_proveedores():
    """Obtener todos los proveedores"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, contacto, email, telefono, direccion, fecha_creacion FROM Proveedores ORDER BY nombre")
        
        proveedores = []
        for row in cursor.fetchall():
            proveedores.append({
                'id': row[0],
                'nombre': row[1],
                'contacto': row[2] or '',
                'email': row[3] or '',
                'telefono': row[4] or '',
                'direccion': row[5] or '',
                'fecha_creacion': row[6].isoformat()
            })
        
        conn.close()
        return jsonify(proveedores)
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error obteniendo proveedores: {str(e)}"}), 500

@app.route('/proveedores', methods=['POST'])
def create_proveedor():
    """Crear un nuevo proveedor"""
    data = request.get_json()
    
    if not data or 'nombre' not in data:
        return jsonify({"error": "Nombre es requerido"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Proveedores (nombre, contacto, email, telefono, direccion)
            VALUES (?, ?, ?, ?, ?)
        """, data['nombre'], data.get('contacto', ''), data.get('email', ''),
             data.get('telefono', ''), data.get('direccion', ''))
        
        conn.commit()
        
        # Obtener el ID del proveedor insertado usando el nombre
        cursor.execute("""
            SELECT TOP 1 id FROM Proveedores 
            WHERE nombre = ?
            ORDER BY id DESC
        """, data['nombre'])
        result = cursor.fetchone()
        proveedor_id = result[0] if result else None
        
        # Obtener el proveedor creado
        cursor.execute("SELECT id, nombre, contacto, email, telefono, direccion, fecha_creacion FROM Proveedores WHERE id = ?", proveedor_id)
        row = cursor.fetchone()
        
        proveedor = {
            'id': row[0],
            'nombre': row[1],
            'contacto': row[2] or '',
            'email': row[3] or '',
            'telefono': row[4] or '',
            'direccion': row[5] or '',
            'fecha_creacion': row[6].isoformat()
        }
        
        conn.close()
        return jsonify(proveedor), 201
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error creando proveedor: {str(e)}"}), 500

@app.route('/proveedores/<int:proveedor_id>', methods=['DELETE'])
def delete_proveedor(proveedor_id):
    """Eliminar un proveedor (marcar como inactivo)"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verificar si el proveedor existe
        cursor.execute("SELECT COUNT(*) FROM Proveedores WHERE id = ?", proveedor_id)
        if cursor.fetchone()[0] == 0:
            conn.close()
            return jsonify({"error": "Proveedor no encontrado"}), 404
        
        # Verificar si hay productos usando este proveedor
        cursor.execute("SELECT COUNT(*) FROM Productos WHERE proveedor_id = ? AND activo = 1", proveedor_id)
        productos_count = cursor.fetchone()[0]
        
        if productos_count > 0:
            conn.close()
            return jsonify({"error": f"No se puede eliminar el proveedor. Hay {productos_count} productos activos usando este proveedor."}), 400
        
        # Eliminar físicamente (temporal hasta agregar campo activo)
        cursor.execute("DELETE FROM Proveedores WHERE id = ?", proveedor_id)
        conn.commit()
        
        conn.close()
        return jsonify({"message": "Proveedor eliminado exitosamente"})
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error eliminando proveedor: {str(e)}"}), 500

# ==================== ENDPOINTS DE PRODUCTOS ====================

@app.route('/productos', methods=['GET'])
def get_productos():
    """Obtener todos los productos con información de categoría y proveedor"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.nombre, p.descripcion, p.codigo_sku, p.precio,
                   p.cantidad_stock, p.stock_minimo, p.activo, p.fecha_creacion,
                   c.nombre as categoria_nombre, pr.nombre as proveedor_nombre,
                   p.categoria_id, p.proveedor_id
            FROM Productos p
            LEFT JOIN Categorias c ON p.categoria_id = c.id
            LEFT JOIN Proveedores pr ON p.proveedor_id = pr.id
            WHERE p.activo = 1
            ORDER BY p.nombre
        """)
        
        productos = []
        for row in cursor.fetchall():
            productos.append({
                'id': row[0],
                'nombre': row[1],
                'descripcion': row[2] or '',
                'codigo_sku': row[3] or '',
                'precio': float(row[4]),
                'cantidad_stock': row[5],
                'stock_minimo': row[6],
                'activo': bool(row[7]),
                'fecha_creacion': row[8].isoformat(),
                'categoria_nombre': row[9] or '',
                'proveedor_nombre': row[10] or '',
                'categoria_id': row[11],
                'proveedor_id': row[12]
            })
        
        conn.close()
        return jsonify(productos)
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error obteniendo productos: {str(e)}"}), 500

@app.route('/debug/productos-categorias', methods=['GET'])
def debug_productos_categorias():
    """Debug: Ver productos con sus categorías"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.nombre, p.categoria_id, c.nombre as categoria_nombre
            FROM Productos p
            LEFT JOIN Categorias c ON p.categoria_id = c.id
            ORDER BY p.categoria_id
        """)
        rows = cursor.fetchall()
        
        productos = []
        for row in rows:
            productos.append({
                'producto': row[0],
                'categoria_id': row[1],
                'categoria_nombre': row[2]
            })
        
        conn.close()
        return jsonify(productos)
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error: {str(e)}"}), 500

@app.route('/productos/<int:producto_id>', methods=['GET'])
def get_producto(producto_id):
    """Obtener un producto específico por ID"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.nombre, p.descripcion, p.codigo_sku, p.precio,
                   p.cantidad_stock, p.stock_minimo, p.activo, p.fecha_creacion,
                   c.nombre as categoria_nombre, pr.nombre as proveedor_nombre,
                   p.categoria_id, p.proveedor_id
            FROM Productos p
            LEFT JOIN Categorias c ON p.categoria_id = c.id
            LEFT JOIN Proveedores pr ON p.proveedor_id = pr.id
            WHERE p.id = ? AND p.activo = 1
        """, producto_id)
        row = cursor.fetchone()
        
        if row:
            producto = {
                'id': row[0],
                'nombre': row[1],
                'descripcion': row[2] or '',
                'codigo_sku': row[3] or '',
                'precio': float(row[4]),
                'cantidad_stock': row[5],
                'stock_minimo': row[6],
                'activo': bool(row[7]),
                'fecha_creacion': row[8].isoformat(),
                'categoria_nombre': row[9] or '',
                'proveedor_nombre': row[10] or '',
                'categoria_id': row[11],
                'proveedor_id': row[12]
            }
            conn.close()
            return jsonify(producto)
        else:
            conn.close()
            return jsonify({"error": "Producto no encontrado"}), 404
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error obteniendo producto: {str(e)}"}), 500

@app.route('/productos', methods=['POST'])
def create_producto():
    """Crear un nuevo producto"""
    data = request.get_json()
    
    if not data or 'nombre' not in data or 'categoria_id' not in data:
        return jsonify({"error": "Nombre y categoría son requeridos"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Productos (nombre, descripcion, codigo_sku, precio,
                                 cantidad_stock, stock_minimo, categoria_id, proveedor_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, data['nombre'], data.get('descripcion', ''), data.get('codigo_sku', ''),
             data.get('precio', 0), data.get('cantidad_stock', 0),
             data.get('stock_minimo', 5), data['categoria_id'], data.get('proveedor_id'))
        
        conn.commit()
        
        # Obtener el ID del producto insertado usando el nombre y SKU
        cursor.execute("""
            SELECT TOP 1 id FROM Productos 
            WHERE nombre = ? AND codigo_sku = ?
            ORDER BY id DESC
        """, data['nombre'], data.get('codigo_sku', ''))
        result = cursor.fetchone()
        producto_id = result[0] if result else None
        
        # Obtener el producto creado con información de categoría y proveedor
        cursor.execute("""
            SELECT p.id, p.nombre, p.descripcion, p.codigo_sku, p.precio,
                   p.cantidad_stock, p.stock_minimo, p.activo, p.fecha_creacion,
                   c.nombre as categoria_nombre, pr.nombre as proveedor_nombre,
                   p.categoria_id, p.proveedor_id
            FROM Productos p
            LEFT JOIN Categorias c ON p.categoria_id = c.id
            LEFT JOIN Proveedores pr ON p.proveedor_id = pr.id
            WHERE p.id = ?
        """, producto_id)
        row = cursor.fetchone()
        
        producto = {
            'id': row[0],
            'nombre': row[1],
            'descripcion': row[2] or '',
            'codigo_sku': row[3] or '',
            'precio': float(row[4]),
            'cantidad_stock': row[5],
            'stock_minimo': row[6],
            'activo': bool(row[7]),
            'fecha_creacion': row[8].isoformat(),
            'categoria_nombre': row[9] or '',
            'proveedor_nombre': row[10] or '',
            'categoria_id': row[11],
            'proveedor_id': row[12]
        }
        
        conn.close()
        return jsonify(producto), 201
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error creando producto: {str(e)}"}), 500

@app.route('/productos/<int:producto_id>', methods=['PUT'])
def update_producto(producto_id):
    """Actualizar un producto existente"""
    data = request.get_json()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verificar si el producto existe
        cursor.execute("SELECT COUNT(*) FROM Productos WHERE id = ?", producto_id)
        if cursor.fetchone()[0] == 0:
            conn.close()
            return jsonify({"error": "Producto no encontrado"}), 404
        
        # Actualizar el producto
        cursor.execute("""
            UPDATE Productos 
            SET nombre = ?, descripcion = ?, codigo_sku = ?, precio = ?,
                cantidad_stock = ?, stock_minimo = ?, categoria_id = ?, proveedor_id = ?,
                fecha_actualizacion = ?
            WHERE id = ?
        """, data.get('nombre'), data.get('descripcion', ''), data.get('codigo_sku', ''),
             data.get('precio', 0), data.get('cantidad_stock', 0),
             data.get('stock_minimo', 5), data.get('categoria_id'), data.get('proveedor_id'),
             datetime.now(), producto_id)
        
        conn.commit()
        
        # Obtener el producto actualizado
        cursor.execute("""
            SELECT p.id, p.nombre, p.descripcion, p.codigo_sku, p.precio,
                   p.cantidad_stock, p.stock_minimo, p.activo, p.fecha_creacion,
                   c.nombre as categoria_nombre, pr.nombre as proveedor_nombre
            FROM Productos p
            LEFT JOIN Categorias c ON p.categoria_id = c.id
            LEFT JOIN Proveedores pr ON p.proveedor_id = pr.id
            WHERE p.id = ?
        """, producto_id)
        row = cursor.fetchone()
        
        producto = {
            'id': row[0],
            'nombre': row[1],
            'descripcion': row[2] or '',
            'codigo_sku': row[3] or '',
            'precio': float(row[4]),
            'cantidad_stock': row[5],
            'stock_minimo': row[6],
            'activo': bool(row[7]),
            'fecha_creacion': row[8].isoformat(),
            'categoria_nombre': row[9] or '',
            'proveedor_nombre': row[10] or ''
        }
        
        conn.close()
        return jsonify(producto)
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error actualizando producto: {str(e)}"}), 500

@app.route('/productos/<int:producto_id>', methods=['DELETE'])
def delete_producto(producto_id):
    """Eliminar un producto (marcar como inactivo)"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verificar si el producto existe
        cursor.execute("SELECT COUNT(*) FROM Productos WHERE id = ?", producto_id)
        if cursor.fetchone()[0] == 0:
            conn.close()
            return jsonify({"error": "Producto no encontrado"}), 404
        
        # Marcar como inactivo en lugar de eliminar
        cursor.execute("UPDATE Productos SET activo = 0 WHERE id = ?", producto_id)
        conn.commit()
        
        conn.close()
        return jsonify({"message": "Producto eliminado (marcado como inactivo)"})
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error eliminando producto: {str(e)}"}), 500

# ==================== ENDPOINTS DE MOVIMIENTOS DE STOCK ====================

@app.route('/movimientos', methods=['GET'])
def get_movimientos():
    """Obtener todos los movimientos de stock"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, m.producto_id, p.nombre as producto_nombre, m.tipo_movimiento,
                   m.cantidad, m.motivo, m.numero_referencia, m.fecha_movimiento
            FROM MovimientosStock m
            LEFT JOIN Productos p ON m.producto_id = p.id
            ORDER BY m.fecha_movimiento DESC
        """)
        
        movimientos = []
        for row in cursor.fetchall():
            movimientos.append({
                'id': row[0],
                'producto_id': row[1],
                'producto_nombre': row[2] or '',
                'tipo_movimiento': row[3],
                'cantidad': row[4],
                'motivo': row[5] or '',
                'numero_referencia': row[6] or '',
                'fecha_movimiento': row[7].isoformat()
            })
        
        conn.close()
        return jsonify(movimientos)
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error obteniendo movimientos: {str(e)}"}), 500

@app.route('/movimientos', methods=['POST'])
def create_movimiento():
    """Crear un nuevo movimiento de stock"""
    data = request.get_json()
    
    if not data or 'producto_id' not in data or 'tipo_movimiento' not in data or 'cantidad' not in data:
        return jsonify({"error": "Producto, tipo de movimiento y cantidad son requeridos"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verificar que el producto existe
        cursor.execute("SELECT COUNT(*) FROM Productos WHERE id = ?", data['producto_id'])
        if cursor.fetchone()[0] == 0:
            conn.close()
            return jsonify({"error": "Producto no encontrado"}), 404
        
        # Crear el movimiento
        cursor.execute("""
            INSERT INTO MovimientosStock (producto_id, tipo_movimiento, cantidad, motivo, numero_referencia)
            VALUES (?, ?, ?, ?, ?)
        """, data['producto_id'], data['tipo_movimiento'], data['cantidad'],
             data.get('motivo', ''), data.get('numero_referencia', ''))
        
        # Actualizar el stock del producto
        if data['tipo_movimiento'] == 'ENTRADA':
            cursor.execute("UPDATE Productos SET cantidad_stock = cantidad_stock + ? WHERE id = ?", 
                         data['cantidad'], data['producto_id'])
        else:  # SALIDA
            cursor.execute("UPDATE Productos SET cantidad_stock = cantidad_stock - ? WHERE id = ?", 
                         data['cantidad'], data['producto_id'])
        
        conn.commit()
        movimiento_id = cursor.lastrowid
        
        # Obtener el movimiento creado
        cursor.execute("""
            SELECT m.id, m.producto_id, p.nombre as producto_nombre, m.tipo_movimiento,
                   m.cantidad, m.motivo, m.numero_referencia, m.fecha_movimiento
            FROM MovimientosStock m
            LEFT JOIN Productos p ON m.producto_id = p.id
            WHERE m.id = ?
        """, movimiento_id)
        row = cursor.fetchone()
        
        movimiento = {
            'id': row[0],
            'producto_id': row[1],
            'producto_nombre': row[2] or '',
            'tipo_movimiento': row[3],
            'cantidad': row[4],
            'motivo': row[5] or '',
            'numero_referencia': row[6] or '',
            'fecha_movimiento': row[7].isoformat()
        }
        
        conn.close()
        return jsonify(movimiento), 201
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error creando movimiento: {str(e)}"}), 500

# ==================== ENDPOINTS DE REPORTES ====================

@app.route('/reportes/stock-bajo', methods=['GET'])
def get_stock_bajo():
    """Obtener productos con stock bajo"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.nombre, p.codigo_sku, p.cantidad_stock, p.stock_minimo,
                   c.nombre as categoria_nombre
            FROM Productos p
            LEFT JOIN Categorias c ON p.categoria_id = c.id
            WHERE p.cantidad_stock <= p.stock_minimo AND p.activo = 1
            ORDER BY (p.cantidad_stock - p.stock_minimo) ASC
        """)
        
        productos = []
        for row in cursor.fetchall():
            productos.append({
                'id': row[0],
                'nombre': row[1],
                'codigo_sku': row[2] or '',
                'cantidad_stock': row[3],
                'stock_minimo': row[4],
                'categoria_nombre': row[5] or '',
                'diferencia': row[3] - row[4]
            })
        
        conn.close()
        return jsonify(productos)
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error obteniendo stock bajo: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Iniciando Sistema de Gestión de Inventario...")
    print("📝 API disponible en: http://localhost:5000")
    print("🗄️ Base de datos: SQL Server - InventarioDB")
    print("🌐 Abre inventory.html en tu navegador para usar la interfaz")
    app.run(host='0.0.0.0', port=5000, debug=True)
