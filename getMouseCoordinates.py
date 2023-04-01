from ctypes import windll, Structure, c_long, byref
from time import sleep
import pyautogui
import math


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

HealtBar1 = (6,255,25)
HealtBar1 = (33,255,25)
MyTank = (0, 220, 15)


def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    im = pyautogui.screenshot()
    px = im.getpixel((pt.x, pt.y))
    return { "x": pt.x, "y": pt.y, "color": px , "dif": math.sqrt((px[0]-MyTank[0])**2+(px[1]-MyTank[1])**2+(px[2]-MyTank[2])**2)}

while True:
    pos = queryMousePosition()
    print(pos)
    sleep(1)

