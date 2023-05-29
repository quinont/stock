from tkinter import *
import socket
import datetime
import json
import os


class JsonFileHandler:
    def __init__(self, filename):
        self.filename = filename

    def read_json(self):
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            with open(self.filename, 'r') as file:
                data = json.load(file)
            return data
        else:
            return {}

    def write_json(self, data):
        with open(self.filename, 'w') as file:
            json.dump(data, file)

class TextWriterHandler:
    def __init__(self, filename):
        self.filename = filename

    def write_text(self, text):
        with open(self.filename, 'a') as file:
            file.write(text + '\n')

class StockSystem:
    def __init__(self, root, store, config):
        self.store = store
        self.config_file = config
        self.config = self.config_file.read_json()

        # Set Variables
        self.last_change = StringVar()
        if "last_change" in self.config:
            self.update_last_change(self.config["last_change"])
        else:
            self.update_last_change()
        self.diff_days = StringVar()
        if "available" in self.config:
            self.available = IntVar(value=int(self.config["available"]))
        else:
            self.available = IntVar(value=4)
        self.cant = IntVar(value=0)

        root.title("Stock System v0.1")
        width= root.winfo_screenwidth()
        height= root.winfo_screenheight()
        root.geometry("%dx%d" % (width, height))
        frame = Frame(root, borderwidth=2, relief="sunken")
        frame.grid(column=1, row=1, sticky=(N, E, S, W))
        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)

        label_ip = Label(frame, text="Direccion IP:")
        label_ip.grid(column=1, row=1, sticky=(E), columnspan=3)

        label_dir_ip = Label(frame, text=self.get_ip_address())
        label_dir_ip.grid(column=5, row=1, sticky=(W))

        label_last_change = Label(frame, text="Fecha de ultimo Cambio:")
        label_last_change.grid(column=1, row=2, sticky=(E), columnspan=3)

        label_last_change_value = Label(frame, textvariable=self.last_change)
        label_last_change_value.grid(column=5, row=2, sticky=(W))

        label_diff_days = Label(frame, text="Cantidad de dias desde\n el ultimo cambio:")
        label_diff_days.grid(column=1, row=3, sticky=(E), columnspan=3)

        self.label_diff_days_value = Label(frame, textvariable=self.diff_days)
        self.label_diff_days_value.grid(column=5, row=3, sticky=(W))
        self.update_diff_days_cron()

        label_available = Label(frame, text="Cantidad disponible:")
        label_available.grid(column=1, row=4, sticky=(E), columnspan=3)

        label_available_value = Label(frame, textvariable=self.available)
        label_available_value.grid(column=5, row=4, sticky=(W))

        button_cant_min = Button(frame, text="-", command=self.update_cant_min)
        button_cant_min.grid(column=1, row=5, sticky=(E, W))

        self.update_cant_max(4)
        label_cant = Label(frame, textvariable=self.cant)
        label_cant.grid(column=2, row=5, sticky=(E, W))

        button_cant_max = Button(frame, text="+", command=self.update_cant_max)
        button_cant_max.grid(column=3, row=5, sticky=(E, W))

        button_adding_to_available = Button(frame, text="Ingresar botellones", command=self.update_available)
        button_adding_to_available.grid(column=1, row=6, sticky=(E, W), columnspan=3)

        button_remove_element = Button(frame, text="Cambiar Botellon", command=self.remove_element)
        button_remove_element.grid(column=5, row=5, sticky=(S, N, E, W), rowspan=2)

        for child in frame.winfo_children():
            child.grid_configure(padx=10, pady=5)
            child.configure(font=('calibri', 13))


    def get_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = str(s.getsockname()[0])
            s.close()
            return ip_address
        except:
            return "0.0.0.0 (error)"

    def update_last_change(self, last_change = ""):
        if last_change != "":
            lc = last_change
        else:
            last_change = datetime.datetime.now()
            lc = last_change.strftime('%d/%m/%y - %H:%M:%S %p')
        self.last_change.set(lc)

    def update_diff_days_cron(self):
        diff_in_days = datetime.datetime.now() - datetime.datetime.strptime(self.last_change.get(), '%d/%m/%y - %H:%M:%S %p')
        msg = f'{diff_in_days.days} dias - {divmod(diff_in_days.seconds, 60*60)[0]} horas - {divmod(diff_in_days.seconds, 60*60)[1]} seg'
        self.diff_days.set(msg)
        self.label_diff_days_value.after(1000, self.update_diff_days_cron)

    def update_diff_days(self):
        diff_in_days = datetime.datetime.now() - datetime.datetime.strptime(self.last_change.get(), '%d/%m/%y - %H:%M:%S %p')
        msg = f'{diff_in_days.days} dias - {divmod(diff_in_days.seconds, 60*60)[0]} horas - {divmod(diff_in_days.seconds, 60*60)[1]} seg'
        self.diff_days.set(msg)

    def update_available(self):
        available = self.available.get() + self.cant.get()
        self.cant.set(4)
        self.available.set(available)
        self.update_config_file()

    def remove_element(self):
        self.store.write_text(datetime.datetime.now().strftime('%d/%m/%y - %H:%M:%S %p'))
        available = self.available.get()
        available = available - 1
        self.available.set(available)
        self.update_last_change()
        self.update_diff_days()
        self.update_config_file()

    def update_config_file(self):
        available = self.available.get()
        last_change = self.last_change.get()
        self.config["available"] = available
        self.config["last_change"] = last_change
        self.config_file.write_json(self.config)

    def update_cant_max(self, inc = 1):
        aux = self.cant.get()
        aux = aux + inc
        self.cant.set(aux)

    def update_cant_min(self, inc = 1):
        aux = self.cant.get()
        aux = aux - inc
        self.cant.set(aux)


store = TextWriterHandler("cambios.txt")
config = JsonFileHandler('config.json')
root = Tk()
StockSystem(root, store, config)
root.mainloop()
