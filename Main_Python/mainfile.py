from pypylon import pylon
import time
import cv2
import os
import concurrent.futures
import datetime
import pathlib
import pandas as pd
import WaterLevelProcess as WLP
import firstsetup as fst
import matplotlib.pyplot as plt
import numpy as np
import BarcodeProcess as BCP
import WaterLevelChecking as WLC

def FirstProcess(st, ser1, path, camera):
    BottleCount = int(ser1.readline())
    time.sleep(1.9)
    print('BottleCount', BottleCount)
    time_start = time.perf_counter()
    print('time_start', time_start)
    imMode1 = fst.capture(camera, st['1ple'], st['1plgm'], st['1plgn'], st['1plds'])
    imMode3 = fst.capture(camera, st['3ple'], st['3plgm'], st['3plgn'], st['3plds'])
    imMode2 = fst.capture(camera, st['2ple'], st['2plgm'], st['2plgn'], st['2plds'])


    try:
        con1, p1img, p1data = BCP.Barcode(imMode1)
        con3, p3img, p2data, p3data = WLP.WaterLevelProcess(imMode3, BottleCount, path)
        con2, p2img, p4data = WLC.WaterLevelChecking(imMode2, BottleCount, path)


        pathlib.Path(path + '\\Mode1\\').mkdir(parents=True,exist_ok=True)
        pathlib.Path(path + '\\Mode2\\').mkdir(parents=True,exist_ok=True)
        pathlib.Path(path + '\\Mode3\\').mkdir(parents=True,exist_ok=True)
        pathlib.Path(path + '\\barcode\\').mkdir(parents=True,exist_ok=True)

        name1 = os.path.join(path,'Mode1', str(BottleCount) + '.tiff')
        name2 = os.path.join(path,'Mode2', str(BottleCount) + '.tiff')
        name3 = os.path.join(path,'Mode3', str(BottleCount) + '.tiff')
        name4 = os.path.join(path,'barcode', str(BottleCount) + '.tiff')


        try:
            print('Saving images...')
            cv2.imwrite(name1, imMode1)
            cv2.imwrite(name2, imMode2)
            cv2.imwrite(name3, imMode3)
            cv2.imwrite(name4, p1img)
            print('Save successfully')
        except Exception as e:
            print('Failed: ', str(e))
        cv2.waitKey(10)
        return BottleCount, imMode1, con1, p1img, p1data, imMode2, con2, p2img, p4data,  con3, p3img,\
               p2data, p3data, imMode3
    except:
        print('Cannot processed')
        try:
            pathlib.Path(path + '\\Mode1\\').mkdir(parents=True, exist_ok=True)
            pathlib.Path(path + '\\Mode2\\').mkdir(parents=True, exist_ok=True)
            pathlib.Path(path + '\\Mode3\\').mkdir(parents=True, exist_ok=True)
            pathlib.Path(path + '\\barcode\\').mkdir(parents=True, exist_ok=True)

            name1 = os.path.join(path, 'Mode1', str(BottleCount) + '.tiff')
            name2 = os.path.join(path, 'Mode2', str(BottleCount) + '.tiff')
            name3 = os.path.join(path, 'Mode3', str(BottleCount) + '.tiff')
            print('Saving images...')
            cv2.imwrite(name1, imMode1)
            cv2.imwrite(name2, imMode2)
            cv2.imwrite(name3, imMode3)
            print('Save successfully')
        except Exception as e:
            print('Failed: ', str(e))
        cv2.waitKey(10)
        return BottleCount, imMode1, 'FalseBC', None, 'Object not found', imMode2, 'FalseDF', None, 'Object not found', \
                'FalseWL', None,  'Object not found', 'Cap Not Found', imMode3

def ExportCSV(data):
    df = pd.DataFrame(data)
    df.to_csv(path + str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M')) + '.csv')
    print('CSV data has been exported')


if __name__ == '__main__':
    data = {}
    data['Name'] = []
    data['Water level'] = []
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    ser1 = fst.arduinoPort()
    st = fst.SaveFile_read()
    fst.ledcontrol_send(fst.Command_Input(st))
    print('Ready to work')
    path = r'E:\Bottle_image\\' + str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M'))

    check = 1
    while check == 1:
        print('command:')
        condition = input()
        if condition == 'Start':
            ser1.write('Start\n'.encode())
            break
        else:
            check = 0

    while condition == 'Start':
        BottleCount, imMode1, con1, p1img, p1data, imMode2, con2, p2img, p4data, con3, p3img, p2data, p3data, imMode3 = FirstProcess(st, ser1, path, camera)



        if p4data == 'False':
            cv2.putText(p3img, 'DF: False', (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            ser1.write(str(BottleCount).encode())
        if (p4data == 'True') and (p2data =='Water level is wrong') :
            cv2.putText(p3img, 'DF: True', (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            ser1.write(str(BottleCount).encode())
        cv2.imshow('backlight', p3img)
        cv2.waitKey(1)
        data['Name'].append(p1data)
        data['Water level'].append(p2data)
        if BottleCount == 90:
            ser1.write('Stop\n'.encode())
            break
    ExportCSV(data)
    fst.ledcontrol_send(['cl'])
    print('Program has stopped')