print("IoT Gateway")
from collections import Counter
from matplotlib import collections
import paho.mqtt.client as mqttclient
import time
import json
import serial.tools.list_ports

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
mess = ""

#Please check the comport in the device manager
THINGS_BOARD_ACCESS_TOKEN = "kL08JlLQdUehNMD657AM"
#bbc_port = "COM5"

def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "USB Serial Device" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort

bbc_port=getPort()

if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port , baudrate=115200)

def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    collect_data = {}
    # TODO: Add your source code to publish data to the server
    if splitData[1] == 'TEMP':
        collect_data = {'TEMP': splitData[2]}
    if splitData[1] == 'LIGHT':
        collect_data = {'LIGHT': splitData[2]}
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)

def readSerial():
    
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'valueLED': True}
    temp_data1 = {'valueFAN': True}
    cmd = 1
    #TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            temp_data['valueLED'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            if jsonobj['params']==True:
                cmd=1
            else: cmd=0
        if jsonobj['method'] == "setFAN":
            temp_data1['valueFAN'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data1), 1)
            if jsonobj['params']==True:
                cmd=3
            else: cmd=2
    except:
        pass

    if len(bbc_port) > 0:
        print('cmd :',cmd)
        ser.write((str(cmd) + "#").encode())

def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

counter=0

while True:

    if len(bbc_port) >  0:
        readSerial()

    time.sleep(1)