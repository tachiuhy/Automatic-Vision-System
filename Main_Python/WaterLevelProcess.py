import cv2
import os
from imutils import contours, perspective
import imutils as imu
from scipy.spatial import distance as dist
import numpy as np
import pathlib
import matplotlib.pyplot as plt


def preprocessing(img):
    img1 = img[0: 400, :]
    plt.figure(5), plt.imshow(img1, cmap='gray')
    _, img1 = cv2.threshold(img1, 50, 255, cv2.THRESH_TOZERO)
    _, img1 = cv2.threshold(img1, 50, 255, cv2.THRESH_BINARY)
    kernel = np.ones((9, 9), np.uint8)
    img1 = cv2.morphologyEx(img1, cv2.MORPH_CLOSE, kernel)
    img1 = cv2.erode(img1, (7, 7), iterations=1)
    img1 = cv2.morphologyEx(img1, cv2.MORPH_OPEN, kernel)

    img2 = img[400:500, :]
    plt.figure(4),plt.imshow(img2, cmap='gray')
    img2 = cv2.GaussianBlur(img2, (5, 5), np.sqrt(16))
    _, img2 = cv2.threshold(img2, 1, 255, cv2.THRESH_BINARY)


    img3 = img[500::, :]
    plt.figure(3),plt.imshow(img3, cmap='gray')
    kernel1 = np.ones((5, 5), np.uint8)
    _, img3 = cv2.threshold(img3, 50, 255, cv2.THRESH_BINARY)
    img3 = cv2.morphologyEx(img3, cv2.MORPH_CLOSE, kernel1)
    img3 = cv2.erode(img3, (7, 7), iterations=3)
    img3 = cv2.morphologyEx(img3, cv2.MORPH_OPEN, kernel1)

    hold = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
    hold[0:400, :] = img1
    hold[400:500, :] = img2
    hold[500::, :] = img3
    hold = imu.auto_canny(hold)
    hold = hold*2
    hold = cv2.dilate(hold, (5, 5))
    return hold

def detect_lib(edge, img_rgb):
    cnts = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imu.grab_contours(cnts)
    (cnts, _) = contours.sort_contours(cnts)
    for cnt in cnts:
        area = cv2.contourArea(cnt)
        if (area > 100000):
            box = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(box)
            box = np.array(box, dtype="int")
            box = perspective.order_points(box)
            box = box.astype(int)
            #print('box', box)
            cv2.drawContours(img_rgb, [box], -1, (0, 0, 255), 3)
            return box
        else:
            pass

def detect_waterlevel(edge, img_rgb):
    cnts = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
            cv2.drawContours(img_rgb, [box1], -1, (0, 0, 255), 3)
            return box1
        else:
            pass

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
    cmperpixel = 0.0039197
    level_val_cm = level_val*cmperpixel
    return level_val_cm

def WaterLevelProcess(img,count,path):

    img = img[300:1000, 700:1700]
    img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    edge = preprocessing(img)
    box_of_lid = detect_lib(edge, img_rgb)
    box_of_waterlevel = detect_waterlevel(edge, img_rgb)
    if box_of_lid is not None and box_of_waterlevel is not None:
        # Tim vi tri cua 2 diem thuoc co chai
        [tll, bll, brl, trl] = take4point(box_of_lid)
        pt1 = []
        pt1.append(tll[0])
        pt1.append(int(tll[1] + (bll[1] - tll[1]) * 0.55))
        pt1 = tuple(pt1)
        pt2 = []
        pt2.append(trl[0])
        pt2.append(int(trl[1] + (brl[1] - trl[1]) * 0.55))
        pt2 = tuple(pt2)

        # Tim vi tri mat cong duoi cua muc nuoc
        [_, blw, brw, _] = take4point(box_of_waterlevel)
        mid_x, mid_y = mid_point(blw, brw)
        cv2.circle(edge, (int(mid_x), int(mid_y)), 3, 255, -1)

        # Tinh khoang cach tu diem muc nuoc va duong co chai
        mid_x_lib, mid_y_lid = mid_point(pt1, pt2)
        cmperpixel = 0.0039197
        p2data = abs(mid_y - mid_y_lid)
        p2data = p2data * cmperpixel
        if 1.35 < p2data < 1.65:
            cv2.drawContours(img_rgb, [box_of_waterlevel], -1, (0, 255, 0), 3)
            cv2.drawContours(img_rgb, [box_of_lid], -1, (0, 255, 0), 3)
            cv2.drawContours(edge, [box_of_waterlevel], -1, 255, 3)
            cv2.drawContours(edge, [box_of_lid], -1, 255, 3)
            cv2.putText(img_rgb, 'True', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(edge, 'True', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
        else:
            cv2.drawContours(img_rgb, [box_of_waterlevel], -1, (0, 0, 255), 3)
            cv2.drawContours(img_rgb, [box_of_lid], -1, (0, 0, 255), 3)
            cv2.drawContours(edge, [box_of_waterlevel], -1, 255, 3)
            cv2.drawContours(edge, [box_of_lid], -1, 255, 3)
            cv2.putText(img_rgb, 'False', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(edge, 'False', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
            p2data = 'Water level is wrong'
        # Tinh do ho nam cua lo
        p3data = water_level_val(pt1, pt2, int(mid_x_lib), int(mid_y_lid))
        path = path + r'_result\\BackLight'
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        name = os.path.join(path, str(count) + '.tiff')

        try:
            print(name, ' :Saving...')
            cv2.imwrite(name, edge)
            print(name, ': Save successfully')
        except Exception as e:
            print('Failed: ', str(e))

        return 'RightWL', img_rgb, str(p2data), str(p3data)
    else:
        cv2.putText(img_rgb, 'False', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(edge, 'False', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
        p2data = 'Water level is wrong'
        p3data = 'Cap not found'
        path = path + r'_result\\BackLight'
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        name = os.path.join(path, str(count) + '.tiff')
        try:
            print(name, ' :Saving...')
            cv2.imwrite(name, edge)
            print(name, ': Save successfully')
        except Exception as e:
            print('Failed: ', str(e))
        return 'FalseWL', img_rgb, p2data, p3data