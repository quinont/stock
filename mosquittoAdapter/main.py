from classes.topicSubscriptor import *
from classes.mqttAdapter import MqttAdapter
from classes.loggingConfig import setupLogging

import paho.mqtt.client as mqtt
import re
import os
import logging

# Definir el nombre del servidor MQTT y el puerto
brokerAddress = os.environ.get("brokerAddress", "192.168.88.1")
port = int(os.environ.get("brokerPort", "1883"))


def main():
    logging.debug('Comenzando el programa')
    client = mqtt.Client()

    mqttAdapter = MqttAdapter(client, brokerAddress, port)

    mqttAdapter.addSubscriptors(TopicSubHTTPCaller("/descuento/+/+/"))
    mqttAdapter.addSubscriptors(TopicSubOtherTopic("/otrotopico/#"))

    mqttAdapter.connectToServer()
    mqttAdapter.runForever()


if __name__ == "__main__":
    main()
