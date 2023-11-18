from classes.loggingConfig import setupLogging
from classes.topicSubscriptor import *
import logging

class TopicSubscriberFactory:
    @staticmethod
    def createSubscriber(subscriberType, topic):
        if subscriberType == "HTTPCaller":
            return TopicSubHTTPCaller(topic)
        elif subscriberType == "OtherTopic":
            return TopicSubOtherTopic(topic)
        else:
            logging.error(f"Tipo de suscriptor desconocido: {subscriberType}")
            raise ValueError(f"Tipo de suscriptor desconocido: {subscriberType}")
