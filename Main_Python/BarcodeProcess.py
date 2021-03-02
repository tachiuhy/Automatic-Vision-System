import cv2
from pyzbar import pyzbar as pzb
from pyzbar.pyzbar import ZBarSymbol
import numpy as np

def Barcode(img):
    img = img[1060:1960, 950:1170]
    equ = cv2.equalizeHist(img)
    img_smoothed = cv2.GaussianBlur(equ, (5, 5), np.sqrt(8))
    barcodes = pzb.decode(img_smoothed, symbols=[ZBarSymbol.CODE128])
    if len(barcodes) == 0:
        print('Barcode not found')
        p1data ='NULL'
        return 'FalseBC', img_smoothed, p1data
    else:
        for k in barcodes:
            name = k.data
            Sample_name = name[0:11]
            Sample_name = Sample_name.decode("utf-8")
        p1data = str(Sample_name)

        return 'RightBC', img_smoothed, p1data