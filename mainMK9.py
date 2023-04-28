import pytesseract
import numpy
import cv2
import pyautogui
import math
import difflib
import time
import json
import os
import kNearestNeighbors as knn
import queue
from PIL import Image, ImageEnhance, ImageGrab, ImageFilter
from datetime import datetime
from threading import Thread 
from weapons import WEPS

RULES = """
        ~~~DAS IST EIN BILLIGER FARMBOT FÜR XP~~~
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

#Variablen
RADIUS = 343
DRIVEDISTANCE = 433
WEAPONPIXELS = []
WEAPONPIXELS_ACTIVE = False
WINDPIXELS = []
WINDPIXELS_ACTIVE = False

#Temp-Variablen
INLOBBY = True
SHOOTING = False

#Koordinaten
READY_BUTTON = [1177,952,1608,986]
XP_FIELD = [312,120,440,150]
WIND_FIELD = [946,77,973,95]
WIND_FIELD_RIGHT = [985,74,1000,93]
WIND_FIELD_LEFT = [919,74,934,93]
WEAPON_FIELD = [713,1038,950,1064]
SHOOTLINE_FIELD = [-30,-300,30,20]
GAME_FIELD = [0,0,1920,920]
TANK1BOX = [100,720]
TANK2BOX = [1200,1820]

#FARBEN
MyTank = (0, 220, 15)
EnemyTank = (194,3,3)
Gear = (244,245,126)
Terrain = (64,217,255)

#Sonstiges
settings = json.load(open("settings.json"))
file_executed_in = os.getcwd()

tesseract = None
if os.path.exists(f"{file_executed_in}\Tesseract-OCR\\tesseract.exe"):
    tesseract = f"{file_executed_in}\Tesseract-OCR\\tesseract.exe"
else: tesseract = settings["bot"]["tesseract"]

pytesseract.pytesseract.tesseract_cmd = tesseract
pyautogui.FAILSAFE = False

#!Sonstiges-Functions
#*Lade die WeaponPixel Daten
def loadWeaponPixels():
    global WEAPONPIXELS_ACTIVE
    print("----------------------------------------------------------------")
    print("lade Waffen-Trainings-Daten")
    print("----------------------------------------------------------------")
    file1 = open('WeaponPixels.txt', 'r')
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

#*Lade die WindPixel Daten
def loadWindPixels():
    global WINDPIXELS_ACTIVE
    print("----------------------------------------------------------------")
    print("lade Wind-Trainings-Daten")
    print("----------------------------------------------------------------")
    file1 = open('WindPixels.txt', 'r')
    Lines = file1.readlines()

    count = 0
    for line in Lines:
        count += 1
        txt = "{}".format(line.strip())
        d = txt.split(" ")
        for i in range(2,len(d)):
            d[i] = int(d[i])
        WINDPIXELS.append([d[2:], d[0], int(d[1])])
        if count % 10 == 0: print(f"WIND | {count} von {len(Lines)} geladen")

    WINDPIXELS_ACTIVE = True
    print("----------------------------------------------------------------")
    print("Trainings-Daten wurden geladen, schalte nun auf bessere Winderkennung um.")
    print("----------------------------------------------------------------")

#*Mache Screenshots
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

def makeScreenFromWind():
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

def makeScreenFromGame():
    cap = ImageGrab.grab(bbox = (GAME_FIELD[0],GAME_FIELD[1],GAME_FIELD[2],GAME_FIELD[3]))

    filter = ImageEnhance.Color(cap)
    new_cap = filter.enhance(0)
    enhancer = ImageEnhance.Contrast(new_cap)
    new_cap = enhancer.enhance(10)
    new_cap = new_cap.filter(ImageFilter.EDGE_ENHANCE)
    
    return new_cap

#*Wandle den Screenshot einer Waffe zu einem 1D-Array um
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

#!Lobby-Functions
#*Lese die XP, wenn dies nicht möglich ist. Gib 0 wieder
def getXP():
    cap = ImageGrab.grab(bbox = (XP_FIELD[0],XP_FIELD[1],XP_FIELD[2],XP_FIELD[3]))
    xp_str =  pytesseract.image_to_string(cv2.cvtColor(numpy.array(cap), cv2.COLOR_BGR2GRAY))
    xp = ""
    for char in xp_str:
        if char.isdigit(): xp += char
    try:
        xp = int(xp)
        return int(xp)
    except: return 0

#*Testet ob ich gerade in der Lobby bin
def inLobby():
    inLobby = pyautogui.locateOnScreen("Images/ReadyButton.png", grayscale=True, confidence=0.9)
    if inLobby: return True
    else: return False

#*Drückt auf bereit
def pressReady():
    readyButton = pyautogui.locateOnScreen("Images/ReadyButton.png", grayscale=True, confidence=0.9)
    if readyButton == None: return
    pyautogui.click(readyButton[0],readyButton[1])
    pyautogui.click(5,5)

#!Game-Functions
#^Schuss-Functions
def pressKey(x, key):
    pyautogui.press(key, presses=x, interval=settings["bot"]["interval"])

#*Bewegt das Rohr um einen Bestimmten Winkel
def moveCannon(angle, strength, old_angle, old_strength, myPos):
    strength, old_strength = (100-strength), (100-old_strength)
    key_angle = "left"
    if angle > 90: key_angle="right"
    angle_delta = abs(angle-90)
    
    key_strength = "down"
    #Winkel-Berechnung
    delta_OldAngle = old_angle - angle
    delta_90Angle = 90 - angle

    #Stärke-Berechnung
    delta_OldStrengh = old_strength - strength
    delta_100Strengh = 100 - strength

    #Zusammen
    maximum = max(abs(delta_OldAngle), abs(delta_90Angle), abs(delta_OldStrengh), abs(delta_100Strengh))
    if maximum == abs(delta_OldAngle) or maximum == abs(delta_OldStrengh):
        print("Ich setze meinen Winkel zurück")
        myPos = getMyExcaktCoordinates(myPos)
        print(f"Mein Winkel wurde zurückgesetzt! Ich habe nun genaue Koordinaten von {myPos}")
        resetAngle(myPos)
        strength, old_strength = (100-strength), (100-old_strength)
    else:
        print("Ich bleibe auf meinem Winkel und passse ihn an")
        if delta_OldAngle >= 0:
            key_angle = "left"
            angle_delta = old_angle - angle
        else:
            key_angle = "right"
            angle_delta = angle - old_angle

        if delta_OldStrengh >= 0:
            key_strength = "down"
            strength = old_strength - strength
        else:
            key_strength = "up"
            strength = strength - old_strength

    #Schuss-Ausrichtung
    threads = []
    t = Thread(target=pressKey, args=(angle_delta, key_angle))
    threads.append(t)

    t = Thread(target=pressKey, args=(strength, key_strength))
    threads.append(t)

    for t in threads: t.start()
    for t in threads: t.join()

#*Gibt mir meine aktuell ausgewählte Waffe wieder und zudem die Kategorie mit Pytesseract
def getSelectedWeaponImageRead():
    cap = makeScreenFromWeapons()
    wep_str =  pytesseract.image_to_string(cv2.cvtColor(numpy.array(cap), cv2.COLOR_BGR2GRAY))
    wep_str = wep_str.lower().strip()
    highest_ratio = 0
    current_wep = wep_str
    category = "normal"

    for wep_cat in WEPS:
        for wep in WEPS[wep_cat]:
            if type(wep) is tuple: wep = wep[0]
            r = difflib.SequenceMatcher(None, wep_str, wep.lower()).ratio()
            if r > highest_ratio:
                highest_ratio = r
                current_wep = wep
                category = wep_cat

    return current_wep, category

#*Gibt mir meine aktuell ausgewählte Waffe wieder und zudem die Kategorie mit KNearestNeigbours
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

#*gibt mir den Besten Schusswinkel wieder KATEGORIE: normal
def getBestAngleNORMAL(wind,myPos,enemyPos):
    distance = abs(enemyPos[0] - myPos[0])
    heightDistance = enemyPos[1] - myPos[1]

    distance = abs(distance)
    distance += 0.1*heightDistance

    angleDif = 0
    angleDif = math.ceil(distance/RADIUS*4)
    distance = abs(distance - angleDif * RADIUS/4)

    if myPos[0] >= enemyPos[0]: angleDif *= -1

    windDif = abs(round(wind/14))
    if myPos[0] >= enemyPos[0] and wind >= 0: windDif *= -1
    elif myPos[0] <= enemyPos[0] and wind >= 0: windDif *= -1

    strenghDif = round(distance/15)

    print(f"Ich berechnen für diesen Schuss folgende Daten:\n{angleDif=} {windDif=} {strenghDif=}")
    return (90 + angleDif + windDif), strenghDif

#*gibt mir den Besten Schusswinkel wieder KATEGORIE: straight
def getBestAngleSTRAIGHT(myPos, enemyPos):
    m = (myPos[1]-enemyPos[1])/(myPos[0]-enemyPos[0])
    angle = math.degrees(math.atan(m))
    if myPos[0] < enemyPos[0]: angle += 180
    return round(angle), 0

#*gibt mir den Besten Schusswinkel wieder KATEGORIE: 45degrees
def getBestAngle45DEGREES(wind, myPos, enemyPos):
    distance = enemyPos[0] - myPos[0]
    heightDistance = enemyPos[1] - myPos[1]
    angle = 0
    strengh = 0

    if distance < 0: angle = 45
    else: angle = 135

    distance = abs(distance)
    distance -= 0.75*heightDistance

    windAngleDelta = 0.115*abs(wind)/100
    if myPos[0] >= enemyPos[0] and wind <= 0: windAngleDelta *= -1
    elif myPos[0] <= enemyPos[0] and wind >= 0: windAngleDelta *= -1

    radia = distance/RADIUS
    strengh = 35 * math.sqrt(abs(radia))
    strengh = round(strengh + (strengh * windAngleDelta))
    return angle, (100-strengh)

#*gibt mir den Besten Schusswinkel wieder KATEGORIE: deltaAngle
def getBestAngleDELTAANGLE(wind,myPos,enemyPos, weapon):
    angle, _ = getBestAngleNORMAL(wind,myPos,enemyPos)
    
    delta = 0
    for w in WEPS["deltaAngle"]:
        if w[0] == weapon:
            delta = w[1]
            break
        
    if myPos[0] >= enemyPos[0]: angle += -1*delta
    else: angle += delta
    return angle, 0

def getBestAngleRADIUS(myPos, enemyPos, weapon):
    angle, _ = getBestAngleSTRAIGHT(myPos, enemyPos)
    distance = enemyPos[0] - myPos[0]
    radia = abs(distance/RADIUS)

    delta = 0
    for w in WEPS["radius"]:
        if w[0] == weapon:
            delta = w[1]
            break

    strengh = min(round(radia * delta),100)
    return angle, 100-strengh

#*Drückt auf Shoot
def shoot():
    pyautogui.click(1200, 1000)
    pyautogui.click(5, 5)

#^Movement-Functions
#*Bewege mich für t-Sekunden
def move(key, t):
    pyautogui.keyDown(key)
    time.sleep(t)
    pyautogui.keyUp(key)

#*Bewege mich in einen vorgebenen Bereich, jenachdem ob ich links oder rechts stehe.
def makeMove(myPos, enemyPos, weapon_cat):
    tolerance = 25

    myPosX = myPos[0]
    myPosY = GAME_FIELD[3] - myPos[1]
    enPosX = enemyPos[0]
    enPosY = GAME_FIELD[3] - enemyPos[1]

    whichBox = 1
    if myPosX > enPosX: whichBox = 2

    heights = []
    if whichBox == 1: heights = getTerrainHeights(TANK1BOX[0],TANK1BOX[1])
    else: heights = getTerrainHeights(TANK2BOX[0],TANK2BOX[1])

    maxHeight = [0, float("-inf")]
    for d in heights:
        if d[1] > maxHeight[1]: maxHeight = d
    
    print(f"{maxHeight=}")
    if myPosX <= maxHeight[0] + tolerance and myPosX >= maxHeight[0] - tolerance: return False, weapon_cat
    key = ""
    time = min(abs(maxHeight[0]-myPosX)/120,4)
    if myPosX < maxHeight[0]: key = "d"
    else: key = "a"

    move(key, time)
    return True, weapon_cat

#^Overview-Functions
#*Gibt die Koordinaten eines Gegners wieder und von mir
def getAverageCoordinatesBrute(capColor, everyPixel=2, tolerance=0.05):
    s = s = ImageGrab.grab(bbox = (GAME_FIELD[0],GAME_FIELD[1],GAME_FIELD[2],GAME_FIELD[3]))

    allds = []
    allcords = []

    for x in range(0,s.width,everyPixel):
        for y in range(0,s.height,everyPixel):
            color = s.getpixel((x, y))
            d = math.sqrt((color[0]-capColor[0])**2+(color[1]-capColor[1])**2+(color[2]-capColor[2])**2)
            allds.append(d)
            allcords.append([x,y])
    min_d = min(allds)*(1-tolerance)
    max_d = min(allds)*(1+tolerance)

    anzahl = 0
    average_x, average_y = 0,0
    for x in range(len(allds)):
        if allds[x] >= min_d and allds[x] <= max_d:
            average_x += allcords[x][0]
            average_y += allcords[x][1]
            anzahl += 1

    if anzahl == 0: anzahl = 1

    average_x = average_x/anzahl
    average_y = average_y/anzahl

    return [int(average_x), int(average_y), min(allds)]

def getAverageCoordinatesBreadth(capColor, lastX, lastY, everyPixel=2):
    s = ImageGrab.grab(bbox = (GAME_FIELD[0],GAME_FIELD[1],GAME_FIELD[2],GAME_FIELD[3]))
    q = queue.Queue()
    visited = numpy.zeros((GAME_FIELD[2],GAME_FIELD[3]), dtype=bool)

    q.put([lastX, lastY])
    visited[lastX][lastY] = True
    minD = [0,0,float("inf")]

    while not q.empty():
        field = q.get()
        color = s.getpixel((field[0], field[1]))
        d = math.sqrt((color[0]-capColor[0])**2+(color[1]-capColor[1])**2+(color[2]-capColor[2])**2)
        if d < minD[2]: minD = [field[0], field[1], d]

        if d < 15: return minD

        if field[0] + everyPixel < GAME_FIELD[2] and not visited[field[0] + everyPixel][field[1]]:
            q.put([field[0] + everyPixel, field[1]])
            visited[field[0] + everyPixel][field[1]] = True
        if field[0] - everyPixel > GAME_FIELD[0] and not visited[field[0] - everyPixel][field[1]]:
            q.put([field[0] - everyPixel, field[1]])
            visited[field[0] - everyPixel][field[1]] = True
        if field[1] + everyPixel < GAME_FIELD[3] and not visited[field[0]][field[1] + everyPixel]:
            q.put([field[0], field[1] + everyPixel])
            visited[field[0]][field[1] + everyPixel] = True
        if field[1] - everyPixel > GAME_FIELD[1] and not visited[field[0]][field[1] - everyPixel]:
            q.put([field[0], field[1] - everyPixel])
            visited[field[0]][field[1] - everyPixel] = True

    return minD

#*Gibt mir auf den Pixel genau die Koordinaten meines Panzers wieder
def getMyExcaktCoordinates(myPos):
    pyautogui.click(myPos[0], min(myPos[1]+250, 880))
    time.sleep(0.1)
    
    height = SHOOTLINE_FIELD[3]
    if max(myPos[1]+SHOOTLINE_FIELD[1],0) == 0:
        height = abs(SHOOTLINE_FIELD[1])-myPos[1]
    cap = pyautogui.screenshot(region=(myPos[0]+SHOOTLINE_FIELD[0], max(myPos[1]+SHOOTLINE_FIELD[1],0), SHOOTLINE_FIELD[2]*2, height))

    enhancer = ImageEnhance.Sharpness(cap)
    cap = enhancer.enhance(1000)
    enhancer = ImageEnhance.Contrast(cap)
    cap = enhancer.enhance(10)

    firstaxs = []
    for x in range(0,cap.width):
        for y in range(0,cap.height):
            color = cap.getpixel((x, y))
            if color == (255,255,255): firstaxs.append(x)
            else: cap.putpixel((x,y),(0,0,0))

    allxs = []
    for x in firstaxs:
        if x not in allxs: allxs.append(x)

    cap = cap.crop((0,2,cap.width,cap.height-2))
    highest_row = 0
    highest_count = 0
    for x in allxs:
        count = 0
        for y in range(cap.height):
            color = cap.getpixel((x, y))
            if color == (255,255,255): count += 1
        if count == cap.height:
            for y in range(cap.height):
                color = cap.getpixel((x+1, y))
                if color == (255,255,255): count += 1
        if count > highest_count:
            highest_row = x
            highest_count = count

    myPos[0] = myPos[0]+SHOOTLINE_FIELD[0]+highest_row
    return myPos

#*Gibt mir die Koordinaten aus der alten Runde wieder. Ist der Panzer immernoch in dieser Box -> True | Nein -> False
def isTankInSameBox(x,y,tankColor):
    box_size = 50
    s = pyautogui.screenshot(region=(max(x-box_size,0),max(y-box_size,0),box_size*2, box_size*2))

    smallestD = float("inf")
    for x in range(0,s.width,2):
        for y in range(0,s.height,2):
            color = s.getpixel((x, y))
            d = math.sqrt((color[0]-tankColor[0])**2+(color[1]-tankColor[1])**2+(color[2]-tankColor[2])**2)
            if d < smallestD: smallestD = d

    if smallestD <= 6: return True
    return False
    
#*Wenn ich dran bin gibt dieser True zurück
def myTurn():
    myTurn = pyautogui.locateOnScreen("Images/FireButton.png", confidence=0.9)
    if myTurn == None: return False
    else: return True

#*Gibt wenn ich im Loading Screen bin True zurück
def loadingScreen():
    FireButton = pyautogui.locateOnScreen("Images/FireButton.png", confidence=0.9)
    NotFireButton = pyautogui.locateOnScreen("Images/NotFireButton.png", confidence=0.9)
    ReadyButton = pyautogui.locateOnScreen("Images/ReadyButton.png", confidence=0.9)
    LockedInButton = pyautogui.locateOnScreen("Images/LockedInButton.png", confidence=0.9)
    if not FireButton and not NotFireButton and not ReadyButton and not LockedInButton: return True
    return False

#*Guckt überall auf der Map wo ein Gear sein könnte
def gearLoop(debug=False):
    global INLOBBY
    global SHOOTING
    while True:
        if (INLOBBY == True or SHOOTING == True) or debug:
            time.sleep(2)
            continue
        cords = getAverageCoordinatesBrute(Gear, everyPixel=5, tolerance=0.001)
        if cords[2] <= 15:
            print("Gear detected")
            pyautogui.moveTo(cords[0], cords[1])

#*Setzt meinen Schussradius auf 100,90 (probiert es zumindest LOL)
def resetAngle(myPos):
    myPos = getMyExcaktCoordinates(myPos)
    pyautogui.click(myPos[0], max(myPos[1]-300, 0))

    if myPos[1] <= 300: pressKey(60, "up")
    else: pressKey(20, "up")

def getWindRichtung():
    richtung = "Rechts"
    for CORDS in (WIND_FIELD_LEFT, WIND_FIELD_RIGHT):
        cap = ImageGrab.grab(bbox = (CORDS[0],CORDS[1],CORDS[2],CORDS[3]))
        filter = ImageEnhance.Color(cap)
        cap = filter.enhance(0)
        enhancer = ImageEnhance.Contrast(cap)
        cap = enhancer.enhance(100)
        if cap.getpixel((int(cap.width/2),int(cap.height/2))) == (255,255,255):
            if CORDS == WIND_FIELD_RIGHT: richtung = "Rechts"
            else: richtung = "Links"
    return richtung

#*Gibt mir den Wind zurück
def getWindImageRead():
    answers=[]
    cap = ImageGrab.grab(bbox = (WIND_FIELD[0],WIND_FIELD[1],WIND_FIELD[2],WIND_FIELD[3]))

    for x in [Image.LANCZOS, Image.BILINEAR, Image.BICUBIC, Image.BOX, Image.HAMMING, Image.NEAREST]:
        new_cap = cap.resize((cap.width*20,cap.height*20), resample=x)
        filter = ImageEnhance.Color(new_cap)
        new_cap = filter.enhance(0)
        enhancer = ImageEnhance.Contrast(new_cap)
        new_cap = enhancer.enhance(100)
        text =  str(pytesseract.image_to_string(cv2.cvtColor(numpy.array(new_cap), cv2.COLOR_BGR2GRAY),config="--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789")).strip()
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

    return int(highest_num[0]), getWindRichtung()

def getWindNeighbors():
    cap = makeScreenFromWind()
    arr, ones = convertTo1DArray(cap)
    new_point = arr
    wep_str = knn.multiThreadfindCategory(new_point, WINDPIXELS, 8, ones, fixedK=1)
    return int(wep_str), getWindRichtung()

#^Terrain-Functions
def getGroundHeight(x, mid, cap):
    color = cap.getpixel((x, mid))
    if color[0] >= 233 and color[1] >= 233 and color[2] >= 233: 
        while not (color[0] <= 233 and color[1] <= 233 and color[2] <= 233) and mid > GAME_FIELD[1]:
            mid -= 1
            color = cap.getpixel((x, mid))
        return mid
    else:
        while not (color[0] >= 233 and color[1] >= 233 and color[2] >= 233) and mid < GAME_FIELD[3]:
            mid += 1
            color = cap.getpixel((x, mid))
        return mid

def getTerrainHeights(left_bound, right_bound):
    cap = makeScreenFromGame()

    #Reine Erkennen der Rohdaten
    data = []
    lastY = getGroundHeight(left_bound, int(GAME_FIELD[3]/2), cap)
    data.append([left_bound,lastY])
    for x in range(left_bound+1, right_bound+1):
        newY = getGroundHeight(x, lastY, cap)
        data.append([x,GAME_FIELD[3]-newY])
        lastY = newY

    #Smoothen
    difThreshold = 100
    i = 0
    while i < len(data)-1:
        dif = abs(data[i][1]-data[i+1][1])
        if dif >= difThreshold:
            data.pop(i)
            data.pop(min(i+1,len(data)-1))
            i = 0
        i += 1

    return data

#^Play-Loop
#*Dieser Loop wird solange ausgeführt, wie der Spiel sich im Spiel befindet
def play(waitTime=3, debug=False):
    global INLOBBY
    global SHOOTING

    while inLobby(): time.sleep(0.2)
    if not debug: time.sleep(waitTime)

    INLOBBY = False

    myPos = getAverageCoordinatesBreadth(MyTank, int(GAME_FIELD[2]/2),int(GAME_FIELD[3]/2), everyPixel=4)
    enemyPos = getAverageCoordinatesBreadth(EnemyTank, int(GAME_FIELD[2]/2),int(GAME_FIELD[3]/2), everyPixel=4)
    round = 1
    old_shoot_data = [90,0]
    print(f"Meine Position: {myPos}\nGegner Position: {enemyPos}")
    
    while True:
        while myTurn() == False:
            time.sleep(0.2)
            if loadingScreen(): pyautogui.click(1013, 1050)
            if inLobby(): return
        print(f"Ich bin nun dran! Wir befinden uns in Runde {round}")
        SHOOTING = True
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print("date and time =", dt_string)	

        #Kriege Waffen Daten
        wep_data = ["shot","normal"]
        if WEAPONPIXELS_ACTIVE:
            print("Benutze gute Waffen-auslesung")
            wep_data = getSelectedWeaponNeighbors()
        else:
            print("Benutze schlechte Waffen-auslesung")
            wep_data = getSelectedWeaponImageRead()
        
        weapon = wep_data[0]
        weapon_cat = wep_data[1]
        shoot_data = [90,0]

        if weapon_cat != "instant":
            #Kriege Koordinaten
            if isTankInSameBox(myPos[0], myPos[1], MyTank) == False:
                print("Die Kalkulation hat ergeben ... Ich habe mich bewegt!")
                myPos = getAverageCoordinatesBreadth(MyTank, myPos[0], myPos[1], everyPixel=4)
            else:
                print("Die Kalkulation hat ergeben ... Ich bin stehen geblieben!")
            if isTankInSameBox(enemyPos[0], enemyPos[1], EnemyTank) == False:
                print("Die Kalkulation hat ergeben ... Der Gegner hat sich bewegt!")
                enemyPos = getAverageCoordinatesBreadth(EnemyTank, enemyPos[0], enemyPos[1], everyPixel=4)
            else: 
                print("Die Kalkulation hat ergeben ... Der Gegner ist stehen geblieben")

            #Bewegung
            moveMe, weapon_cat = makeMove(myPos, enemyPos, weapon_cat)
            if moveMe:
                print("Ich habe mich bewegt ... Ich berechne meine Position neu!")
                myPos = getAverageCoordinatesBreadth(MyTank, myPos[0], myPos[1], everyPixel=4)
            print(f"Meine PosgetAverageCoordinatesBreadthition: {myPos}\nGegner Position: {enemyPos}")

            #Schuss-Kalkulation
            wind = 0
            if WEAPONPIXELS_ACTIVE:
                print("Benutze gute Wind-auslesung")
                wind = getWindNeighbors()
            else:
                print("Benutze schlechte Wind-auslesung")
                wind = getWindImageRead()

            print(f"{weapon} wurde geschossen")

            delta_x = myPos[0] - enemyPos[0]
            calc_wind = wind[0]
            if delta_x >= 0: delta_x *= -1
            if wind[1] == "Links": calc_wind = wind[0] * -1

            #& Shoot-Categories
            if weapon_cat == "normal": shoot_data = getBestAngleNORMAL(calc_wind ,myPos,enemyPos)
            elif weapon_cat == "straight": shoot_data = getBestAngleSTRAIGHT(myPos, enemyPos)
            elif weapon_cat == "45degrees": shoot_data = getBestAngle45DEGREES(calc_wind, myPos, enemyPos)
            elif weapon_cat == "deltaAngle": shoot_data = getBestAngleDELTAANGLE(calc_wind, myPos, enemyPos, weapon)
            elif weapon_cat == "radius": shoot_data = getBestAngleRADIUS(myPos, enemyPos, weapon)
            elif weapon_cat == "landing": shoot_data = getBestAngle45DEGREES(calc_wind, myPos, enemyPos)

            else: shoot_data = getBestAngleNORMAL(calc_wind ,myPos,enemyPos)

        print(f"Wind-Daten {wind=}")
        print(f"Waffen-Daten {weapon=} {weapon_cat=}")
        moveCannon(shoot_data[0], shoot_data[1], old_shoot_data[0], old_shoot_data[1], myPos)
        old_shoot_data[0], old_shoot_data[1] = shoot_data[0], shoot_data[1]
        SHOOTING = False
        shoot()
        print("Meinen Turn beendet")
        round += 1
        time.sleep(3)

#*Dieser Loop ist die Brücke zwischen Lobby und Spiel
def main(debug=False):
    global INLOBBY
    #Regeln einmal printen
    print(RULES)

    #ErsterStart
    if inLobby() == False and not debug:
        print("Starte von der Lobby aus!")
        return

    t = Thread(target=loadWeaponPixels)
    t.start()
    t = Thread(target=loadWindPixels)
    t.start()
    t = Thread(target=gearLoop)
    t.start()


    first_xp = getXP()
    print(f"Deine aktuelle XP-Anzahl beträgt: {first_xp}")

    #Die Unendliche Schleife
    while True:
        try:
            pressReady()
            while inLobby() and not debug:
                time.sleep(1)
            play(debug=debug)
            INLOBBY = True
            nowXP = getXP()
            print(f"Deine aktuelle XP-Anzahl beträgt: {nowXP}\nSomit hast du {nowXP-first_xp} XP bisher gemacht!")

        except Exception as e:
            time.sleep(3)
            print(e)
            shoot()

if __name__ == "__main__":
    wait = 3
    for x in range(wait):
        print(f"starting in {wait-x}...")
        time.sleep(1)

    main(debug=settings["bot"]["debug"])