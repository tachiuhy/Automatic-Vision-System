from pypylon import pylon
import serial
import serial.tools.list_ports
import requests
from selenium import webdriver
import sys
def arduinoPort():
    ports = serial.tools.list_ports.comports()
    com = []
    for p in ports:
        com.append(str(p))
    com = list(filter(lambda x: 'CH340' in x, com))
    try:
        com = str(com[0]).split()
        print('Arduino found at', com[0])
        ser1 = serial.Serial(com[0], 9600)
    except Exception as e:
        print('No COM found')
        sys.exit()
    return ser1
def capture(camera,Exposure,Gamma,Gain,DigitalShift,BalanceRatio):

    camera.Open()
    camera.ExposureTime = Exposure
    camera.Gamma = Gamma
    try:
        camera.PixelFormat = "Mono8"
    except:
        pass
    camera.Gain = Gain
    camera.DigitalShift = DigitalShift
    camera.BalanceRatio = BalanceRatio

    numberOfImagesToGrab = 1

    camera.StartGrabbingMax(numberOfImagesToGrab)

    while camera.IsGrabbing():
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        check = grabResult.GrabSucceeded()
        if check is True:
            print('Capture Successfully')
            return grabResult
        else:
            print('ERROR: Something happened during the communication between the camera and the host.')
            ledcontrol_send(['cl'])
            sys.exit()

def ledcontrol_send(Commands):
    try:
        r = requests.get('http://192.168.1.10/', auth=('admin', 'admin'))
        print('Contact to LED Controller:',r.ok)
        print('Sending Commands')
    except Exception as e:
        print(e)
        sys.exit()
    option = webdriver.ChromeOptions()
    option.add_argument("headless")
    option.add_argument("disable-gpu")
    driver = webdriver.Chrome(executable_path='E:\chromedriver.exe', options=option)
    try:
        driver.get("http://192.168.1.10/general_setup.htm")
        textboxes = driver.find_element_by_xpath("//*[@id='content']/form/field_general_conifg/div[1]/div[2]/input")
        textboxes.send_keys('cl')
        textboxes.send_keys('\n')
        for i in range(0, len(Commands)):
            textboxes = driver.find_element_by_xpath("//*[@id='content']/form/field_general_conifg/div[1]/div[2]/input")
            textboxes.send_keys(Commands[i])
            textboxes.send_keys('\n')
            print(Commands[i],'has been sent')
    except Exception as e:
        print(e)
        sys.exit()
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

    LiCurrent = []
    for n in range(1, 4):
        LiI = 0
        for i in range(1, MCount + 1):
            LiName = str(i) + 'ch' + str(n) + 'i'
            LiI = int(max(st[LiName], LiI))
        LiCurrent.append(LiI)

    LiWidth = []
    for n in range(1, 4):
        LiW = 0
        for i in range(1, MCount + 1):
            LiName = str(i) + 'ch' + str(n) + 'w'
            # print(st[LiName])
            LiW = int(max(st[LiName], LiW))
        LiWidth.append(LiW)

    percent = []
    for n in range(0, 3):
        for i in range(1, MCount + 1):
            LiName = str(i) + 'ch' + str(n + 1) + 'i'
            percent.append(int((st[LiName] / LiCurrent[n]) * 100))

    commandlist = ['TM1']
    for m in range(0, 3):
        commandlist.append('PO' + str(m + 1) + ',' + str(LiWidth[m]) + ',0,' + str(LiCurrent[m]))
    commandlist.append('NSM' + str(MCount))
    for i in range(1, 4):
        cmd = ''
        for m in range(MCount * i - MCount, MCount * i):
            cmd = cmd + ',' + str(percent[m])
        commandlist.append('SSM' + str(i) + cmd)
    return commandlist, MCount