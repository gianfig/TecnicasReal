from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime

# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)  # Permitir CORS para el frontend

# Base de datos en memoria (para simplicidad)
tasks_db = []

# Endpoints de la API

@app.route('/')
def root():
    """Endpoint de bienvenida"""
    return jsonify({
        "message": "¡Bienvenido a la API de Tareas!", 
        "version": "1.0.0"
    })

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Obtener todas las tareas"""
    return jsonify(tasks_db)

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Obtener una tarea específica por ID"""
    for task in tasks_db:
        if task['id'] == task_id:
            return jsonify(task)
    return jsonify({"error": "Tarea no encontrada"}), 404

@app.route('/tasks', methods=['POST'])
def create_task():
    """Crear una nueva tarea"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Título es requerido"}), 400
    
    task = {
        'id': str(uuid.uuid4()),
        'title': data['title'],
        'description': data.get('description', ''),
        'completed': data.get('completed', False),
        'created_at': datetime.now().isoformat()
    }
    
    tasks_db.append(task)
    return jsonify(task), 201

@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Actualizar una tarea existente"""
    data = request.get_json()
    
    for i, task in enumerate(tasks_db):
        if task['id'] == task_id:
            if 'title' in data:
                task['title'] = data['title']
            if 'description' in data:
                task['description'] = data['description']
            if 'completed' in data:
                task['completed'] = data['completed']
            
            tasks_db[i] = task
            return jsonify(task)
    
    return jsonify({"error": "Tarea no encontrada"}), 404

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Eliminar una tarea"""
    for i, task in enumerate(tasks_db):
        if task['id'] == task_id:
            deleted_task = tasks_db.pop(i)
            return jsonify({
                "message": "Tarea eliminada", 
                "task": deleted_task
            })
    
    return jsonify({"error": "Tarea no encontrada"}), 404

@app.route('/tasks/completed', methods=['GET'])
def get_completed_tasks():
    """Obtener solo las tareas completadas"""
    completed = [task for task in tasks_db if task['completed']]
    return jsonify(completed)

@app.route('/tasks/pending', methods=['GET'])
def get_pending_tasks():
    """Obtener solo las tareas pendientes"""
    pending = [task for task in tasks_db if not task['completed']]
    return jsonify(pending)

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    print("📝 API de Tareas disponible en: http://localhost:5000")
    print("🌐 Abre index.html en tu navegador para usar la interfaz")
    app.run(host='0.0.0.0', port=5000, debug=True)
