import serial
from threading import Thread
import tkinter as tk
from tkinter import ttk


class SerialController:
    def __init__(self):
        self.ser = None
        self.ports = []

    def list_serial_ports(self):
        try:
            from serial.tools.list_ports import comports
            self.ports = [port.device for port in comports()]
            return self.ports
        except Exception as e:
            print("Error listing serial ports:", e)
            return []

    def connect_serial(self, port, baudrate=115200):
        if self.ser:
            self.ser.close()
        self.ser = serial.Serial(port, baudrate, timeout=1)
        print(
            f"Connected to {port} with baudrate {self.ser.baudrate}, parity {self.ser.parity}, stopbits {self.ser.stopbits}, bytesize {self.ser.bytesize}")

    def disconnect_serial(self):
        if self.ser:
            self.ser.close()
            self.ser = None
            print("Disconnected from serial port")

    def serial_is_open(self) -> bool:
        return self.ser and self.ser.is_open

    def send_command(self, command):
        if self.serial_is_open():
            self.ser.write(command.encode('utf-8'))
            print(f"Sent data: {command}")

    def try_read_serial(self):
        try:
            raw_data = self.ser.readline()
            return raw_data
        except:
            return None

    def read_serial(self):
        if self.serial_is_open():
            raw_data = self.try_read_serial()
            if raw_data:
                print(f"Raw data: {raw_data}")
                data = raw_data.decode('utf-8', errors='replace').strip()
                print(f"Decoded data: {data}")
                return data
        return None


class Application(tk.Tk):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.history = []
        self.history_index = 0

        self.title("Arduino Control")
        self.setup_ui()
        self.refresh_ports()
        self.delay_thread()

    def setup_ui(self):
        frame = tk.Frame(self)
        frame.pack(padx=10, pady=10)

        label = tk.Label(frame, text="Select serial port:")
        label.grid(row=0, column=0)

        self.port_var = tk.StringVar()
        self.port_combobox = ttk.Combobox(frame, textvariable=self.port_var)
        self.port_combobox.grid(row=0, column=1)

        connect_button = tk.Button(frame, text="Connect", command=self.connect_serial)
        connect_button.grid(row=0, column=2)

        refresh_button = tk.Button(frame, text="Refresh", command=self.refresh_ports)
        refresh_button.grid(row=0, column=3)

        disconnect_button = tk.Button(frame, text="Disconnect", command=self.disconnect_serial)
        disconnect_button.grid(row=0, column=4)

        label_command = tk.Label(frame, text="Enter command ('H(angle)', 'V(angle)', or 'GET'):")
        label_command.grid(row=1, column=0)

        self.entry = tk.Entry(frame, width=30)
        self.entry.grid(row=1, column=1)
        self.entry.bind("<Return>", self.send_command)
        self.entry.bind("<Up>", self.history_back)
        self.entry.bind("<Down>", self.history_forward)

        button = tk.Button(frame, text="Send", command=self.send_command)
        button.grid(row=1, column=2)

        self.text = tk.Text(frame, height=10, width=40)
        self.text.grid(row=2, columnspan=5, sticky="nsew")

        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def delay_thread(self):
        self.after(500, self.start_serial_thread)

    def start_serial_thread(self):
        thread = Thread(target=self.read_serial, daemon=True)
        thread.start()
        print("START serial_thread")

    def connect_serial(self):
        port = self.port_combobox.get()
        self.controller.connect_serial(port)

    def disconnect_serial(self):
        self.controller.disconnect_serial()

    def read_serial(self):
        while True:
            if self.controller.serial_is_open():
                data = self.controller.read_serial()
                if data:
                    self.text.insert(tk.END, f"Received: {data}\n")
                    self.text.see(tk.END)

    def send_command(self, event=None):
        command = self.entry.get()
        self.history.append(command)
        self.history_index = len(self.history)
        self.controller.send_command(command)
        self.text.insert(tk.END, f"Sent: {command}\n")
        self.text.see(tk.END)
        self.entry.delete(0, tk.END)

    def history_back(self, event):
        if self.history_index > 0:
            self.history_index -= 1
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, self.history[self.history_index])

    def history_forward(self, event):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, self.history[self.history_index])

    def update_serial_ports(self):
        self.controller.list_serial_ports()
        ports = self.controller.ports
        self.port_combobox['values'] = ports
        if len(ports):
            self.port_var.set(ports[0])
        else:
            self.port_var.set("")

    def refresh_ports(self):
        self.after(100, self.update_serial_ports)
        self.port_combobox['values'] = self.controller.ports
        self.port_var.set("")


if __name__ == "__main__":
    controller = SerialController()
    app = Application(controller)
    app.mainloop()
