from classes.topicSubscriptor import TopicSubHTTPDescontar, TopicSubOtherTopic
import logging


class TopicSubscriberFactory:
    @staticmethod
    def createSubscriber(subscriberType, topic):
        if subscriberType == "HTTPDescontar":
            return TopicSubHTTPDescontar(topic)
        elif subscriberType == "OtherTopic":
            return TopicSubOtherTopic(topic)
        else:
            logging.error(
                f"Tipo de suscriptor desconocido: {subscriberType}"
            )
            raise ValueError(
                f"Tipo de suscriptor desconocido: {subscriberType}"
            )
