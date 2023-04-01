from PIL.ImageOps import grayscale
import pyautogui
from time import sleep
import pytesseract, numpy, cv2
from PIL import ImageGrab 
import math
from PIL import Image, ImageEnhance

RULES = """
        ~~~DAS IST EIN BILLIGER FARMBOT FÜR NORMALES TEAM-DEATHMATCH~~~
            REGELN:
                -Fenster: Vollbild
                -Map-Color: Blue
                -Map-Mode: Generated/LowerXP: Eine Flache Map
                -Mode: Deathmatch
                -Players: 2
                -Wind: High
                -Shot-Type: Single
                -Mod: One-Wep
                -Obstacles: <=Med 
            Aktiviere den Bot in der Lobby und sei nicht bereit!
        """

#Koordinaten
READY_BUTTON = [1177,952,1608,986]
XP_FIELD = [312,120,440,150]
WIND_FIELD = [946,77,973,95]
WIND_FIELD_RIGHT = [985,74,1000,93]
WIND_FIELD_LEFT = [919,74,934,93]

#Faktoren
WIND_FACTOR = 6.433

#FARBEN
MyTank = (0, 220, 15)
EnemyTank = (194,3,3)

tesseract = open("settings.txt").read()
pytesseract.pytesseract.tesseract_cmd = tesseract
pyautogui.FAILSAFE = False

#!Lobby-Functions
def getXP():
    cap = ImageGrab.grab(bbox = (XP_FIELD[0],XP_FIELD[1],XP_FIELD[2],XP_FIELD[3]))
    xp_str =  pytesseract.image_to_string(cv2.cvtColor(numpy.array(cap), cv2.COLOR_BGR2GRAY))
    xp = ""
    for char in xp_str:
        if char.isdigit(): xp += char
    return int(xp)

def waitForLobby():
    inLobby = pyautogui.locateOnScreen("Images/ReadyButton.png", grayscale=True, confidence=0.9)
    if inLobby: return True
    else: return False

def pressReady():
    readyButton = pyautogui.locateOnScreen("Images/ReadyButton.png", grayscale=True, confidence=0.9)
    pyautogui.click(readyButton[0],readyButton[1])
    pyautogui.click(0,0)

#!Game-Functions
def calculateDestiny(wind,angle,strengh):
    Delta_Angle = (angle-90)*87
    Delta_Wind = WIND_FACTOR*wind
    Delta_Strengh = (strengh/100)**2
    return (Delta_Angle*Delta_Strengh + Delta_Wind)

def getTankCoordinates(tankColor):
    s = pyautogui.screenshot(region=(0,0,1920,927))
    pyautogui.FAILSAFE = False

    allds = []
    allcords = []
    tolerance=0.03

    for x in range(0,s.width,2):
        for y in range(0,s.height,2):
            color = s.getpixel((x, y))
            d = math.sqrt((color[0]-tankColor[0])**2+(color[1]-tankColor[1])**2+(color[2]-tankColor[2])**2)
            allds.append(d)
            allcords.append([x,y])
    min_d = min(allds)*(1-tolerance)
    max_d = min(allds)*(1+tolerance)

    newcords = []

    for x in range(len(allds)):
        if allds[x] >= min_d and allds[x] <= max_d:
            newcords.append(allcords[x])
    average_x, average_y = 0,0
    for x in newcords:
        average_x += x[0]
        average_y += x[1]
    average_x = average_x/len(newcords)
    average_y = average_y/len(newcords)

    return [int(average_x), int(average_y)]

def myTurn():
    myTurn = pyautogui.locateOnScreen("Images/FireButton.png", confidence=0.9)
    if myTurn == None: return False
    else: return True

def resetAngle(myPos):
    pyautogui.click(myPos[0], myPos[1]-300)
    for x in range(30):
        pyautogui.press("up")

