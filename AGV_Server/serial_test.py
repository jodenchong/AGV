
import sys
import glob
import serial
import json
import time
import threading

condition_RxData = threading.Condition()
condition_test = threading.Condition()

class USB_Ctrller(threading.Thread):
    def __init__(self, devicepath, baudrate):
        threading.Thread.__init__(self)
        self.USB_Ctrller_event = threading.Event()
        self.USB_Ctrller_event.set()
        self.ser = serial.Serial(devicepath, baudrate, timeout = 1)
        self.ser.flush()

        self.writeflag = 0

        self.RxData = ""
        self.TxData = ""

    def run(self):
        while self.USB_Ctrller_event.is_set:
            if self.TxData:
                condition_RxData.acquire()
                # self.ser.write(str("w" + '\n').encode())
                self.ser.write(self.TxData.encode())
                time.sleep(0.5)
                self.writeflag = 1
                try:
                    self.RxData = self.ser.readline().decode('ascii').translate({ord(i): None for i in "\r\n"})
                    # self.RxData = self.RxData.split('\r')[0]
                    if self.RxData:
                        # print(self.RxData)
                        self.writeflag = 0
                        self.TxData = ""
                        condition_RxData.notify_all()
                except Exception as e:
                    print(e)
                condition_RxData.release()
            time.sleep(0.1)
    
    def getRxData(self,TXDATA):
        # self.start()
        condition_RxData.acquire()
        self.TxData = TXDATA
        # if self.writeflag == 1:
        condition_RxData.wait()
        
        m = self.RxData
        condition_RxData.release()
        
        return m


class main():
    def __init__(self,usbPort):
        # self.usbCtrl_event = threading.Event()
        self.usbCtrl = USB_Ctrller(usbPort, 57600)
        self.usbCtrl.start()

    def updateRxData(self,TXDATA):
        return self.usbCtrl.getRxData(TXDATA)


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True


def serial_ports(name):
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[U]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    resultPort = ""

    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    print(result)
    
    for port in result:
        connetionTry = 0
        serINdata = ""
        resultPort = "Null"

        try:
            ser = serial.Serial(port, 57600, timeout = 2) # ttyACM1 for Arduino board
            # ser.open()
        except Exception as e:
            print ("\n" + port + " " + str(e))

        ser.write('{"name":1}\n\r'.encode())
        # time.sleep(0.1)
        # start = time.perf_counter()
        while True:
            try:
                print ("Attempt to Read")
                serINdata = ser.readline().decode('ascii').translate({ord(i): None for i in "\r\n"})
                # serINdata = ser.readline().decode('ascii').translate({ord(i): None for i in "\r\n"})
                if serINdata:
                    time.sleep(0.2)
                    serialJSON = json.loads(serINdata)
                    print ("Reading: ", serialJSON) 
                    serINdata = 0
                    if serialJSON["name"] == name:
                        resultPort = port
                    break
            except:
                pass

            if (connetionTry > 1):
                break
            connetionTry += 1
            
        ser.flush() #flush the buffer
        ser.close()
    print ("End " + resultPort)
    return resultPort


if __name__ == '__main__':
    try:
        # print("PORT : " + serial_ports("AGV"))
        AGV = main(serial_ports("AGV"))
        # print(AGV.updateRxData('{"name":1}'))
    except KeyboardInterrupt:
        pass
        AGV.usbCtrl.USB_Ctrller_event.clear()




