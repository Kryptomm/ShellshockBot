from PIL.ImageOps import grayscale
import pytesseract, numpy, cv2, pyautogui, math, difflib, time, json, os
from PIL import Image, ImageEnhance, ImageFilter, ImageGrab
from datetime import datetime
from threading import Thread
import pyexcel

pyautogui.FAILSAFE = False

settings = json.load(open("settings.json"))
file_executed_in = os.getcwd()

tesseract = None
if settings["tesseract"] != "local": tesseract = settings["tesseract"]
else: tesseract = f"{file_executed_in}\Tesseract-OCR\\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = tesseract

WIND_FIELD = [946,77,973,95]

def makeScreen():
    cap = ImageGrab.grab(bbox = (WIND_FIELD[0],WIND_FIELD[1],WIND_FIELD[2],WIND_FIELD[3]))

    filter = ImageEnhance.Color(cap)
    new_cap = filter.enhance(0)
    enhancer = ImageEnhance.Contrast(new_cap)
    new_cap = enhancer.enhance(100)

    newCap  = Image.new(mode = "RGB", size = (cap.width, cap.height), color = (0, 0, 0))
    for x in range(cap.width):
        for y in range(cap.height):
            color = cap.getpixel((x, y))
            if color[0] <= 70 and color[1] <= 70 and color[2] <= 70: 
                newCap.putpixel((x,y),(255,255,255))
            else:
                newCap.putpixel((x,y),(0,0,0))
    return newCap

def convertTo1DArray(cap):
    arr = []
    num = 0
    for x in range(cap.width):
        for y in range(cap.height):
            color = cap.getpixel((x, y))
            c = round(0.2989 * color[0] + 0.5870 * color[1] + 0.1140 * color[2])
            if c == 255:
                arr.append(1)
                num += 1
            else: arr.append(0)
    return arr, num

def getName(cap):
    text =  str(pytesseract.image_to_string(cv2.cvtColor(numpy.array(cap), cv2.COLOR_BGR2GRAY),config="--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789")).strip()
    return text


if __name__ == "__main__":
    wait = 2
    time.sleep(wait)

    cap = makeScreen()

    #Filter out Double Numbers
    file1 = open('WindPixels.txt', 'r')
    Lines = file1.readlines()

    WINDPIXELS = {}
    count = 0
    for line in Lines:
        count += 1
        txt = "{}".format(line.strip())
        d = txt.split(" ")
        for i in range(2,len(d)):
            d[i] = int(d[i])
        WINDPIXELS[int(d[0])] = [d[2:], int(d[1])]
    
    file1.close()
    keys = list(WINDPIXELS.keys())
    keys.sort()
    
    file1 = open('WindPixels.txt', 'w')
    for k in keys:
        text = f"{k} {WINDPIXELS[k][1]} "
        d = WINDPIXELS[k][0]
        for p in d: text += str(p) + " "
        text += "\n"
        file1.write(text)
    file1.close()

    name = getName(cap)
    data, num = convertTo1DArray(cap)
    text = f"{name} {num} "
    for p in data: text += str(p) + " "
    text += "\n"

    with open('WindPixels.txt', 'a') as f:
        f.write(text)

    print(name)