from classes.topicSubscriptor import *
from classes.mqttAdapter import MqttAdapter
from classes.loggingConfig import setupLogging
from classes.topicSubscriberFactory import TopicSubscriberFactory

import paho.mqtt.client as mqtt
import re
import os
import logging
import json

# Definir el nombre del servidor MQTT y el puerto
brokerAddress = os.environ.get("brokerAddress", "192.168.88.1")
port = int(os.environ.get("brokerPort", "1883"))
topicFile = os.environ.get("topicFile", "topics.json")


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


if __name__ == "__main__":
    main()
