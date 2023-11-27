# from classes.topicSubscriptor import *
from classes.mqttAdapter import MqttAdapter
from classes.loggingConfig import setupLogging
from classes.topicSubscriberFactory import TopicSubscriberFactory
from fastapi import FastAPI

import uvicorn
import paho.mqtt.client as mqtt
import os
import logging
import json

# Definir el nombre del servidor MQTT y el puerto
brokerAddress = os.environ.get("brokerAddress", "192.168.88.1")
port = int(os.environ.get("brokerPort", "1883"))
topicFile = os.environ.get("topicFile", "topics.json")


setupLogging()
app = FastAPI()


def loadTopicSub(mqttAdapter):
    logging.debug(f'Cargando archivo de topicos {topicFile}')
    with open(topicFile) as f:
        data = json.load(f)

    for topic_data in data["topics"]:
        topic = topic_data["topic"]
        subscriber_type = topic_data["type"]
        suber = TopicSubscriberFactory.createSubscriber(subscriber_type, topic)
        mqttAdapter.addSubscriptors(suber)


def main():
    logging.debug('Comenzando el programa')
    client = mqtt.Client()

    mqttAdapter = MqttAdapter(client, brokerAddress, port)

    loadTopicSub(mqttAdapter)

    mqttAdapter.connectToServer()

    mqttAdapter.runForever()

    # Corriendo el server
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


# Es necesario que se tome el estado de la conexion de mqtt con el server
@app.get("/health")
def health_check():
    return {"status": "OK"}


if __name__ == "__main__":
    main()
