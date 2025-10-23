from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
import uuid
from datetime import datetime

# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)  # Permitir CORS para el frontend

# Configuración de la base de datos SQL Server
# Ajusta estos valores según tu configuración
DB_CONFIG = {
    'server': 'DESKTOP-T14SCLD\\SQLEXPRESS',  # Tu instancia de SQL Server
    'database': 'TasksDB',
    'trusted_connection': 'yes',  # Usar autenticación de Windows
    'driver': '{ODBC Driver 17 for SQL Server}'  # o la versión que tengas
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
    """Inicializar la base de datos si no existe la tabla"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Verificar si la tabla existe
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'Tasks'
            """)
            if cursor.fetchone()[0] == 0:
                # Crear la tabla si no existe
                cursor.execute("""
                    CREATE TABLE Tasks (
                        id NVARCHAR(50) PRIMARY KEY,
                        title NVARCHAR(255) NOT NULL,
                        description NVARCHAR(MAX),
                        completed BIT NOT NULL DEFAULT 0,
                        created_at DATETIME2 NOT NULL DEFAULT GETDATE()
                    )
                """)
                conn.commit()
                print("✅ Tabla Tasks creada exitosamente")
            else:
                print("✅ Tabla Tasks ya existe")
            conn.close()
        except Exception as e:
            print(f"Error inicializando base de datos: {e}")

# Inicializar la base de datos al arrancar
init_database()

# Endpoints de la API

@app.route('/')
def root():
    """Endpoint de bienvenida"""
    return jsonify({
        "message": "¡Bienvenido a la API de Tareas con SQL Server!", 
        "version": "2.0.0",
        "database": "SQL Server"
    })

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Obtener todas las tareas"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, completed, created_at FROM Tasks ORDER BY created_at DESC")
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row[0],
                'title': row[1],
                'description': row[2] or '',
                'completed': bool(row[3]),
                'created_at': row[4].isoformat()
            })
        
        conn.close()
        return jsonify(tasks)
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error obteniendo tareas: {str(e)}"}), 500

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Obtener una tarea específica por ID"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, completed, created_at FROM Tasks WHERE id = ?", task_id)
        row = cursor.fetchone()
        
        if row:
            task = {
                'id': row[0],
                'title': row[1],
                'description': row[2] or '',
                'completed': bool(row[3]),
                'created_at': row[4].isoformat()
            }
            conn.close()
            return jsonify(task)
        else:
            conn.close()
            return jsonify({"error": "Tarea no encontrada"}), 404
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error obteniendo tarea: {str(e)}"}), 500

@app.route('/tasks', methods=['POST'])
def create_task():
    """Crear una nueva tarea"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Título es requerido"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        task_id = str(uuid.uuid4())
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Tasks (id, title, description, completed, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, task_id, data['title'], data.get('description', ''), 
             data.get('completed', False), datetime.now())
        
        conn.commit()
        
        # Obtener la tarea creada
        cursor.execute("SELECT id, title, description, completed, created_at FROM Tasks WHERE id = ?", task_id)
        row = cursor.fetchone()
        
        task = {
            'id': row[0],
            'title': row[1],
            'description': row[2] or '',
            'completed': bool(row[3]),
            'created_at': row[4].isoformat()
        }
        
        conn.close()
        return jsonify(task), 201
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error creando tarea: {str(e)}"}), 500

@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Actualizar una tarea existente"""
    data = request.get_json()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verificar si la tarea existe
        cursor.execute("SELECT COUNT(*) FROM Tasks WHERE id = ?", task_id)
        if cursor.fetchone()[0] == 0:
            conn.close()
            return jsonify({"error": "Tarea no encontrada"}), 404
        
        # Actualizar la tarea
        cursor.execute("""
            UPDATE Tasks 
            SET title = ?, description = ?, completed = ?
            WHERE id = ?
        """, data.get('title'), data.get('description', ''), 
             data.get('completed', False), task_id)
        
        conn.commit()
        
        # Obtener la tarea actualizada
        cursor.execute("SELECT id, title, description, completed, created_at FROM Tasks WHERE id = ?", task_id)
        row = cursor.fetchone()
        
        task = {
            'id': row[0],
            'title': row[1],
            'description': row[2] or '',
            'completed': bool(row[3]),
            'created_at': row[4].isoformat()
        }
        
        conn.close()
        return jsonify(task)
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error actualizando tarea: {str(e)}"}), 500

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Eliminar una tarea"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Obtener la tarea antes de eliminarla
        cursor.execute("SELECT id, title, description, completed, created_at FROM Tasks WHERE id = ?", task_id)
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({"error": "Tarea no encontrada"}), 404
        
        deleted_task = {
            'id': row[0],
            'title': row[1],
            'description': row[2] or '',
            'completed': bool(row[3]),
            'created_at': row[4].isoformat()
        }
        
        # Eliminar la tarea
        cursor.execute("DELETE FROM Tasks WHERE id = ?", task_id)
        conn.commit()
        
        conn.close()
        return jsonify({
            "message": "Tarea eliminada",
            "task": deleted_task
        })
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error eliminando tarea: {str(e)}"}), 500

@app.route('/tasks/completed', methods=['GET'])
def get_completed_tasks():
    """Obtener solo las tareas completadas"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, completed, created_at FROM Tasks WHERE completed = 1 ORDER BY created_at DESC")
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row[0],
                'title': row[1],
                'description': row[2] or '',
                'completed': bool(row[3]),
                'created_at': row[4].isoformat()
            })
        
        conn.close()
        return jsonify(tasks)
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error obteniendo tareas completadas: {str(e)}"}), 500

@app.route('/tasks/pending', methods=['GET'])
def get_pending_tasks():
    """Obtener solo las tareas pendientes"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, completed, created_at FROM Tasks WHERE completed = 0 ORDER BY created_at DESC")
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row[0],
                'title': row[1],
                'description': row[2] or '',
                'completed': bool(row[3]),
                'created_at': row[4].isoformat()
            })
        
        conn.close()
        return jsonify(tasks)
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Error obteniendo tareas pendientes: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask con SQL Server...")
    print("📝 API de Tareas disponible en: http://localhost:5000")
    print("🗄️ Base de datos: SQL Server - TasksDB")
    print("🌐 Abre index.html en tu navegador para usar la interfaz")
    app.run(host='0.0.0.0', port=5000, debug=True)
