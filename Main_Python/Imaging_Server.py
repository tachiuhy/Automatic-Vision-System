from scipy.spatial import distance as dist
from imutils import contours, perspective
from pyzbar.pyzbar import ZBarSymbol
from pyzbar import pyzbar as pzb
import imutils as imu
import numpy as np
import pathlib
import cv2
import os


class Barcode:
    def __init__(self, img):
        img = img[1050:1960, 960:1170]
        equ = cv2.equalizeHist(img)
        self.img_smoothed = cv2.GaussianBlur(equ, (5, 5), np.sqrt(8))
        barcodes = pzb.decode(self.img_smoothed, symbols=[ZBarSymbol.CODE128])
        if len(barcodes) == 0:
            print('Barcode not found')
            self.p1data = 'NULL'
        else:
            for k in barcodes:
                name = k.data
                Sample_name = name[0:11]
                Sample_name = Sample_name.decode("utf-8")
            self.p1data = str(Sample_name)


class WaterChecking:
    """
Kiem tra co hay khong muc nuoc doi voi anh co hieu ung darkfield
:param img: Anh Darkfield
:return: True: anh co kha nang muc nuoc
         False: anh khong co muc nuoc
"""
    def __init__(self, img, count, path):
        self.img = img
        self.count = count
        self.path = path
        self.Preprocessor()
        self.WaterLevelDetector()
        if self.box is not None:
            path = self.path + r'_result\\DarkField'
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            name = os.path.join(path, str(self.count) + '.tiff')
            cv2.putText(self.eroded_img, 'True', (15, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255, 1)

            try:
                print(name, ' :Saving...')
                cv2.imwrite(name, self.eroded_img)
                print(name, ': Save successfully')
            except Exception as e:
                print('Failed: ', str(e))
            self.p4data = 'True'

        else:
            self.p4data = 'False'
            cv2.putText(self.eroded_img, 'False', (15, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255, 1)
            path = self.path + r'_result\\DarkField'
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            name = os.path.join(path, str(self.count) + '.tiff')
            try:
                print(name, ' :Saving...')
                cv2.imwrite(name, self.eroded_img)
                print(name, ': Save successfully')
            except Exception as e:
                print('Failed: ', str(e))

    def Preprocessor(self):
        self.img = self.img[800:1050, 700:1700]
        _, th = cv2.threshold(self.img, 30, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closing = cv2.morphologyEx(th, cv2.MORPH_GRADIENT, kernel, iterations=2)
        self.eroded_img = cv2.erode(closing, (3, 3))

    def WaterLevelDetector(self):
        cnts = cv2.findContours(self.eroded_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imu.grab_contours(cnts)
        if len(cnts) != 0:
            (cnts, _) = contours.sort_contours(cnts)
            for cnt in cnts:
                x, y, w, h = cv2.boundingRect(cnt)
                if w > 200:
                    self.box = cv2.minAreaRect(cnt)
                    self.box = cv2.boxPoints(self.box)
                    self.box = np.array(self.box, dtype="int")
                    self.box = perspective.order_points(self.box)
                    self.box = self.box.astype(int)
                else:
                    pass



class WaterProcess:
    def __init__(self, img, count, path):
        self.path = path
        self.count = count
        self.img = img
        self.img = self.img[300:1000, 600:1800]
        self.img_rgb = cv2.cvtColor(self.img, cv2.COLOR_GRAY2BGR)
        self.edge = self.preprocessing
        box_of_lid = self.detect_lib
        box_of_waterlevel = self.detect_waterlevel
        if box_of_lid is not None and box_of_waterlevel is not None:
            # Tim vi tri cua 2 diem thuoc co chai
            [tll, bll, brl, trl] = self.take4point(box_of_lid)
            pt1 = [tll[0], int(tll[1] + (bll[1] - tll[1]) * 0.55)]
            pt1 = tuple(pt1)
            pt2 = [trl[0], int(trl[1] + (brl[1] - trl[1]) * 0.55)]
            pt2 = tuple(pt2)

            # Tim vi tri mat cong duoi cua muc nuoc
            [_, blw, brw, _] = self.take4point(box_of_waterlevel)
            mid_x_water, mid_y_water = self.mid_point(blw, brw)
            cv2.circle(self.edge, (int(mid_x_water), int(mid_y_water)), 5, 255, -1)

            # Tinh khoang cach tu diem muc nuoc va duong co chai
            mid_x_lib, mid_y_lid = self.mid_point(pt1, pt2)
            cv2.circle(self.edge, (int(mid_x_lib), int(mid_y_lid)), 5, 255, -1)
            mmperpixel = 0.039197
            self.p2data = abs(mid_y_water - mid_y_lid)
            self.p2data = self.p2data * mmperpixel

            if 13.5 < self.p2data < 16.5:                    #######################################
                self.p2data = str(round(self.p2data, 2))
                cv2.drawContours(self.img_rgb, [box_of_waterlevel], -1, (0, 255, 0), 3)
                cv2.drawContours(self.img_rgb, [box_of_lid], -1, (0, 255, 0), 3)
                cv2.putText(self.edge, 'True', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
            else:
                cv2.drawContours(self.img_rgb, [box_of_waterlevel], -1, (0, 0, 255), 3)
                cv2.drawContours(self.img_rgb, [box_of_lid], -1, (0, 0, 255), 3)
                cv2.putText(self.edge, 'False', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
                self.p2data = 'Water level is wrong'
            # Tinh do ho nam cua lo
            mid_x_top, mid_y_top = self.mid_point(tll, trl)
            u1_x = int(trl[0] - mid_x_top)
            u1_y = int(trl[1] - mid_y_top)
            u2_x = 200
            u2_y = 0
            self.p3data = np.arccos((abs(u1_x * u2_x + u1_y * u2_y)) / (
                    np.sqrt(pow(u1_x, 2) + pow(u1_y, 2)) * np.sqrt(pow(u2_x, 2) + pow(u2_y, 2))))
            if self.p3data > 0.03:
                cv2.circle(self.img_rgb, (int(mid_x_top + 100), int(mid_y_top)), 20, (0, 0, 255))
                cv2.line(self.img_rgb, (int(mid_x_top), int(mid_y_top)), (int(mid_x_top + 200), int(mid_y_top)), (0, 0, 255), 2)
                cv2.circle(self.edge, (int(mid_x_top + 50), int(mid_y_top)), 20, 255)
                cv2.line(self.edge, (int(mid_x_top), int(mid_y_top)), (int(mid_x_top + 100), int(mid_y_top)), 255, 2)
                self.p3data = 'Cap opening'
            else:
                cv2.circle(self.edge, (int(mid_x_top + 50), int(mid_y_top)), 20, 255)
                cv2.line(self.edge, (int(mid_x_top), int(mid_y_top)), (int(mid_x_top + 100), int(mid_y_top)), 255, 2)
                self.p3data = str(self.p3data)

            path = self.path + r'_result\\BackLight'
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            name = os.path.join(path, str(count) + '.tiff')

            try:
                print(name, ' :Saving...')
                cv2.imwrite(name, self.edge)
                print(name, ': Save successfully')
            except Exception as e:
                print('Failed: ', str(e))

        else:
            cv2.putText(self.edge, 'False', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
            self.p2data = 'Water level is wrong'
            self.p3data = 'Cap is opening'
            path = self.path + r'_result\\BackLight'
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            name = os.path.join(path, str(count) + '.tiff')
            try:
                print(name, ' :Saving...')
                cv2.imwrite(name, self.edge)
                print(name, ': Save successfully')
            except Exception as e:
                print('Failed: ', str(e))

    def preprocessing(self):
        img1 = self.img[0: 400, :]
        _, img1 = cv2.threshold(img1, 25, 255, cv2.THRESH_TOZERO)
        _, img1 = cv2.threshold(img1, 25, 255, cv2.THRESH_BINARY)
        kernel = np.ones((9, 9), np.uint8)
        img1 = cv2.morphologyEx(img1, cv2.MORPH_CLOSE, kernel)
        img1 = cv2.erode(img1, (7, 7), iterations=1)
        img1 = cv2.morphologyEx(img1, cv2.MORPH_OPEN, kernel)

        img2 = self.img[400:500, :]
        img2 = cv2.GaussianBlur(img2, (5, 5), np.sqrt(16))
        _, img2 = cv2.threshold(img2, 1, 255, cv2.THRESH_BINARY)

        img3 = self.img[500::, :]
        kernel1 = np.ones((5, 5), np.uint8)
        _, img3 = cv2.threshold(img3, 50, 255, cv2.THRESH_BINARY)
        img3 = cv2.morphologyEx(img3, cv2.MORPH_CLOSE, kernel1)
        img3 = cv2.erode(img3, (7, 7), iterations=3)
        img3 = cv2.morphologyEx(img3, cv2.MORPH_OPEN, kernel1)

        self.hold = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
        self.hold[0:400, :] = img1
        self.hold[400:500, :] = img2
        self.hold[500::, :] = img3
        self.hold = imu.auto_canny(self.hold)
        self.hold = cv2.dilate(self.hold, (3, 3), iterations=2)

    def detect_lib(self):
        cnts = cv2.findContours(self.edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imu.grab_contours(cnts)
        (cnts, _) = contours.sort_contours(cnts)
        for cnt in cnts:
            area = cv2.contourArea(cnt)
            if (area > 90000):
                box = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(box)
                box = np.array(box, dtype="int")
                box = perspective.order_points(box)
                box = box.astype(int)
                #print('box', box)
                cv2.drawContours(self.img_rgb, [box], -1, (0, 0, 255), 3)
                cv2.drawContours(self.edge, [box], -1, 255, 3)
                return box
            else:
                pass

    def detect_waterlevel(self):
        cnts = cv2.findContours(self.edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imu.grab_contours(cnts)
        (cnts, _) = contours.sort_contours(cnts)
        for cnt in cnts:
            area = cv2.contourArea(cnt)
            if ( 2000 < area < 100000):
                box1 = cv2.minAreaRect(cnt)
                box1 = cv2.boxPoints(box1)
                box1 = np.array(box1, dtype="int")
                box1 = perspective.order_points(box1)
                box1 = box1.astype(int)
                cv2.drawContours(self.img_rgb, [box1], -1, (0, 0, 255), 3)
                cv2.drawContours(self.edge, [box1], -1, 255, 3)
                return box1
            else:
                pass

    def take4point(self, pc):
        # Sắp xếp các điểm có từ nhỏ đến lớn theo giá trị của trụ x trong ma trận
        xSorted = pc[np.argsort(pc[:, 0]), :]

        # Thu được những điểm có tọa độ gần trụ y (leftmost) và xa trụ y (rightmost) nhất
        leftmost = xSorted[:2, :]
        rightmost = xSorted[2:, :]

        # Từ ma trận chứa 2 điểm gần y nhất
        leftmost = leftmost[np.argsort(leftmost[:, 1]), :]
        (tl, bl) = leftmost

        # Tìm 2 điểm còn lại bằng tính khoảng cách
        D = dist.cdist(tl[np.newaxis], rightmost, 'euclidean')[0]
        (br, tr) = rightmost[np.argsort(D)[::-1], :]
        return np.array([tl, bl, br, tr], dtype='int')

    def mid_point(self, point1, point2):
        return (point1[0] + point2[0]) * 0.5, (point1[1] + point2[1]) * 0.5