# Client UI

Esto es un cliente para escritorio escrito en python.

La idea es que se pueda levantar como un proceso en un raspberry pi 2. Es por eso que no se esta ocupando una app web. Entonces la idea es que sea rapido simple y facil de usar.

# Levantar la app al comienzo del SO

> Si bien esto sirve para cualquier Linux, solo lo probe con Raspbian GNU/Linux 11 (bullseye)

Primero deberiamos tener el main.py en una carpeta, por ejemplo en el home del usuario:
```
mkdir ${HOME}/deskGuiStock
# De alguna manera copias el main.py al directorio.
```

Darle permisos de ejecucion al main.py
```
chmod +x ${HOME}/deskGuiStock/main.py
```

Crear carpeta .config/autostart en el home del usuario:
```
mkdir -p ${HOME}/.config/autostart
```

Ahora crear el archivo para la configuracion:
```
vim ${HOME}/.config/autostart/stock.desktop
```

En el archivo copiamos lo siguiente:
```
[Desktop Entry]
Type=Application
Name=StockSystem
Exec=/usr/bin/python3 ${HOME}/deskGuiStock/main.py
```

Listo, para la proxima ves que inicie el SO ya vas a tener todo up&running


# TODO

- Mejorar la documentacion
- Mejorar el codigo spaghetti
- Guardar configuracion y cambios en un sistema aparte
- Poder guardar otra cosa que no sea solamente botellones (comida para perro, comida para humanos, etc)
- Es posible poner sensores en los distintos productos para medir su disponibilidad?

# Bugs
- Dobles clic en los botones no esta considerado.

