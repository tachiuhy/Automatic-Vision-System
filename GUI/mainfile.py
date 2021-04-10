from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from pypylon import pylon
import time
import cv2
import os
import datetime
import pathlib
import pandas as pd
import firstsetup as FST
import Imaging_Server as IS
import imutils as imu


class FirstProcess:
    def __init__(self, RunningState, Save_File_Content, Serial_port, path, camera):
        print('alo')
        self.RunningState = RunningState
        self.BottleCount = 0
        if RunningState == 'Online':
            print('Running Online')
            self.st = Save_File_Content
            self.Serial_Port = Serial_port
            self.save_path = path
            self.Camera = camera
            self.BottleCount = int(self.Serial_Port.readline())
            time.sleep(1.9)     # tuning
            print('BottleCount', self.BottleCount)  # show command
            time_start = time.perf_counter()
            print('time_start', time_start)  # show command
            self.Mode1_img = FST.capture(self.Camera, self.st['1ple'], self.st['1plgm'], self.st['1plgn'], self.st['1plds'])
            self.Mode3_img = FST.capture(camera, self.st['3ple'], self.st['3plgm'], self.st['3plgn'], self.st['3plds'])
            self.Mode2_img = FST.capture(camera, self.st['2ple'], self.st['2plgm'], self.st['2plgn'], self.st['2plds'])
        elif RunningState == 'Offline':
            print('Running Offine')
            self.save_path = path
            self.BottleCount += 1
            print('BottleCount', self.BottleCount)
            time_start = time.perf_counter()
            print('time_start', time_start)  # show command
            self.Mode1_img, self.Mode2_img, self.Mode3_img = FST.offline_capture(r'E:\2021-03-01_13.28', self.BottleCount)

        try:
            # Processing Image
            self.Mode1 = IS.Barcode(self.Mode1_img)
            self.Mode3 = IS.WaterProcess(self.Mode3_img, self.BottleCount, self.save_path)
            self.Mode2 = IS.WaterChecking(self.Mode2_img, self.BottleCount, self.save_path)
            self.processed_img1 = self.Mode1.img_smoothed
            self.processed_img2 = self.Mode2.eroded_img
            self.processed_img3 = self.Mode3.img_rgb
            self.p1data = self.Mode1.p1data
            self.p2data = self.Mode3.p2data
            self.p3data = self.Mode3.p3data
            self.p4data = self.Mode2.p4data

            pathlib.Path(path + '\\Mode1\\').mkdir(parents=True, exist_ok=True)
            pathlib.Path(path + '\\Mode2\\').mkdir(parents=True, exist_ok=True)
            pathlib.Path(path + '\\Mode3\\').mkdir(parents=True, exist_ok=True)
            pathlib.Path(path + '\\barcode\\').mkdir(parents=True, exist_ok=True)
            name1 = os.path.join(path, 'Mode1', str(self.BottleCount) + '.tiff')
            name2 = os.path.join(path, 'Mode2', str(self.BottleCount) + '.tiff')
            name3 = os.path.join(path, 'Mode3', str(self.BottleCount) + '.tiff')
            name4 = os.path.join(path, 'barcode', str(self.BottleCount) + '.tiff')
            try:
                print('Saving images...')
                cv2.imwrite(name1, self.Mode1_img)
                cv2.imwrite(name2, self.Mode2_img)
                cv2.imwrite(name3, self.Mode3_img)
                cv2.imwrite(name4, self.processed_img1)
                print('Save successfully')
            except Exception as e:
                print('Failed: ', str(e))
            cv2.waitKey(10)

        except:
            print('Cannot processed')
            try:
                pathlib.Path(path + '\\Mode1\\').mkdir(parents=True, exist_ok=True)
                pathlib.Path(path + '\\Mode2\\').mkdir(parents=True, exist_ok=True)
                pathlib.Path(path + '\\Mode3\\').mkdir(parents=True, exist_ok=True)
                pathlib.Path(path + '\\barcode\\').mkdir(parents=True, exist_ok=True)

                name1 = os.path.join(path, 'Mode1', str(self.BottleCount) + '.tiff')
                name2 = os.path.join(path, 'Mode2', str(self.BottleCount) + '.tiff')
                name3 = os.path.join(path, 'Mode3', str(self.BottleCount) + '.tiff')
                print('Saving images...')
                cv2.imwrite(name1, self.Mode1_img)
                cv2.imwrite(name2, self.Mode2_img)
                cv2.imwrite(name3, self.Mode3_img)
                print('Save successfully')
            except Exception as e:
                print('Failed: ', str(e))
            cv2.waitKey(10)

            self.Condition1 = 'False Barcode'
            self.processed_img1 = None
            self.p1data = 'Barcode not found'

            self.Condition2 = 'False DF'
            self.processed_img2 = None
            self.p4data = 'Water Level not found'

            self.Condition3 = 'False BL'
            self.processed_img3 = None
            self.p2data = 'Fail Water level'
            self.p3data = 'Opened Cap'