def getWind():
    answers=[]
    cap = ImageGrab.grab(bbox = (WIND_FIELD[0],WIND_FIELD[1],WIND_FIELD[2],WIND_FIELD[3]))

    for x in [Image.LANCZOS, Image.BILINEAR, Image.BICUBIC, Image.BOX, Image.HAMMING, Image.NEAREST]:
        new_cap = cap.resize((cap.width*20,cap.height*20), resample=x)
        filter = ImageEnhance.Color(new_cap)
        new_cap = filter.enhance(0)
        enhancer = ImageEnhance.Contrast(new_cap)
        new_cap = enhancer.enhance(100)
        text =  str(pytesseract.image_to_string(cv2.cvtColor(numpy.array(new_cap), cv2.COLOR_BGR2GRAY),config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')).strip()
        if len(text) >= 1: answers.append(text)

    speicher = []
    highest_num = [0,0]
    for x in answers:
        if x not in speicher:
            speicher.append(x)
    for x in speicher:
        count = answers.count(x)
        if count > highest_num[1]:
            highest_num = [x,count]

    richtung = None
    for CORDS in (WIND_FIELD_LEFT, WIND_FIELD_RIGHT):
        cap = ImageGrab.grab(bbox = (CORDS[0],CORDS[1],CORDS[2],CORDS[3]))
        filter = ImageEnhance.Color(cap)
        cap = filter.enhance(0)
        enhancer = ImageEnhance.Contrast(cap)
        cap = enhancer.enhance(100)
        if cap.getpixel((int(cap.width/2),int(cap.height/2))) == (255,255,255):
            if CORDS == WIND_FIELD_RIGHT: richtung = "Rechts"
            else: richtung = "Links"


    return int(highest_num[0]), richtung

def shoot():
    pyautogui.click(1200, 1000)
    pyautogui.click(0, 0)

def getBestAngle(wind,myX,eX):
    delta = eX-myX
    bestangle = 0
    bestDeltaDif = 10000000
    beststrengh = 0
    for a in range(50,131):
        for s in range(20,101):
            calcAngle = calculateDestiny(wind,a,s)
            if abs(calcAngle - delta) < bestDeltaDif:
                bestangle = a
                beststrengh = s
                bestDeltaDif = abs(calcAngle - delta)
    print(bestDeltaDif)
    return bestangle,beststrengh

def play():
    while waitForLobby(): sleep(0.2)
    sleep(10)
    myPos = getTankCoordinates(MyTank)
    enemyPos = getTankCoordinates(EnemyTank)

    print(myPos, enemyPos)
    while True:
        while myTurn() == False:
            sleep(0.5)
            if waitForLobby(): return
        print("My Turn")
        myPos = getTankCoordinates(MyTank)
        enemyPos = getTankCoordinates(EnemyTank)
        resetAngle(myPos)

        #Alles für den Shot
        wind = getWind()
        delta_x = myPos[0] - enemyPos[0]
        calc_wind = wind[0]
        if delta_x >= 0: delta_x *= -1
        if wind[1] == "Links":
            calc_wind = wind[0] * -1
        shoot_data = getBestAngle(calc_wind,myPos[0],enemyPos[0])
        angle = shoot_data[0]
        strengh = shoot_data[1]
        key = "left"
        if angle > 90: key="right"
        angle_delta = abs(angle-90)
        print(angle_delta, strengh, wind)
        for x in range(angle_delta):
            pyautogui.press(key)
        for x in range(abs(strengh-100)):
            pyautogui.press("down")
        shoot()
        print("Meinen Turn beendet")

def main(debugMode=False):
    #Regeln einmal printen
    print(RULES)

    #ErsterStart
    if debugMode == False:
        if waitForLobby() == False:
            print("Starte von der Lobby aus!")
            return
        first_xp = getXP()
        print(f"Deine aktuelle XP-Anzahl beträgt: {first_xp}")

    #Die Unendliche Schleife
    while True:
        pressReady()
        if debugMode == False:
            while waitForLobby(): sleep(1)
        play()
        nowXP = getXP()
        print(f"Deine aktuelle XP-Anzahl beträgt: {nowXP}\nSomit hast du {nowXP-first_xp} XP gemacht!")

if __name__ == "__main__":
    wait = 3
    for x in range(wait):
        print(f"starting in {wait-x}...")
        sleep(1)
    print(main(debugMode=False))