from pypylon import pylon
import serial
import serial.tools.list_ports
import requests
from selenium import webdriver
import numpy as np

def arduinoPort():
    ports = serial.tools.list_ports.comports()
    com = []
    for p in ports:
        com.append(str(p))
    # com = list(filter(lambda x: 'Arduino' in x, com))
    com = str(com[0]).split()
    print(com[0])
    ser1 = serial.Serial(com[0], 9600)
    return ser1

def capture(camera,Exposure,Gamma,Gain,DigitalShift):
    camera.Open()
    camera.ExposureTime = Exposure
    camera.Gamma = Gamma
    try:
        camera.PixelFormat = "Mono8"
    except:
        pass
    camera.Gain = Gain
    camera.DigitalShift = DigitalShift

    numberOfImagesToGrab = 1

    camera.StartGrabbingMax(numberOfImagesToGrab)
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_Mono8
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
    while camera.IsGrabbing():
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        check = grabResult.GrabSucceeded()
        if check is True:
            #print('Capture Successfully')

            return grabResult.Array

def ledcontrol_send(Commands):
    r = requests.get('http://192.168.5.10/', auth=('admin', 'admin'))
    print('Contact to LED Controller:',r.ok)
    print('Sending Commands')

    option = webdriver.ChromeOptions()
    option.add_argument("headless")
    option.add_argument("disable-gpu")
    driver = webdriver.Chrome(executable_path='E:\chromedriver.exe', options=option)

    driver.get("http://192.168.5.10/general_setup.htm")
    textboxes = driver.find_element_by_xpath("//*[@id='content']/form/field_general_conifg/div[1]/div[2]/input")
    textboxes.send_keys('cl')
    textboxes.send_keys('\n')
    for i in range(0, len(Commands)):
        textboxes = driver.find_element_by_xpath("//*[@id='content']/form/field_general_conifg/div[1]/div[2]/input")
        textboxes.send_keys(Commands[i])
        textboxes.send_keys('\n')
        print(Commands[i],'has been sent')
def SaveFile_read():
    with open('settings.txt') as f:
        f_content = (f.read())
        f_sep = f_content.replace('=', '\n')
        f_split = f_sep.split()
        st = {}
        a = int(len(f_split) / 2)
        for i in range(0, a):
            o = 2 * i + 1
            st[f_split[o - 1]] = int(f_split[o])
        pass
    return st
def Command_Input(st):
    MCount = 0
    for i in range(0, 4):
        o = str(i + 1)
        mo = 'Mode' + o
        MCount = MCount + st[mo]
    #print("Total mode=", MCount)
    LiCurrent = []
    for n in range(1, 4):
        LiI = 0
        for i in range(1, MCount + 1):
            LiName = str(i) + 'ch' + str(n) + 'i'
            # print(st[LiName])
            LiI = int(max(st[LiName], LiI))
        LiCurrent.append(LiI)
    #print(LiCurrent)

    LiWidth = []
    for n in range(1, 4):
        LiW = 0
        for i in range(1, MCount + 1):
            LiName = str(i) + 'ch' + str(n) + 'w'
            # print(st[LiName])
            LiW = int(max(st[LiName], LiW))
        LiWidth.append(LiW)
    #print(LiWidth)

    percent = []
    for n in range(0, 3):
        for i in range(1, MCount + 1):
            LiName = str(i) + 'ch' + str(n + 1) + 'i'
            percent.append(int((st[LiName] / LiCurrent[n]) * 100))

    #print(percent)

    commandlist = ['TM1']
    for m in range(0, 3):
        commandlist.append('PO' + str(m + 1) + ',' + str(LiWidth[m]) + ',0,' + str(LiCurrent[m]))
    commandlist.append('NSM' + str(MCount))
    for i in range(1, 4):
        cmd = ''
        for m in range(MCount * i - MCount, MCount * i):
            cmd = cmd + ',' + str(percent[m])
        commandlist.append('SSM' + str(i) + cmd)
    #print(commandlist)
    return (commandlist)