class MainFunction_Thread(QtCore.QThread):
    StrSignal = QtCore.pyqtSignal(str)
    # Im1Signal = QtCore.pyqtSignal(object)
    # Im2Signal = QtCore.pyqtSignal(object)
    # Im3Signal = QtCore.pyqtSignal(object)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.path = ''
        self.RunningState = 'Online'

    def run(self):
        print('Main function initialized')
        data = {}
        data['Name'] = []
        data['Water level (mm)'] = []
        data['Water level presence'] = []
        data['Cap Checking'] = []

        if self.RunningState == 'Online':
            print('Online')
            camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            setup = FST.FirstSetup()
            Serial_Port = setup.GetArduino()
            Read_Content = setup.SaveFile_read()
            commandlist = setup.Command_Input().commandlist
            setup.ledcontrol_send(commandlist)
            setup.Serial_port.write('Start\n'.encode())

        elif self.RunningState == 'Offline':
            print('Offine')
            camera = 'Offline Camera'
            setup = FST.Offline_FirstSetup()
            Serial_Port = setup.GetArduino()
            Read_Content = setup.SaveFile_read()
            setup.Command_Input()
            commandlist = setup.commandlist
            setup.ledcontrol_send(commandlist)
        self.StrSignal.emit("Ready to work")
        self.path = self.path + str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M'))

        while True:
            Running = FirstProcess(self.RunningState, Read_Content, Serial_Port, self.path, camera)

            data['Name'].append(Running.p1data)
            data['Water level presence'].append(Running.p4data)
            data['Water level (mm)'].append(Running.p2data)
            data['Cap Checking'].append(Running.p3data)
            cv2.putText(Running.processed_img3, 'Barcode: ' + str(Running.p1data),
                        (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            if (Running.p4data == 'False') or (Running.p2data == 'Water level is wrong') or (
                    Running.p3data == 'Cap opening'):
                cv2.putText(Running.processed_img3, 'DF: False', (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(Running.processed_img3, 'Water level: False', (100, 200), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (255, 0, 0), 2)
                cv2.putText(Running.processed_img3, 'Cap is opening', (100, 250), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (255, 0, 0), 2)
                setup.Serial_port.write(str(Running.BottleCount).encode())
            else:
                cv2.putText(Running.processed_img3, 'DF: True', (100, 150), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (255, 0, 0), 2)
                cv2.putText(Running.processed_img3, 'Water level: ' + str(Running.p2data), (100, 200),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(Running.processed_img3, 'Cap is closing', (100, 250), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (255, 0, 0), 2)

            cv2.imshow('Backlight', imu.resize(Running.processed_img3, width=400))
            cv2.imshow('Darkfield', imu.resize(Running.Mode2_img[800:1050, 700:1700], width=400))
            cv2.imshow('Label', imu.resize(Running.Mode1_img[900:1950, 400:2000], width=400))
            cv2.waitKey(1)

            if Running.BottleCount == 360:
                setup.Serial_port.write('Stop\n'.encode())
                break
        self.ExportCSV(data)
        setup.ledcontrol_send(['cl'])
        print('Program has stopped')    ###############################################

    def ExportCSV(self, data):
        df = pd.DataFrame(data)
        df.to_csv(self.path + str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M')) + '.csv')
        print('CSV data has been exported')