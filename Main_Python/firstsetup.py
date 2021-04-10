import yaml
from pypylon import pylon
import serial
import serial.tools.list_ports
import requests
from selenium import webdriver
import numpy as np


class FirstSetup:
    def __init__(self):
        None

    def GetArduino(self):
        ports = serial.tools.list_ports.comports()
        com = []
        for p in ports:
            com.append(str(p))
        # com = list(filter(lambda x: 'Arduino' in x, com))
        com = str(com[0]).split()
        print(com[0])
        self.Serial_port = serial.Serial(com[0], 9600)

    def ledcontrol_send(self, command):
        self.command = command
        r = requests.get('http://192.168.5.10/', auth=('admin', 'admin'))
        print('Contact to LED Controller:', r.ok)
        print('Sending Commands')

        option = webdriver.ChromeOptions()
        option.add_argument("headless")
        option.add_argument("disable-gpu")
        driver = webdriver.Chrome(executable_path='E:\chromedriver.exe', options=option)

        driver.get("http://192.168.5.10/general_setup.htm")
        textboxes = driver.find_element_by_xpath("//*[@id='content']/form/field_general_conifg/div[1]/div[2]/input")
        textboxes.send_keys('cl')
        textboxes.send_keys('\n')
        for i in range(0, len(self.command)):
            textboxes = driver.find_element_by_xpath("//*[@id='content']/form/field_general_conifg/div[1]/div[2]/input")
            textboxes.send_keys(self.command[i])
            textboxes.send_keys('\n')
            print(self.command[i], 'has been sent')

    def SaveFile_read(self):
        with open('YAML_Setting.yml') as file:
            self.content = yaml.load(file, Loader=yaml.FullLoader)

    def Command_Input(self):
        MCount = 0
        for i in range(0, 4):
            o = str(i + 1)
            mo = 'Mode' + o
            MCount = MCount + self.content[mo]
        #print("Total mode=", MCount)
        LiCurrent = []
        for n in range(1, 4):
            LiI = 0
            for i in range(1, MCount + 1):
                LiName = str(i) + 'ch' + str(n) + 'i'
                # print(st[LiName])
                LiI = int(max(self.content[LiName], LiI))
            LiCurrent.append(LiI)
        #print(LiCurrent)

        LiWidth = []
        for n in range(1, 4):
            LiW = 0
            for i in range(1, MCount + 1):
                LiName = str(i) + 'ch' + str(n) + 'w'
                # print(st[LiName])
                LiW = int(max(self.content[LiName], LiW))
            LiWidth.append(LiW)
        #print(LiWidth)

        percent = []
        for n in range(0, 3):
            for i in range(1, MCount + 1):
                LiName = str(i) + 'ch' + str(n + 1) + 'i'
                percent.append(int((self.content[LiName] / LiCurrent[n]) * 100))

        #print(percent)

        self.commandlist = ['TM1']
        for m in range(0, 3):
            self.commandlist.append('PO' + str(m + 1) + ',' + str(LiWidth[m]) + ',0,' + str(LiCurrent[m]))
        self.commandlist.append('NSM' + str(MCount))
        for i in range(1, 4):
            cmd = ''
            for m in range(MCount * i - MCount, MCount * i):
                cmd = cmd + ',' + str(percent[m])
            self.commandlist.append('SSM' + str(i) + cmd)


def capture(Camera, Exposure, Gamma, Gain, DigitalShift):
    Camera.Open()
    Camera.ExposureTime = Exposure
    Camera.Gamma = Gamma
    try:
        Camera.PixelFormat = "Mono8"
    except Exception as e:
        print('Failed: ', str(e))
    Camera.Gain = Gain
    Camera.DigitalShift = DigitalShift
    Camera.StartGrabbingMax(1)
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_Mono8
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
    while Camera.IsGrabbing():
        grabResult = Camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        check = grabResult.GrabSucceeded()
        if check is True:
            image = grabResult.Array
    return image