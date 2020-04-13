# import serial
# import json
# import threading
# import paho.mqtt.client as mqtt
# from enum import Enum, auto
# import time

# try:
#     ser = serial.Serial('/dev/ttyUSB1', 57600, timeout = 1) # ttyACM1 for Arduino board
#     ser.open()
# except Exception as e:
#     print ("Exception: Opening serial port: " + str(e))

# readOut = 0   #chars waiting from laser range finder

# print ("Starting up")
# connected = False
# commandToSend = '{"mode":1}' # get the distance in mm

# while True:
#     print ("Writing: ",  commandToSend)
#     ser.write(str(commandToSend).encode())
#     time.sleep(1)
#     while True:
#         try:
#             print ("Attempt to Read")
#             readOut = ser.readline().decode('ascii')
#             time.sleep(1)
#             print ("Reading: ", readOut) 
#             break
#         except:
#             pass
#     print ("Restart")
#     ser.flush() #flush the buffer


import sys
import glob
import serial
import json
import time

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True

# def getValues(value):
#     ser.

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

        ser = serial.Serial(port, 57600, timeout = 1) # ttyACM1 for Arduino board
        ser.flush()
        time.sleep(3)
        ser.write('{"name":1}\n\r'.encode())
        time.sleep(0.5)
        readOut = ser.readline().decode('ascii').translate({ord(i): None for i in "\r\n"})
        json_object = json.loads(readOut)
        print ("Reading: ", json_object) 
        if json_object.is_json():
            if json_object["name"] == 'AGV':
                resultPort = port 
        ser.flush() #flush the buffer
        ser.close()

    print ("End " + resultPort)
    return resultPort

if __name__ == '__main__':
    serial_ports("AGV")