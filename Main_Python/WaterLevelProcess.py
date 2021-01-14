import cv2
import os
from imutils import contours, perspective
import imutils as imu
from scipy.spatial import distance as dist
import numpy as np
import pathlib

def preprocessing(img):
    img1 = img[0: 100, :]
    _, img1 = cv2.threshold(img1, 50, 255, cv2.THRESH_TOZERO)
    _, img1 = cv2.threshold(img1, 50, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    img1 = cv2.morphologyEx(img1, cv2.MORPH_CLOSE, kernel)
    img1 = cv2.erode(img1, (5, 5), iterations=1)
    img1 = cv2.morphologyEx(img1, cv2.MORPH_OPEN, kernel)

    img2 = img[100:130, :]
    img2 = cv2.GaussianBlur(img2, (5, 5), np.sqrt(16))
    _, img2 = cv2.threshold(img2, 1, 255, cv2.THRESH_BINARY)
    img2 = cv2.morphologyEx(img2, cv2.MORPH_CLOSE, kernel)
    img2 = cv2.erode(img2, (13, 13), iterations=1)
    img2 = cv2.morphologyEx(img2, cv2.MORPH_OPEN, kernel)

    img3 = img[130::, :]
    _, img3 = cv2.threshold(img3, 50, 255, cv2.THRESH_BINARY)
    img3 = cv2.morphologyEx(img3, cv2.MORPH_CLOSE, kernel)
    img3 = cv2.erode(img3, (5, 5), iterations=1)
    img3 = cv2.morphologyEx(img3, cv2.MORPH_OPEN, kernel)

    hold = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
    hold[0:100, :] = img1
    hold[100:130, :] = img2
    hold[130::, :] = img3
    hold = imu.auto_canny(hold)
    return hold
def detect_lib(edge):
    cnts = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imu.grab_contours(cnts)
    (cnts, _) = contours.sort_contours(cnts)
    #print(len(cnts))
    if len(cnts) >= 2:
        box = cv2.minAreaRect(cnts[0])
        box = cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        box = perspective.order_points(box)
        cv2.drawContours(edge, [box.astype('int')], -1, (255, 0, 0), 1)
        box = box.astype(int)

        box1 = cv2.minAreaRect(cnts[1])
        box1 = cv2.boxPoints(box1)
        box1 = np.array(box1, dtype="int")
        box1 = perspective.order_points(box1)
        cv2.drawContours(edge, [box1.astype('int')], -1, (255, 0, 0), 1)
        box1 = box1.astype(int)
        if box[0][1] < box1[0][1]:
            return box
        if box[0][1] > box1[0][1]:
            return box1

    else:
        return None
def detect_waterlevel(edge):
    cnts = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imu.grab_contours(cnts)
    (cnts, _) = contours.sort_contours(cnts)

    if len(cnts) >= 2:
        box = cv2.minAreaRect(cnts[0])
        box = cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        box = perspective.order_points(box)
        cv2.drawContours(edge, [box.astype('int')], -1, (255, 0, 0), 1)
        box = box.astype(int)

        box1 = cv2.minAreaRect(cnts[1])
        box1 = cv2.boxPoints(box1)
        box1 = np.array(box1, dtype="int")
        box1 = perspective.order_points(box1)
        cv2.drawContours(edge, [box1.astype('int')], -1, (255, 0, 0), 1)
        box1 = box1.astype(int)
        if box[0][1] > box1[0][1]:
            return box
        if box[0][1] < box1[0][1]:
            return box1
    else:
        return None
def take4point(pc):
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
def mid_point(point1, point2):
    return ((point1[0] + point2[0])*0.5, (point1[1] +point2[1])*0.5)
def water_level_val(pt1, pt2, mid_ptX, mid_ptY):
    a = pt2[1] - pt1[1]
    b = pt1[0] - pt2[0]
    c = a * pt1[0] + b * pt1[1]
    level_val = (np.abs(a*mid_ptX + b*mid_ptY + c))/np.sqrt(a**2 + b**2)
    cmperpixel = 9/2056
    level_val_cm = level_val*cmperpixel
    return level_val_cm
def WaterLevelProcess(img,count,path):

    img = img[350:800, 960:1500]
    img = imu.resize(img, width=200)
    edge = preprocessing(img)
    box_of_lid = detect_lib(edge)
    box_of_waterlevel = detect_waterlevel(edge)
    if box_of_lid is not None:
        [tll, bll, brl, trl] = take4point(box_of_lid)
        pt1 = []
        pt1.append(tll[0])
        pt1.append(int(tll[1] + (bll[1] - tll[1]) * 0.75))
        pt1 = tuple(pt1)
        pt2 = []
        pt2.append(trl[0])
        pt2.append(int(trl[1] + (brl[1] - trl[1]) * 0.75))
        pt2 = tuple(pt2)
        cv2.line(edge, pt1, pt2, 255, 2)
    else:
        pass

    if box_of_waterlevel is not None:
        [_, blw, brw, _] = take4point(box_of_waterlevel)
        mid_x, mid_y = mid_point(blw, brw)
        cv2.circle(edge, (int(mid_x), int(mid_y)), 3, 255, -1)
        p2data = water_level_val(pt1, pt2, int(mid_x), int(mid_y))
        p2data = round(p2data, 4)
        print(p2data)
        path = path + '_result'
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        name = os.path.join(path, str(count) + '.tiff')

        try:
            print(name, ' :Saving...')
            cv2.imwrite(name, edge)
            print(name, ': Save successfully')
        except Exception as e:
            print('Failed: ', str(e))
        return 'RightWL', edge, str(p2data)

    else:
        p2data = 'Water level is wrong'
        path = path + '_result'
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        name = os.path.join(path, str(count) + '.tiff')
        try:
            print(name, ' :Saving...')
            cv2.imwrite(name, edge)
            print(name, ': Save successfully')
        except Exception as e:
            print('Failed: ', str(e))
        return 'FalseWL', edge, p2data
