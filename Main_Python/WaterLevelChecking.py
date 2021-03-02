import cv2
import imutils as imu
from imutils import contours, perspective
import numpy as np
import pathlib
import os

def Preprocessor(img):
    img = img[900:1000, 700:1600]
    _, th = cv2.threshold(img, 60, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    closing = cv2.morphologyEx(th, cv2.MORPH_GRADIENT, kernel, iterations=2)
    erode = cv2.erode(closing, (3, 3))
    return erode

def WaterLevelDetector(erode):
    cnts = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imu.grab_contours(cnts)
    (cnts, _) = contours.sort_contours(cnts)
    if len(cnts) != 0:
        for cnt in cnts:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 200:
                box = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(box)
                box = np.array(box, dtype="int")
                box = perspective.order_points(box)
                box = box.astype(int)
                return box
            else:
                pass
    else:
        pass

def WaterLevelChecking(img, count, path):
    """
    Kiem tra co hay khong muc nuoc doi voi anh co hieu ung darkfield
    :param img: Anh Darkfield
    :return: True: anh co kha nang muc nuoc
             False: anh khong co muc nuoc
    """

    erode = Preprocessor(img)
    box = WaterLevelDetector(erode)

    if box is not None:
        path = path + r'_result\\DarkField'
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        name = os.path.join(path, str(count) + '.tiff')
        cv2.putText(erode, 'True', (15, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255, 1)

        try:
            print(name, ' :Saving...')
            cv2.imwrite(name, erode)
            print(name, ': Save successfully')
        except Exception as e:
            print('Failed: ', str(e))
        p4data = 'True'
        return 'RightDF',  erode, p4data
    else:
        p4data = 'False'
        cv2.putText(erode, 'False', (15, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255, 1)
        path = path + r'_result\\DarkField'
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        name = os.path.join(path, str(count) + '.tiff')
        try:
            print(name, ' :Saving...')
            cv2.imwrite(name, erode)
            print(name, ': Save successfully')
        except Exception as e:
            print('Failed: ', str(e))
        return 'FalseDF', erode, p4data