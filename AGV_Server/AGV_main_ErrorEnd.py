
import sys
import glob
import serial
import json
import time
import threading
from enum import Enum, auto
import paho.mqtt.client as mqtt
condition_RxData = threading.Condition()
USB_Ctrller_event = threading.Event()
#-- MQTT
publishTitle = ("in/motor/AGV") 
subscribeTitle = ("out/motor/AGV")
CLIENT_IP = ("192.168.0.104")
CLIENT_PORT = (1883)
CLIENT_USER = ("admin")
CLIENT_PWORD = ("1234")
#------------------------------------------ MQTT ----------------------------------
class MQTT_task(threading.Thread):
    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect(CLIENT_IP,CLIENT_PORT,60)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(CLIENT_USER, CLIENT_PWORD)

    def on_connect(self, client, userdata, flags, rc):
        global publishTitle
        global subscribeTitle
        print('conneted MQTT')
        # stringtemp2 = eve3Init["name"] +" v2"+ " online A:" + motorList[0] + " B:" + motorList[1] + " C:" + motorList[2] + " D:" + motorList[3]
        self.client.subscribe(subscribeTitle)
        self.client.publish (publishTitle, "AGV Here")


    def on_message(self, client, userdata, msg):
        global eventMain_state
        # global arduino
        # global TASK
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        m_in=json.loads(m_decode) #decode json data
        # global mainTask_SM

        if m_in.get('test1') != None:
            print("test1 Got:", m_in['test1'])
            client.publish("in/motor","test1")
        elif m_in.get('name') != None:
            arduino.write(b'{"NAME":1}')

        elif m_in.get('AGV') != None:
            if eventMain_state == TASK.END:
                # eventMain_state = m_in["AGV"]
                eventMain_state = TASK.START
            else:
                print("AGV Buzy")
        
        elif m_in.get('data') != None:
            arduino.write(str(m_in.get('data')))


#------------------------------------------ USB controller ----------------------------------   
class USB_Ctrller(threading.Thread):
    def __init__(self, devicepath, baudrate):
        threading.Thread.__init__(self)
        USB_Ctrller_event.set()
        self.ser = serial.Serial(devicepath, baudrate, timeout = 1)
        self.ser.flush()

        self.writeflag = 0

        self.RxData = ""
        self.TxData = ""

    def run(self):
        while True:
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
                        print(self.RxData)
                        self.writeflag = 0
                        self.TxData = ""
                        condition_RxData.notify_all()
                except Exception as e:
                    print(e)
                condition_RxData.release()
            time.sleep(0.1)

            if not USB_Ctrller_event.is_set:
                break
    
    def getRxData(self,TXDATA):
        # self.start()
        condition_RxData.acquire()
        self.TxData = TXDATA
        if self.writeflag == 1:
            condition_RxData.wait()
        
        m = self.RxData
        condition_RxData.release()
        
        return m


class main():
    def __init__(self,usbPort):
        # self.usbCtrl_event = threading.Event()
        self.usbCtrl = USB_Ctrller(usbPort, 57600)
        self.usbCtrl.start()
        self.startMQTT = MQTT_task()
        self.startMQTT.client.loop_forever()   

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
            ser.open()
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
        print(AGV.updateRxData('{"name":1}'))
        print(AGV.updateRxData('{"name":2}'))
        print(AGV.updateRxData('{"name":3}'))
        
    except KeyboardInterrupt:
        USB_Ctrller_event.clear()
        AGV.usbCtrl.join()
        AGV.startMQTT.client.loop_stop()




