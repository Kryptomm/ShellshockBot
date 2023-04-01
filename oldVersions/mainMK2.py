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
WIND_FACTOR = 6.467

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

def inLobby():
    inLobby = pyautogui.locateOnScreen("Images/ReadyButton.png", grayscale=True, confidence=0.9)
    if inLobby: return True
    else: return False

def pressReady():
    readyButton = pyautogui.locateOnScreen("Images/ReadyButton.png", grayscale=True, confidence=0.9)
    pyautogui.click(readyButton[0],readyButton[1])
    pyautogui.click(0,0)

#!Game-Functions
#^Schuss-Functions
#*Gibt die Schussweite in Pixel wieder
def calculateDestiny(wind,angle):
    Delta_Angle = (angle-90)*87
    Delta_Wind = WIND_FACTOR*wind
    return (Delta_Angle + Delta_Wind)

#*gibt mir den Besten Schusswinkel wieder
def getBestAngle(wind,myX,eX):
    delta = eX-myX
    bestangle = 0
    bestDeltaDif = 10000000
    for a in range(50,131):
        calcAngle = calculateDestiny(wind,a)
        if abs(calcAngle - delta) < bestDeltaDif:
            bestangle = a
            bestDeltaDif = abs(calcAngle - delta)
    return bestangle

#*Drückt auf Shoot
def shoot():
    pyautogui.click(1200, 1000)
    pyautogui.click(0, 0)

#^Overview-Functions
#*Gibt die Koordinaten eines Gegners wieder und von mir
def getTankCoordinates(tankColor):
    s = pyautogui.screenshot(region=(0,100,1920,927))
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

def isTankInSameBox(x,y):
    return

#*Wenn ich dran bin gibt dieser True zurück
def myTurn():
    myTurn = pyautogui.locateOnScreen("Images/FireButton.png", confidence=0.9)
    if myTurn == None: return False
    else: return True

#*Setzt meinen Schussradius auf 100,90 (probiert es zumindest LOL)
def resetAngle(myPos):
    pyautogui.click(myPos[0], myPos[1]-300)
    for x in range(30):
        pyautogui.press("up")

#*Gibt mir den Wind zurück
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

#^Play-Loop
#*Dieser Loop wird solange ausgeführt, wie der Spiel sich im Spiel befindet
def play():
    while inLobby(): sleep(0.2)
    sleep(10)
    myPos = getTankCoordinates(MyTank)
    enemyPos = getTankCoordinates(EnemyTank)
    round = 1
    print(f"Meine Position: {myPos}\nGegner Position: {enemyPos}")
    while True:
        while myTurn() == False:
            sleep(0.5)
            if inLobby(): return
        print(f"Ich bin nun dran! Wir befinden uns in Runde {round}")

        #Kriege Koordinaten
        myPos = getTankCoordinates(MyTank)
        enemyPos = getTankCoordinates(EnemyTank)
        resetAngle(myPos)

        #Schuss-Kalkulation
        wind = getWind()
        delta_x = myPos[0] - enemyPos[0]
        calc_wind = wind[0]
        if delta_x >= 0: delta_x *= -1
        if wind[1] == "Links":
            calc_wind = wind[0] * -1
        shoot_data = getBestAngle(calc_wind,myPos[0],enemyPos[0])
        angle = shoot_data
        key = "left"
        if angle > 90: key="right"
        angle_delta = abs(angle-90)

        #Schuss-Ausrichtung
        for x in range(angle_delta):
            pyautogui.press(key)
        shoot()
        print("Meinen Turn beendet")
        round += 1

def main(debugMode=False):
    #Regeln einmal printen
    print(RULES)

    #ErsterStart
    if debugMode == False:
        if inLobby() == False:
            print("Starte von der Lobby aus!")
            return
        first_xp = getXP()
        print(f"Deine aktuelle XP-Anzahl beträgt: {first_xp}")

    #Die Unendliche Schleife
    while True:
        pressReady()
        if debugMode == False:
            while inLobby(): sleep(1)
        play()
        nowXP = getXP()
        print(f"Deine aktuelle XP-Anzahl beträgt: {nowXP}\nSomit hast du {nowXP-first_xp} XP bisher gemacht!")

if __name__ == "__main__":
    wait = 3
    for x in range(wait):
        print(f"starting in {wait-x}...")
        sleep(1)
    print(main(debugMode=False))