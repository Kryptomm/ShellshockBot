from globals import WEPS
import pyautogui
from PIL import Image, ImageEnhance, ImageGrab, ImageFilter
import kNearestNeighbors as knn
from time import sleep

WEAPON_FIELD = [713,1038,950,1064]
WEAPONPIXELS = []

def loadWeaponPixels():
    global WEAPONPIXELS_ACTIVE
    print("----------------------------------------------------------------")
    print("lade Waffen-Trainings-Daten")
    print("----------------------------------------------------------------")
    file1 = open('data/WeaponPixels.txt', 'r')
    Lines = file1.readlines()

    count = 0
    for line in Lines:
        count += 1
        txt = "{}".format(line.strip())
        d = txt.split(" ")
        for i in range(2,len(d)):
            d[i] = int(d[i])
        WEAPONPIXELS.append([d[2:], d[0].replace("#"," "), int(d[1])])
        if count % 10 == 0: print(f"WAFFEN | {count} von {len(Lines)} geladen")

    WEAPONPIXELS_ACTIVE = True
    print("----------------------------------------------------------------")
    print("Trainings-Daten wurden geladen, schalte nun auf bessere Waffenerkennung um.")
    print("----------------------------------------------------------------")
    
def makeScreenFromWeapons():
    cap = ImageGrab.grab(bbox = (WEAPON_FIELD[0],WEAPON_FIELD[1],WEAPON_FIELD[2],WEAPON_FIELD[3]))
    filter = ImageEnhance.Color(cap)
    cap = filter.enhance(50)
    enhancer = ImageEnhance.Contrast(cap)
    cap = enhancer.enhance(1)
    
    newCap  = Image.new(mode = "RGB", size = (cap.width, cap.height), color = (0, 0, 0))
    for x in range(cap.width):
        for y in range(cap.height):
            color = cap.getpixel((x, y))
            if color[0] >= 230 and color[1] >= 230 and color[2] >= 230: 
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

def getSelectedWeaponNeighbors():
    cap = makeScreenFromWeapons()
    arr, ones = convertTo1DArray(cap)
    new_point = arr
    wep_str = knn.multiThreadfindCategory(new_point, WEAPONPIXELS, 8, ones, fixedK=1)
    
    for wep_cat in WEPS:
        for wep in WEPS[wep_cat]:
            if type(wep) is tuple: wep = wep[0]
            if wep == wep_str: return wep, wep_cat
    return "shot", "normal"

if __name__ == "__main__":
    loadWeaponPixels()
    sleep(3)
    while True:
        wep_data = getSelectedWeaponNeighbors()
        
        print(wep_data)
        
        pyautogui.keyDown("w")
        pyautogui.keyUp("w")
        sleep(0.2)