import paho.mqtt.publish as publish
import requests
import logging
import re
import os


# Definir el nombre del servidor MQTT y el puerto
brokerAddress = os.environ.get("brokerAddress", "192.168.88.1")
port = int(os.environ.get("brokerPort", "1883"))
url_descontar = os.environ.get(
    "URL_DESCONTAR",
    "http://localhost:8080/descontar"
)


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


class TopicSubHTTPDescontar(TopicSubscriptor):
    def handler(self, client, userdata, msg, match):
        producto = match.group(1)
        cantidad = match.group(2)

        response = requests.patch(
            f"{url_descontar}/{producto}/{cantidad}/"
        )

        if response.status_code == 200:
            respuesta_json = response.json()

            prediccion = respuesta_json.get("prediccion")

            if prediccion is not None:
                logging.debug(f'Enviando {prediccion} al topico')
                prediccion_fecha_hora = prediccion
                publish.single(
                    f"/prediccion/{producto}/",
                    prediccion_fecha_hora,
                    hostname=brokerAddress,
                    port=port
                )
            else:
                logging.error(
                    "No se encontró el valor 'prediccion' en la respuesta."
                )
        else:
            logging.error(
                f'Error al hacer PATCH a {url_descontar}, '
                f'Código de estado: {response.status_code}'
            )
            logging.error(response.text)


class TopicSubOtherTopic(TopicSubscriptor):
    def handler(self, client, userdata, msg, match):
        parametro = match.group(1)
        print(
            "Manejo especial para otro tópico con parámetro "
            f"{parametro}: {msg.payload.decode()}"
        )
