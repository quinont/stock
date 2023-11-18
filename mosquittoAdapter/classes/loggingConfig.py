import logging

def setupLogging():
    logging.basicConfig(
        level=logging.DEBUG,  # Puedes ajustar el nivel según sea necesario
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

setupLogging()
