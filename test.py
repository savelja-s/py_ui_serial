import serial
import sys


def send_to_serial(data):
    port = '/dev/ttyUSB0'
    baudrate = 9600

    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            ser.write(data.encode('utf-8'))
            print(f"Sent: {data}")
    except serial.SerialException as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <data>")
        sys.exit(1)

    data = sys.argv[1]
    send_to_serial(data)
