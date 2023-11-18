from classes.loggingConfig import setupLogging
import logging
import re

class TopicSubscriptor():
    def __init__(self, topic):
        logging.debug(f'Creando nuevo subscriptor, con el topico {topic}')
        self.topic = topic
        patronExpRegular = re.sub(r'\+', r'([^/]+)', topic)
        patronExpRegular = re.sub(r'#', r'(.+)', patronExpRegular)
        self.pattern = re.compile(patronExpRegular)

    def getTopic(self):
        return self.topic

    def getPattern(self):
        return self.pattern

    def matching(self, topic):
        return self.pattern.match(topic)

    def handler(self, client, userdata, msg, match):
        pass

class TopicSubHTTPCaller(TopicSubscriptor):
    def handler(self, client, userdata, msg, match):
        producto = match.group(1)
        cantidad = match.group(2)
        print(f"Descuento para el producto {producto} con cantidad {cantidad}: {msg.payload.decode()}")

class TopicSubOtherTopic(TopicSubscriptor):
    def handler(self, client, userdata, msg, match):
        parametro = match.group(1)
        print(f"Manejo especial para otro tópico con parámetro {parametro}: {msg.payload.decode()}")
