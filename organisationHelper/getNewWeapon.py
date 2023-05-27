import pytesseract, numpy, cv2, pyautogui, difflib, time
from PIL import Image, ImageEnhance, ImageGrab
from globals import WEPS
import keyboard
pyautogui.FAILSAFE = False

WEAPON_FIELD = [713,1038,950,1064]

def makeScreen():
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

def getName(cap):
    wep_str =  pytesseract.image_to_string(cv2.cvtColor(numpy.array(cap), cv2.COLOR_BGR2GRAY))
    wep_str = wep_str.lower().strip()
    highest_ratio = 0
    current_wep = wep_str
    for wep_cat in WEPS:
        for wep in WEPS[wep_cat]:
            if type(wep) is tuple: wep = wep[0]
            r = difflib.SequenceMatcher(None, wep_str, wep.lower()).ratio()
            if r > highest_ratio:
                highest_ratio = r
                current_wep = wep
    return current_wep

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

if __name__ == "__main__":
    wait = 3
    time.sleep(wait)
    print("Starting")
    while True:
        time.sleep(1)
        if keyboard.is_pressed('t'): break

        cap = makeScreen()
        name = getName(cap)
        data, num = convertTo1DArray(cap)
        name = name.replace(" ", "#")

        text = f"{name} {num} "
        for p in data: text += str(p) + " "
        text += "\n"

        with open('WeaponPixels.txt', 'a') as f:
            f.write(text)

        print(name)
        pyautogui.keyDown("w")
        pyautogui.keyUp("w")
    
    print("Gestoppt")