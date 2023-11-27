import logging
import sys


class MqttAdapter():
    def __init__(self, client, brokerAddress, port):
        self.subscriptors = []
        self.client = client
        self.brokerAddress = brokerAddress
        self.port = port

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def addSubscriptors(self, suber):
        logging.debug("Agregando nuevo subscriptor a la lista")
        self.subscriptors.append(suber)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Conexión exitosa al servidor MQTT")
            for suber in self.subscriptors:
                client.subscribe(suber.getTopic())
        else:
            logging.error(
                "No se pudo conectar al servidor MQTT."
                f"Código de retorno: {rc}"
            )
            sys.exit(200)

    def on_message(self, client, userdata, msg):
        for suber in self.subscriptors:
            match = suber.matching(msg.topic)
            if match:
                logging.debug(f"Se encontro un manejador para {msg.topic}")
                suber.handler(client, userdata, msg, match)
                return
        logging.error(
            f"No se encontró un manejador para el tópico: {msg.topic}"
        )

    def connectToServer(self):
        logging.debug("Conectando al server")
        self.client.connect(self.brokerAddress, self.port, keepalive=60)

    def runForever(self):
        logging.info("Comenzando a recibir mensajes")
        self.client.loop_start()
