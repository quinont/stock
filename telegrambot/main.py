import paho.mqtt.client as mqtt
from telegram import Bot
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ContextTypes
import os
import requests
from requests.auth import HTTPBasicAuth

# Configuración para el bot de Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_USER_ID = int(os.environ.get("TELEGRAM_USER_ID"))

# Configuración para el servidor Mosquitto
MQTT_BROKER_ADDRESS = os.environ.get("MQTT_BROKER_ADDRESS")
MQTT_TOPICS_LIST = os.environ.get("MQTT_TOPICS_LIST", "#")

# Acceso para Mikrotik
MIKROTIK_API_URL = os.environ.get("MIKROTIK_API_URL")
MIKROTIK_USERNAME = os.environ.get("MIKROTIK_USERNAME")
MIKROTIK_PASSWORD = os.environ.get("MIKROTIK_PASSWORD")
MIKROTIK_DST_ADDRESS = os.environ.get("MIKROTIK_DST_ADDRESS")


def on_message(client, userdata, msg):
    message = msg.payload.decode('utf-8')
    queue_name = msg.topic
    send_telegram_message(f"Nuevo mensaje de Mosquitto en la cola {queue_name}:\n\n{message}")


def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def start(update: Update, context: CallbackContext):
    update.message.reply_text("¡Bot de Mosquitto y Telegram iniciado!")


def public_ip():
    try:
        respuesta = requests.get('https://api.ipify.org?format=json')
        if respuesta.status_code == 200:
            return respuesta.json()['ip']
        else:
            return 'No se pudo obtener la IP pública.'
    except Exception as e:
        return f'Ocurrió un error: {e}'


def send_public_ip(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /send_public_ip is issued."""
    user = update.effective_user
    chat = update.effective_chat
    if user.id == TELEGRAM_USER_ID and chat.type == "private":
        msg = public_ip()
    else:
        msg = "127.0.0.1"

    update.message.reply_text(msg)


def mikrotik_router_requests(endpoint, metodo='GET', datos=None):
    url_completa = f"{MIKROTIK_API_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        if metodo == 'GET':
            respuesta = requests.get(url_completa, headers=headers, auth=HTTPBasicAuth(MIKROTIK_USERNAME, MIKROTIK_PASSWORD))
        elif metodo == 'PATCH':
            respuesta = requests.patch(url_completa, json=datos, headers=headers, auth=HTTPBasicAuth(MIKROTIK_USERNAME, MIKROTIK_PASSWORD))
        elif metodo == 'DELETE':
            respuesta = requests.delete(url_completa, headers=headers, auth=HTTPBasicAuth(MIKROTIK_USERNAME, MIKROTIK_PASSWORD))
        else:
            return ({}, f"Método HTTP no soportado: {metodo}")

        status_code = respuesta.status_code
        if status_code in [200, 201]:
            return (respuesta.json(), "")
        elif status_code == 204:
            return ({}, "")
        else:
            print(f"Error {respuesta.status_code}: {respuesta.text}")
            return ({}, f"Error {respuesta.status_code}: {respuesta.text}")

    except Exception as e:
        print(f"Error al realizar la petición: {e}")
        return ({}, f"Error al realizar la petición: {e}")


def updater_firewall(disable_rule):
    if disable_rule:
        data_disable = {"disabled": "no"}
    else:
        data_disable = {"disabled": "yes"}

    # buscando el nat de acceso ssh
    all_nat_config, request_msg = mikrotik_router_requests("/ip/firewall/nat", "GET")
    if request_msg != "":
        return f"Error al revisar reglas de NAT. Mensaje: {request_msg}"

    ssh_nat = [item for item in all_nat_config if item.get("comment") == "accesossh"]
    if len(ssh_nat) == 0:
        return "Error Regla no encontrada"

    nat_id = ssh_nat[0].get(".id")

    nat_rule, request_msg = mikrotik_router_requests(f"/ip/firewall/nat/{nat_id}", "PATCH", data_disable)
    if request_msg != "":
        return f"Error al cambiar el valor de la regla. Mensaje: {request_msg}"
    if nat_rule.get("disabled") == "false":
        return "Regla nat habilitada"

    firewall_connections, request_msg = mikrotik_router_requests("/ip/firewall/connection", "GET")
    if request_msg != "":
        return f"Error al intentar ver las conexiones del router, Mensaje: {request_msg}"

    delete_connections = [item for item in firewall_connections if item.get("dst-address") == MIKROTIK_DST_ADDRESS]

    for conn in delete_connections:
        conn_id = conn.get(".id")
        if conn_id:
            delete_conn, request_msg = mikrotik_router_requests(f'/ip/firewall/connection/{conn_id}', "DELETE")

    return "Regla nat deshabilitada, y conexiones cortadas"


def firewall_rule_active(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    chat = update.effective_chat
    if user.id == TELEGRAM_USER_ID and chat.type == "private":
        msg = updater_firewall(True)
    else:
        msg = "Regla Activada"

    update.message.reply_text(msg)


def firewall_rule_desactive(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    chat = update.effective_chat
    if user.id == TELEGRAM_USER_ID and chat.type == "private":
        msg = updater_firewall(False)
    else:
        msg = "Regla des-Activada"
    update.message.reply_text(msg)


def main():
    # Configuración del cliente MQTT
    mqtt_client = mqtt.Client()
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER_ADDRESS, 1883, 60)
    for topic in MQTT_TOPICS_LIST.split(","):
        mqtt_client.subscribe(topic)
    mqtt_client.loop_start()

    # Configuración del bot de Telegram
    updater = Updater(token=TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Manejadores de comandos
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    send_public_ip_handler = CommandHandler('send_public_ip', send_public_ip)
    dispatcher.add_handler(send_public_ip_handler)

    firewall_rule_desactive_handler = CommandHandler('firewall_rule_update_disable', firewall_rule_desactive)
    dispatcher.add_handler(firewall_rule_desactive_handler)

    firewall_rule_active_handler = CommandHandler('firewall_rule_update_enable', firewall_rule_active)
    dispatcher.add_handler(firewall_rule_active_handler)

    # Manejador de mensajes
    message_handler = MessageHandler(Filters.text & ~Filters.command, start)
    dispatcher.add_handler(message_handler)

    # Inicia el bot de Telegram
    updater.start_polling()

    # Mantén el programa en ejecución
    updater.idle()


if __name__ == "__main__":
    main()
