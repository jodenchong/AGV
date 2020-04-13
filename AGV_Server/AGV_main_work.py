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
#-- Tasks
# class TASK(Enum):
#     END   = auto()
#     START   = auto()
#     PROC_1   = auto()
#     WAIT   = auto()
#-- threading
# eventSerial = threading.Event()
# eventMain = threading.Event()
# eventMain_state = TASK.END
# serialDataIn = ""
# arduino = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=.1)
#-- JSON
# ACTIONTASKS_LIST = ("tasks","steps")


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
        # elif m_in.get('name') != None:
            # arduino.write(b'{"NAME":1}')

        # elif m_in.get('AGV') != None:
        #     if eventMain_state == TASK.END:
        #         # eventMain_state = m_in["AGV"]
        #         eventMain_state = TASK.START
        #     else:
        #         print("AGV Buzy")
        
        # elif m_in.get('data') != None:
            # arduino.write(str(m_in.get('data')))

#------------------------------------------ Main ----------------------------------
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

if __name__ == "__main__":
    try:
        print("AGV server {0}".format(PG_VESTION))
        print(serial_ports("AGV"))
        startMQTT = MQTT_task()
        startMQTT.client.loop_forever()    

    except KeyboardInterrupt:
        # eventSerial.clear()
        # eventMain.clear()
        startMQTT.client.loop_stop()

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