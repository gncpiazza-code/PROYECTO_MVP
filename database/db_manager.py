# database/db_manager.py
from supabase import create_client, Client
import sys
import os

# Aseguramos que Python encuentre config.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import SUPABASE_URL, SUPABASE_KEY

# Inicializacion del cliente
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_usuarios():
    """Trae todos los usuarios para asignar tareas."""
    try:
        respuesta = supabase.table("usuarios").select("*").execute()
        return respuesta.data
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return []

def crear_nueva_tarea(titulo, descripcion, id_asignado, id_creador):
    """Inserta una tarea en la tabla tareas."""
    datos = {
        "titulo": titulo,
        "descripcion": descripcion,
        "id_asignado": id_asignado,
        "id_creador": id_creador,
        "estado": "Pendiente"
    }
    try:
        respuesta = supabase.table("tareas").insert(datos).execute()
        return respuesta.data
    except Exception as e:
        print(f"Error al crear tarea: {e}")
        return None

def listar_tareas_supervisor(id_supervisor):
    """Consulta tareas especificas para la vista de campo."""
    try:
        respuesta = supabase.table("tareas").select("*").eq("id_asignado", id_supervisor).execute()
        return respuesta.data
    except Exception as e:
        print(f"Error al listar tareas: {e}")
        return []
    # database/db_manager.py (Agregar esta funcion al final)

def crear_usuario(nombre, email, rol, funcion, telegram_id=None):
    """Crea un nuevo miembro del equipo en el sistema."""
    datos = {
        "nombre": nombre,
        "email": email,
        "rol": rol,
        "funcion": funcion,
        "telegram_id": telegram_id
    }
    try:
        respuesta = supabase.table("usuarios").insert(datos).execute()
        return respuesta.data
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        return None

def actualizar_usuario(id_usuario, nuevos_datos):
    """
    Permite modificar nombre, funcion, telegram_id o rol.
    nuevos_datos debe ser un diccionario, ej: {"funcion": "Logistica Sur"}
    """
    try:
        respuesta = supabase.table("usuarios").update(nuevos_datos).eq("id", id_usuario).execute()
        return respuesta.data
    except Exception as e:
        print(f"Error al actualizar usuario: {e}")
        return None

def actualizar_estado_tarea(id_tarea, nuevo_estado):
    """Cambia el estado de una tarea: Pendiente, En Progreso, Completada."""
    try:
        respuesta = supabase.table("tareas").update({"estado": nuevo_estado}).eq("id", id_tarea).execute()
        return respuesta.data
    except Exception as e:
        print(f"Error al actualizar estado de tarea: {e}")
        return None

def listar_todas_tareas():
    """Trae todas las tareas para el panel de seguimiento del Admin."""
    try:
        respuesta = supabase.table("tareas").select("*").order("id", desc=True).execute()
        return respuesta.data
    except Exception as e:
        print(f"Error al listar todas las tareas: {e}")
        return []