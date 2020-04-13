
Python Code: (Double-click to select all)
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
import serial,time
ser = serial.Serial(
    port='COM4',
    baudrate=38400,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    xonxoff=False
)
line = ser.readline();
 
while line:
     line = ser.readline()
     print(line)
     ser.reset_input_buffer()
     cmd = input("Enter command or 'exit':") + '\r\n'
     if len(cmd)>0:
        ser.write(cmd.encode())
     else:
        continue