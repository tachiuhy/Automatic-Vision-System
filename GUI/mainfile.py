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
    def __init__(self, RunningState, Save_File_Content, Serial_port, path, camera, count):
        self.RunningState = RunningState
        self.path = path
        if RunningState == 'Online':
            print('Running Online')
            self.st = Save_File_Content
            self.Serial_Port = Serial_port
            self.save_path = path + '\\' + str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M'))
            self.Camera = camera
            self.BottleCount = int(self.Serial_Port.readline())
            time.sleep(1.9)  # tuning
            print('BottleCount', self.BottleCount)  # show command
            time_start = time.perf_counter()
            print('time_start', time_start)  # show command
            self.Mode1_img = FST.capture(self.Camera, self.st['1ple'], self.st['1plgm'], self.st['1plgn'],
                                         self.st['1plds'])
            self.Mode3_img = FST.capture(camera, self.st['3ple'], self.st['3plgm'], self.st['3plgn'], self.st['3plds'])
            self.Mode2_img = FST.capture(camera, self.st['2ple'], self.st['2plgm'], self.st['2plgn'], self.st['2plds'])
        elif RunningState == 'Offline':
            print('Running Offine')
            self.save_path = path + '\\' + str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M'))
            self.BottleCount = count
            print('count: ', count)
            print('BottleCount', self.BottleCount)
            time_start = time.perf_counter()
            print('time_start', time_start)  # show command
            self.Mode1_img, self.Mode2_img, self.Mode3_img = FST.offline_capture(self.path, self.BottleCount)

        try:
            # Processing Image
            self.Mode1 = IS.Label(self.Mode1_img, self.BottleCount, self.save_path)
            self.Mode3 = IS.WaterProcess(self.Mode3_img, self.BottleCount, self.save_path)
            self.Mode2 = IS.WaterChecking(self.Mode2_img, self.BottleCount, self.save_path)

            self.processed_img1 = self.Mode1.Dome_img_brg
            self.processed_img2 = self.Mode2.DF_img_bgr
            self.processed_img3 = self.Mode3.BL_img_rgb
            self.p1data = self.Mode1.p1data
            self.p5data = self.Mode1.p5data
            self.p2data = self.Mode3.p2data
            self.p3data = self.Mode3.p3data
            self.p4data = self.Mode2.p4data

            if RunningState == 'Online':        # Only save Captured image in online mode
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
            if RunningState == 'Online':    # Only save Captured image in online mode
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
            self.processed_img1 = self.Mode1_img
            self.p1data = 'Barcode not found'

            self.Condition2 = 'False DF'
            self.processed_img2 = self.Mode2_img
            self.p4data = 'Water Level not found'

            self.Condition3 = 'False BL'
            self.processed_img3 = self.Mode3_img
            self.p2data = 'False Water level'
            self.p3data = 'Opened Cap'


class MainFunction_Thread(QtCore.QThread):
    isRunningSignal = QtCore.pyqtSignal(bool)
    StrSignal = QtCore.pyqtSignal(str)
    Im1Signal = QtCore.pyqtSignal(object)
    Im2Signal = QtCore.pyqtSignal(object)
    Im3Signal = QtCore.pyqtSignal(object)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.path = ''
        self.RunningState = 'Online'
        self.YAML_settings = {}

    def run(self):
        self.isRunningSignal.emit(True)
        data = {}
        data['Name'] = []
        data['Water level (mm)'] = []
        data['Water level presence'] = []
        data['Cap Checking'] = []

        if self.RunningState == 'Online':
            self.YAML_settings = self.YAML_settings
            self.StrSignal.emit("System is running Online")
            camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            setup = FST.FirstSetup()
            Serial_Port = setup.GetArduino()
            # Read_Content = setup.SaveFile_read() # Changed to YAML_settings {}
            setup.Command_Input(self.YAML_settings)
            commandlist = setup.commandlist
            setup.ledcontrol_send(commandlist)
            setup.Serial_port.write('Start\n'.encode())

        elif self.RunningState == 'Offline':
            self.StrSignal.emit("System is running Offline")
            camera = 'Offline Camera'
            setup = FST.Offline_FirstSetup()
            Serial_Port = setup.GetArduino()
            # Read_Content = setup.SaveFile_read() # Changed to YAML_settings {}
            setup.Command_Input(self.YAML_settings)
            commandlist = setup.commandlist
            setup.ledcontrol_send(commandlist)
            self.StrSignal.emit('Slimutating Contact to LED Controller: OK')
            self.StrSignal.emit('Sending Commands')
            for i in range(0, len(commandlist)):
                self.StrSignal.emit(str(commandlist[i]) + 'has been sent')
        self.StrSignal.emit("Ready to work")
        self.path = self.path
        count = 0
        while True:
            count += 1
            Running = FirstProcess(self.RunningState, self.YAML_settings, Serial_Port, self.path, camera, count)
            data['Name'].append(Running.p1data)
            data['Water level presence'].append(Running.p4data)
            data['Water level (mm)'].append(Running.p2data)
            data['Cap Checking'].append(Running.p3data)
            self.StrSignal.emit('')
            self.StrSignal.emit('Barcode: ' + str(Running.p1data))
            if (Running.p4data == 'False') or (Running.p2data == 'Water level is wrong') or \
                    (Running.p3data == 'Cap is opening') or (Running.p5data == 'False Label'):
                self.StrSignal.emit('DF: False')
                self.StrSignal.emit('Water level: False')
                self.StrSignal.emit('Cap is opening')
                self.StrSignal.emit('False Label')
                if self.RunningState == 'Online':
                    setup.Serial_port.write(str(Running.BottleCount).encode())
            else:
                self.StrSignal.emit('DF: True')
                self.StrSignal.emit('Water level: ' + str(Running.p2data))
                self.StrSignal.emit('Cap is Closing')
                self.StrSignal.emit('True Label')
            self.Im1Signal.emit(Running.processed_img1)
            self.Im2Signal.emit(Running.processed_img2)
            self.Im3Signal.emit(Running.processed_img3)
            if self.RunningState == 'Online':
                setup.Serial_port.write('Stop\n'.encode())
                self.ExportCSV(data)
                setup.ledcontrol_send(['cl'])
                self.StrSignal.emit("Program has stopped")
                self.isRunningSignal.emit(False)
                break
            elif self.RunningState == 'Offline':
                path_check = os.path.join(self.path, 'Mode1')
                Imgfile_path = [os.path.abspath(i) for i in os.scandir(path_check) if i.is_file()]
                if Running.BottleCount == len(Imgfile_path):
                    self.ExportCSV(data)
                    setup.ledcontrol_send(['cl'])
                    self.StrSignal.emit("Program has stopped")
                    self.isRunningSignal.emit(False)
                    break
                else:
                    pass

    def ExportCSV(self, data):
        df = pd.DataFrame(data)
        df.to_csv(self.path + str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M')) + '.csv')
        print('CSV data has been exported')
