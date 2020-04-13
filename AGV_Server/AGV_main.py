#!/usr/bin/env python3

#-- Python include
import sys
import glob
import serial
import time
import json
import threading
import paho.mqtt.client as mqtt
from enum import Enum, auto
#-- project info
PG_VESTION = ("V1")
#-- serial
# SERIAL_PORT = ('/dev/ttyUSB3')
SERIAL_BAUDRATE = (57600)
#-- MQTT
publishTitle = ("in/motor/AGV") 
subscribeTitle = ("out/motor/AGV")
CLIENT_IP = ("192.168.0.104")
CLIENT_PORT = (1883)
CLIENT_USER = ("admin")
CLIENT_PWORD = ("1234")

USB_Ctrller_event = threading.Event()
condition_RxData = threading.Condition()
USB_Ctrller_event = threading.Event()
#------------------------------------------ MQTT ----------------------------------
class MQTT_task(threading.Thread):
    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect(CLIENT_IP,CLIENT_PORT,60)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(CLIENT_USER, CLIENT_PWORD)

    def on_connect(self, client, userdata, flags, rc):
        # global publishTitle
        # global subscribeTitle
        print('conneted MQTT')
        # stringtemp2 = eve3Init["name"] +" v2"+ " online A:" + motorList[0] + " B:" + motorList[1] + " C:" + motorList[2] + " D:" + motorList[3]
        self.client.subscribe(subscribeTitle)
        self.client.publish (publishTitle, "AGV Here")


    def on_message(self, client, userdata, msg):
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        m_in=json.loads(m_decode) #decode json data


        if m_in.get('test1') != None:
            print("test1 Got:", m_in['test1'])
            client.publish("in/motor","test1")
        elif m_in.get('data') != None:
            stringSent = m_in['data']
            print(AGV.updateRxData(stringSent))
        elif m_in.get('data1') != None:
            AGV.usbCtrl.TxData = m_in['data1']
        
        elif m_in.get('testing') != None:
            AGV.mainTask = m_in['testing']

#------------------------------------------ Serial Port ----------------------------------   
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
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    print(result)
    
    resultPort = ""
    for port in result:
        try:
            ser = serial.Serial(port, 57600, timeout = 2) # ttyACM1 for Arduino board
            ser.open()
        except Exception as e:
            print ("\n" + port + " " + str(e))

        ser.write('{"name":1}\n\r'.encode())
        time.sleep(0.1)
        # start = time.perf_counter()
        while True:
            try:
                print ("Attempt to Read")
                # readOut = ser.readline().decode('ascii').replace('\r', '').replace('\n','') 
                readOut = ser.readline().decode('ascii').translate({ord(i): None for i in "\r\n"})
                time.sleep(1)
                json_object = json.loads(readOut)
                print ("Reading: ", json_object) 
                if json_object["name"] == name:
                    resultPort = port 
                    # print("got agv")
                break
            except:
                pass
        ser.flush() #flush the buffer
        ser.close()
    print ("End " + resultPort)
    return resultPort


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
        self.RxData_Temp = ""

    def run(self):
        while USB_Ctrller_event.is_set:
            if self.TxData:
                condition_RxData.acquire()
                # self.ser.write(str("w" + '\n').encode())
                self.ser.write(self.TxData.encode())
                time.sleep(0.5)
                self.writeflag = 1
                try:
                    self.RxData_Temp = self.ser.readline().decode('ascii').translate({ord(i): None for i in "\r\n"})
                    # self.RxData = self.RxData.split('\r')[0]
                    if self.RxData_Temp:
                        print("Received :" + self.RxData_Temp)
                        self.writeflag = 0
                        self.TxData = ""
                        condition_RxData.notify_all()
                except Exception as e:
                    print(e)
                condition_RxData.release()
            if self.RxData_Temp:
                self.RxData = self.RxData_Temp
                self.RxData_Temp = ""
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

#------------------------------------------ Main ----------------------------------
class main(threading.Thread):
    def __init__(self,usbPort):
        threading.Thread.__init__(self)
        # self.usbCtrl_event = threading.Event()
        self.usbCtrl = USB_Ctrller(usbPort, 57600)
        self.usbCtrl.start()
        # self.startMQTT = MQTT_task()
        # self.startMQTT.client.loop_forever()   
        self.mainTask = "Null"

    def updateRxData(self,TXDATA):
        return self.usbCtrl.getRxData(TXDATA)

    def run(self):
        while True:
            if self.mainTask == "Null":
                pass
            elif self.mainTask == "testing":
                print("main run testing")
                self.mainTask = "Null"

                with open('Tasks.json', 'r', encoding="utf-8") as alphabetFile:
                    actionTask = json.load(alphabetFile)
                    alphabetFile.close()

                actionTaskTemp = actionTask["testing"]["steps"]
                # actionStep = actionTaskTemp["steps"]
                # print(actionStep)
                for step in actionTaskTemp:
                    strTemp1 = {"mode":step["mode"]}
                    self.usbCtrl.TxData = json.dumps(strTemp1)
                    self.delay = int(step["delay"])
                    print(step)
                    time.sleep(self.delay)


if __name__ == "__main__":
    try:
        print("AGV server {0}".format(PG_VESTION))
        # print(serial_ports("AGV"))
        AGV = main(serial_ports("AGV"))
        AGV.start()
        # print(AGV.updateRxData('{"mode":1}'))
        # print(AGV.updateRxData('{"mode":2}'))
        # print(AGV.updateRxData('{"mode":3}'))
        startMQTT = MQTT_task()
        startMQTT.client.loop_forever()    

    except KeyboardInterrupt:
        # eventSerial.clear()
        # eventMain.clear()
        startMQTT.client.loop_stop()
        USB_Ctrller_event.clear()
        print(".......... End ..........")

'''
print("not access")

arduino.write('{"NAME":1}')


    print("AGV server %s" % PG_VESTION)



Packge Install
* pip install paho-mqtt



'''


# def serialWaitData(data):
#     arduino.write(str(data))
#     DONE = True
#     while DONE:
#         data = arduino.readline().strip('\n\r')
#         if is_json(data) == True:
#                 print("Serail :", data)
#                 DONE = False
#         print("DONE ")