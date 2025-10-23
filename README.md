# API de Tareas - Cliente Servidor

Una aplicación web simple para gestionar tareas usando Python FastAPI como backend y HTML/CSS/JavaScript como frontend.

## 🚀 Características

- **API REST** completa con FastAPI
- **Frontend web** responsive y moderno
- **CRUD completo** para tareas (Crear, Leer, Actualizar, Eliminar)
- **Filtros** por estado (completadas/pendientes)
- **Interfaz intuitiva** para gestionar tareas

## 📋 Requisitos

- Python 3.7+
- Navegador web moderno

## 🛠️ Instalación y Uso

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar el servidor API

```bash
python main.py
```

El servidor se ejecutará en `http://localhost:8000`

### 3. Abrir el cliente web

Abre el archivo `index.html` en tu navegador web.

### 4. Ver la documentación de la API

Visita `http://localhost:8000/docs` para ver la documentación interactiva de Swagger.

## 📚 Endpoints de la API

- `GET /` - Información de la API
- `GET /tasks` - Obtener todas las tareas
- `GET /tasks/{task_id}` - Obtener una tarea específica
- `POST /tasks` - Crear una nueva tarea
- `PUT /tasks/{task_id}` - Actualizar una tarea
- `DELETE /tasks/{task_id}` - Eliminar una tarea
- `GET /tasks/completed` - Obtener tareas completadas
- `GET /tasks/pending` - Obtener tareas pendientes

## 🎯 Funcionalidades del Frontend

- **Crear tareas** con título y descripción
- **Ver todas las tareas** con información detallada
- **Editar tareas** existentes
- **Marcar como completada/pendiente**
- **Eliminar tareas**
- **Filtrar** por estado
- **Interfaz responsive** que funciona en móviles

## 🔧 Estructura del Proyecto

```
├── main.py              # Servidor FastAPI
├── index.html           # Cliente web
├── requirements.txt     # Dependencias Python
└── README.md           # Este archivo
```

## 🚀 Próximos Pasos

Esta es una versión básica que puedes expandir con:
- Base de datos persistente (SQLite, PostgreSQL, etc.)
- Autenticación de usuarios
- Categorías de tareas
- Fechas de vencimiento
- Notificaciones
- API más robusta con validaciones avanzadas

## 💡 Notas Técnicas

- La API usa **FastAPI** por su simplicidad y rendimiento
- Los datos se almacenan en memoria (se pierden al reiniciar el servidor)
- El frontend es **vanilla JavaScript** para simplicidad
- La API incluye **documentación automática** en `/docs`
