#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import serial, time

import Skype4Py
import time

#initialization and open the port
#possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call
#hand commands 
hand_com={
'[':'11P1350'+chr(35)+'13P1200T500',
']':'11P1250'+chr(35)+'13P1300T500',
#12P1200 - center, 12P1500 - up
'Y':'9P1800T500',
'H':'9P1500T500',
'N':'9P1200T500', 
'p':'7P1650'+chr(35)+'8P1550'+chr(35)+'9P1400'+chr(35)+'10P1000T1000',
'O':'8P1300T500', 
'I':'8P1100T500',
'U':'8P900T500',
'u':'7P1660T500',
'i':'7P1380T500', 
'o':'7P1100T500',

'9':'1P1100'+chr(35)+'2P1600'+chr(35)+'3P2200'+chr(35)+'4P2200'+chr(35)+'5P1226T1000',
'8':'1P2200'+chr(35)+'2P1600'+chr(35)+'3P2200'+chr(35)+'4P800'+chr(35)+'5P1226T1000',

 
'x':'1P2200'+chr(35)+'2P2300'+chr(35)+'3P2300'+chr(35)+'4P2200'+chr(35)+'5P2200T1000', 
'c':'1P1300'+chr(35)+'2P1300'+chr(35)+'3P1300'+chr(35)+'4P501'+chr(35)+'5P1300T800', 
#'f':'1P2200'+chr(35)+'2P1511'+chr(35)+'3P1000'+chr(35)+'4P2200'+chr(35)+'5P2274T200', 
#'r':'2P600'+chr(35)+'3P1000'+chr(35)+'4P800'+chr(35)+'5P1226T800', 
#'v':'1P2200S1200',
#'v':'JCLF150JCRF150',
#'f':'JCLF200JCRF200',
#'r':'JCLF250JCRF250', 
'7':'25P1500'+chr(35)+'26P2000'+chr(35)+'27P2000'+chr(35)+'28P501'+chr(35)+'29P600',
'6':'25P1500'+chr(35)+'26P2000'+chr(35)+'27P1000'+chr(35)+'28P2300'+chr(35)+'29P600',

'l':'25P2400'+chr(35)+'26P2000'+chr(35)+'27P2200'+chr(35)+'28P2300'+chr(35)+'29P2100'+chr(35)+'30P500T1200', 
'k':'25P1000'+chr(35)+'26P1000'+chr(35)+'27P700'+chr(35)+'28P2000'+chr(35)+'29P1300'+chr(35)+'30P500T800', 
'j':'27P2000'+chr(35)+'28P1000'+chr(35)+'29P2100'+chr(35)+'30P500T1000', 
'R':'1P2200'+chr(35)+'2P500'+chr(35)+'3P1000'+chr(35)+'4P2200'+chr(35)+'5P1226T800', 
'M':'27P1600'+chr(35)+'28P800'+chr(35)+'29P800'+chr(35)+'30P2300T1000',
'1':'14P1607'+chr(35)+'15P1238T100',
'2':'14P1717'+chr(35)+'15P1348T100',
'3':'14P1827'+chr(35)+'15P1458T100',
'4':'14P2000T100'
}
#commands
com = {'w':'JCLF100JCRF100','s':'JCLB100JCRB100','q':'JCLF0JCRF100','e':'JCLF100JCRF0','a':'JCLB100JCRF100','d':'JCLF100JCRB100','z':'JCLF0JCRF0JCLB0JCRB0',
't':'JALU300','g':'JSALEn','b':'JALD300',
'y':'JARU300','h':'JSAREn','n':'JARD300', 
'W':'51','S':'50', 'Z':'52',
'Q':'JSHLEnJSHREn','E':'JSHLEEJSHREE', 
'v':'JCLF150JCRF150',
'f':'JCLF200JCRF200',
'r':'JCLF250JCRF250'
}
txt = {'88':'вперед','77':'назад','112':'поворот налево','53':'поворот направо','45':'разворот влево',
'29':'разворот вправо','55':'платформа стоп',
'115':'левая стоп','12':'левая вперед','15':'левая назад',
'111':'правая стоп','96':'правая вперед','39':'правая назад','51':'up','50':'down','52':'Stop',
'31':'свет выкл','27':'свет вкл'}

