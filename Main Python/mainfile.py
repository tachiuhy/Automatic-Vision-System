from pypylon import pylon
import time
import cv2
import os
import concurrent.futures
import datetime
import pathlib
import pandas as pd
import sys
import WaterLevelProcess as WLP
import firstsetup as fst
import BarcodeProcess as BCP

def FirstProcess(st, ser1, path, camera, ModeCount):
    BottleCount = int(ser1.readline())
    if BottleCount != 0:
        imModeDict = {}
        for i in range(1, ModeCount + 1):
            imModeDict['imMode'+str(i)] = fst.capture(camera, st[str(i)+'ple'], st[str(i)+'plgm'], st[str(i)+'plgn'], st[str(i)+'plds'],st[str(i)+'plbr'])
        try:
            start=time.perf_counter()
            with concurrent.futures.ProcessPoolExecutor() as executor:
                p2 = executor.submit(WLP.WaterLevelProcess, imModeDict['imMode2'].Array, BottleCount, path)
                p1 = executor.submit(BCP.Barcode, imModeDict['imMode1'].Array)
            stop = time.perf_counter()
            print(round(stop - start, 2))
            con2, p2img, p2data = p2.result()
            con1, p1img, p1data = p1.result()

            pathlib.Path(path + '\\barcode\\').mkdir(parents=True,exist_ok=True)
            BarPath = os.path.join(path,'barcode', str(BottleCount) + '.tiff')
            cv2.imwrite(BarPath, p1img)

            try:
                imSaveNameDict = {}
                for i in range(1, ModeCount + 1):
                    pathlib.Path(path + '\\Mode' + str(i)+'\\').mkdir(parents=True, exist_ok=True)
                    imSaveNameDict['name'+str(i)] = os.path.join(path, 'Mode' + str(i), str(BottleCount) + '.tiff')
                    print('Saving images...')
                    cv2.imwrite(imSaveNameDict['name'+str(i)], imModeDict['imMode'+str(i)].Array)
                print('Save successfully')
            except Exception as e:
                print('Failed: ', str(e))
            cv2.waitKey(10)
            return imModeDict, BottleCount, con1, p1img, p1data, con2, p2img, p2data
        except:
            print('Cannot processed')
            try:
                imSaveNameDict = {}
                for i in range(1, ModeCount + 1):
                    pathlib.Path(path + '\\Mode' + str(i)+'\\').mkdir(parents=True, exist_ok=True)
                    imSaveNameDict['name'+str(i)] = os.path.join(path, 'Mode' + str(i), str(BottleCount) + '.tiff')
                    print('Saving images...')
                    cv2.imwrite(imSaveNameDict['name'+str(i)], imModeDict['imMode'+str(i)].Array)
                print('Save successfully')
            except Exception as e:
                print('Failed: ', str(e))
            cv2.waitKey(10)
            return imModeDict, BottleCount, 'FalseBC', None, 'Object not found', 'FalseWL', None, 'Object not found'
    else:
        pass

def ExportCSV(data):
    df = pd.DataFrame(data)
    df.to_csv(path + str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M')) + '.csv')
    print('CSV data has been exported')


if __name__ == '__main__':
    try:
        camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        camera.Open()
        camera.TriggerSoftware.Execute()
        camera.LineSelector = "Line2"
        camera.TriggerMode = "Off"
        camera.CenterX = True
        camera.CenterY = True
        camera.LineInverter = True
        camera.Width = camera.Width.Max
        camera.Height = camera.Height.Max
        camera.LineSource = 'ExposureActive'
    except Exception as e:
        print(e)
        sys.exit()
    ser1 = fst.arduinoPort()
    st = fst.SaveFile_read()
    commandlist, ModeCount = fst.Command_Input(st)
    fst.ledcontrol_send(commandlist)
    WinDict={}
    for i in range(1, ModeCount + 1):
        WinDict['Window'+str(i) ]= pylon.PylonImageWindow()
        WinDict['Window'+str(i) ].Create(i)
    print('Ready to work')
    path = 'G:\Shared drives\Optic\Common\Bottle_Project\Images\\' + str(datetime.datetime.now().strftime('%Y-%m-%d_%H.%M'))

    data = {'Barcode':[],'Water level':[]}

    while True:
        try:
            imModeDict, BottleCount, con1, p1img, p1data, con2, p2img, p2data = FirstProcess(st, ser1, path,camera, ModeCount)
            for i in range(1, ModeCount + 1):
                WinDict['Window' + str(i)].SetImage(imModeDict['imMode' + str(i)])
                WinDict['Window' + str(i)].Show()
            data['Barcode'].append(p1data)
            data['Water level'].append(p2data)
        except:
            keyPressed = cv2.waitKey(100)
            if (keyPressed > 0):
                print('Esc')
                break

            else:
                pass
    ExportCSV(data)
    fst.ledcontrol_send(['cl'])
    print('Program has stopped')