import paho.mqtt.client as mqtt
from telegram import Bot
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os

# Configuración para el bot de Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Configuración para el servidor Mosquitto
MQTT_BROKER_ADDRESS = os.environ.get("MQTT_BROKER_ADDRESS")
MQTT_TOPICS_LIST = os.environ.get("MQTT_TOPICS_LIST", "#")


def on_message(client, userdata, msg):
    message = msg.payload.decode('utf-8')
    queue_name = msg.topic
    send_telegram_message(f"Nuevo mensaje de Mosquitto en la cola {queue_name}:\n\n{message}")


def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def start(update: Update, context: CallbackContext):
    update.message.reply_text("¡Bot de Mosquitto y Telegram iniciado!")


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

    # Manejador de mensajes
    message_handler = MessageHandler(Filters.text & ~Filters.command, start)
    dispatcher.add_handler(message_handler)

    # Inicia el bot de Telegram
    updater.start_polling()

    # Mantén el programa en ejecución
    updater.idle()


if __name__ == "__main__":
    main()