ser0 = serial.Serial()
#ser0.port = "/dev/serial/by-id/usb-067b_2303-if00-port0"
#ser.port = "/dev/ttyS2"
ser0.port = "/dev/ttyUSB1"
ser0.baudrate = 9600
ser0.bytesize = serial.EIGHTBITS #number of bits per bytes
ser0.parity = serial.PARITY_NONE #set parity check: no parity
ser0.stopbits = serial.STOPBITS_ONE #number of stop bits
#ser.timeout = None          #block read
ser0.timeout = 0             #non-block read
#ser.timeout = 2              #timeout block read
ser0.xonxoff = False     #disable software flow control
ser0.rtscts = False     #disable hardware (RTS/CTS) flow control
ser0.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser0.writeTimeout = 2     #timeout for write

ser1 = serial.Serial()
#ser1.port = "/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_D-if00-port0"
#ser1.port = "/dev/ttyUSB9"
ser1.port = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0042_75237333536351D081B2-if00"
ser1.baudrate = 115200
ser1.bytesize = serial.EIGHTBITS #number of bits per bytes
ser1.parity = serial.PARITY_NONE #set parity check: no parity
ser1.stopbits = serial.STOPBITS_ONE #number of stop bits
#ser.timeout = None          #block read
ser1.timeout = 0             #non-block read
#ser.timeout = 2              #timeout block read
ser1.xonxoff = False     #disable software flow control
ser1.rtscts = False     #disable hardware (RTS/CTS) flow control
ser1.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser1.writeTimeout = 2     #timeout for write

is_sleep=0

def ProcessMessage(Message):
  cmd=Message.Body
  for num1 in cmd: 
    if(num1==' '):
       is_sleep=1
       continue
    if(is_sleep==1):
       print 'sleep '+str(float(num1)*0.3)+'s'
       time.sleep(float(num1)*0.3)
       is_sleep=0
       continue
    #num1 = int(num1)
    if(num1 in '98764123MRmjkl' or num1=='[' or num1==']' or num1=='Y' or num1=='H' or num1=='N' or num1=='U' or num1=='I' or num1=='O' or num1=='c' or num1=='x' or num1=='u' or num1=='i' or num1=='o' or num1=='p'):
        #ser1.write(chr(35)+hand_com[num1]+chr(13)+chr(10))
       cmd=chr(35)+hand_com[num1]+chr(13)+chr(10)
       ser1.write(cmd)
       print cmd
    else:
       cmd=com[num1]+chr(13)+chr(10)
       ser1.write(cmd)
       #print (txt[com[num1]])
        #response='0'
        #while int(response.strip())!=int(com[num1]):
        #    ser0.write(chr(35))
        #    time.sleep(0.03)
        #    ser0.write(chr(int(com[num1])))
        #    time.sleep(0.03)
        #    ser0.write(chr(13))
        #    print (txt[com[num1]])
        #    time.sleep(0.005)     
        #    time.sleep(0.2)  #give the serial port sometime to receive the data
        #    response = ser0.readline()
        #    if (response == ''):
        #        response='0'
        #    print("read data: " + response)
    #ser0.close()
    ser1.close()
    except Exception, e1:
    print "error communicating...: " + str(e1)

def MessageStatus(Message, Status):
  if Status == Skype4Py.cmsReceived:
    print("Message '%s' received from user %s", Message.Body, Message.FromHandle)
    Message.MarkAsSeen()
    ProcessMessage(Message)

try: 
    #ser0.open()
    ser1.open()
except Exception, e:
    print "error open serial port: " + str(e)
    exit()

skype=Skype4Py.Skype()
skype.Attach()
# set event handlers
skype.OnMessageStatus = MessageStatus

while(1):
  time.sleep(1);
