# services/telegram_notifier.py
import requests
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import TELEGRAM_BOT_TOKEN

def enviar_notificacion_tarea(telegram_id, titulo, descripcion):
    """Avisa al supervisor por Telegram cuando le asignan una tarea."""
    if not TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN no configurado, notificacion omitida.")
        return

    mensaje = (
        f"Nueva tarea asignada:\n\n"
        f"Titulo: {titulo}\n"
        f"Descripcion: {descripcion or 'Sin descripcion'}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        respuesta = requests.post(
            url,
            json={"chat_id": telegram_id, "text": mensaje},
            timeout=5
        )
        if respuesta.status_code == 200:
            print(f"Notificacion enviada a telegram_id {telegram_id}")
        else:
            print(f"Error Telegram API: {respuesta.text}")
    except Exception as e:
        print(f"Error al enviar notificacion: {e}")
