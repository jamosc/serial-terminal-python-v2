import serial, serial.tools.list_ports

class SerialClass():

    def __init__(self):
        super().__init__()

        self.serialPort = serial.Serial()
        self.serialPort.timeout = 0.5
        self.baudratesDIC = {
        '1200':1200,
        '2400':2400,
        '4800':4800,
        '9600':9600,
        '19200':19200,
        '38400':38400,
        '57600':57600,
        '115200':115200
        }
        self.portList = []
    
    def update_ports(self):
        self.portList = [port.device for port in serial.tools.list_ports.comports()]

    def serial_sendData(self,data):
        if(self.serialPort.is_open):
            message = str(data) + '\n'
            self.serialPort.write(message.encode())

    def serial_connect(self):
        try:
            self.serialPort.open()
        except:
            return 'Serial error'

    def serial_disconnect(self):
        self.serialPort.close()