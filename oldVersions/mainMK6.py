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
from PIL import Image, ImageEnhance, ImageGrab
from datetime import datetime
from threading import Thread

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
RADIUS = 320
WEAPONPIXELS = []
WEAPONPIXELS_ACTIVE = False
WINDPIXELS = []
WINDPIXELS_ACTIVE = False


#Koordinaten
READY_BUTTON = [1177,952,1608,986]
XP_FIELD = [312,120,440,150]
WIND_FIELD = [946,77,973,95]
WIND_FIELD_RIGHT = [985,74,1000,93]
WIND_FIELD_LEFT = [919,74,934,93]
WEAPON_FIELD = [713,1038,950,1064]
SHOOTLINE_FIELD = [-30,-300,30,20]

#FARBEN
MyTank = (0, 220, 15)
EnemyTank = (194,3,3)

#Waffen
WEPS = {"normal": ["shot", "big shot", "heavy shot", "massive shot", "one-bounce", "three-bounce",
                    "five-bounce", "seven-bounce", "digger", "mega-digger", "grenade", "tri-nade",
                    "multi-nade", "grenade storm", "splitter", "double-splitter", "super-splitter",
                    "breaker", "double-breaker", "super-breaker", "breakerchain", "twinkler", "sparkler",
                    "crackler", "sniper", "sub-sniper", "smart snipe", "cactus", "cactus strike",
                    "bulger", "big bulger", "sinkhole", "area strike", "area attack", "gatling gun",
                    "tunneler", "torpedoes", "tunnel strike", "megatunneler", "horizon", "sweeper",
                    "air strike", "helicopter strike", "ac-130", "artillery", "flower", "bouquet",
                    "banana", "banana split", "banana bunch", "snake", "python", "cobra", "zipper",
                    "double zipper", "zipper quad", "bounsplode", "double-bounsplode", 
                    "dead riser", "pixel", "mega-pixel", "super-pixel", "ultra-pixel",
                    "builder", "megabuilder", "static", "static link", "static chain", "molehill", "moles",
                    "rainbow",
                    "megarainbow", "mini-pinger", "pinger", "ping flood", "bolt", "lightning", "2012",
                    "spiker", "super spiker", "disco ball", "groovy ball", "boomerang", "bigboomerang",
                    "mini-v", "flying-v", "yin yang", "yin yang yong", "fireworks", "grand finale",
                    "pyrotechnics", "water balloon", "magnets", "arrow", "bow & arrow", "flaming arrow",
                    "driller", "slammer", "quicksand", "desert", "jumper", "triple-jumper", "spaz",
                    "spazzer", "spaztastic", "pinata", "bounder", "double bounder", "triple bounder",
                    "sticky bomb", "mine layer", "sticky rain", "rain", "hail", "napalm", "heavy napalm",
                    "firestorm", "sunburst", "solar flare",
                    "payload", "magic shower", "shadow", "darkshadow", "deathshadow", "carpet bomb",
                    "carpet fire", "incendiary bombs", "baby seagull", "seagull", "mama seagull",
                    "shrapnel", "shredders", "penetrator", "penetrator v2",
                    "chunklet", "chunker", "bouncy ball", "super ball", "battering ram", "double ram",
                    "ram-squad", "double ram-squad", "asteroids", "spider", "tarantula", "daddy longlegs",
                    "black widow", "clover", "four leaf clover", "3d-bomb", "2x3d", "3x3d", "snowball",
                    "snowstorm", "spotter", "spotter xl", "spotter xxl", "fighter jet", "heavy jet",
                    "bounstrike", "bounstream", "bounstorm", "shooting star", "bee hive", "killer bees",
                    "wasps", "dual-roller", "spreader", "partition", "division", "bfg-1000", "bfg-9000",
                    "train", "express", "mini-turret", "kamikaze", "suicide bomber", "nuke", "meganuke",
                    "black hole", "cosmic rift", "breakermadness", "breakermania", "homing missile",
                    "homing rockets", "puzzler", "deceiver", "baffler", "pentagram", "pentaslam", "radar",
                    "sonar", "lidar", "tweeter", "squawker", "woofer", "acid rain", "acid hail", "sunflower",
                    "helianthus", "sausage", "bratwurst", "kielbasa", "recruiter", "enroller",
                    "enlister", "fury", "rage", "relocator", "displacement bomb", "stone", "boulder", "fireball",
                    "cat", "supercat", "cats and dogs", "asteroid storm",
                    "ghost bomb", "flasher", "strobie", "rave", "sprouter", "blossom", "square", "hexagon",
                    "octagon", "satellite", "ufo", "palm", "double palm", "triple palm", "fountain", 
                    "waterworks", "sprinkler", "flattener", "wall", "fortress", "funnel", "mad birds",
                    "furious birds", "livid birds", "beacon", "beaconator", "chopper", "apache", "skullshot",
                    "skeleton", "pinpoint", "needles", "pins and needles", "god rays", "deity", "hidden blade",
                    "secret blade", "concealed blade", "portal gun", "ashpd", "volcano", "eruption", "throwing star",
                    "multi-star", "ninja", "tangent fire", "tangent attack", "tangent assault", "summoner", "mage",
                    "travelers", "scavengers", "jack-o-lantern", "jack-o-vomit", "wicked witch", "witches broom",
                    "ghouls", "oddball", "oddbomb", "botherer", "tormentor", "punisher"],
        
        "straight": ["glock","m9","desert eagle","moons","orbitals","shank","dagger","sword","uzi","mp5","p90",
                    "rampage","riot","m4","m16","ak-47", "laser beam","great beam","ultra beam","master beam",
                    "early bird","early worm","shockshell","shockshell trio","flintlock","blunderbuss",
                    "fat stacks", "dolla bills", "make-it-rain"],

        "instant": ["earthquake","mega-quake","shockwave","sonic pulse","drone","heavy drone","attractoids",
                    "imploder", "ultimate imploder"],

        "45degrees": ["three-ball", "five-ball", "eleven-ball", "twentyfive-ball", "stream", "creek", "river",
                    "tsunami", "flame", "blaze", "inferno", "splitterchain", "rapidfire", "shotgun", "burst-fire",
                    "gattling gun", "guppies", "minnows", "goldfish", "construction", "excavation", "counter 3000",
                    "counter 4000", "counter 5000", "counter 6000", "gravies", "gravits", "tadpoles", "frogs",
                    "bullfrog", "water trio", "water fight", "fiesta", "sticky trio", "fleet", "heavy fleet",
                    "super fleet", "squadron", "sillyballs", "wackyballs", "crazyballs", "synclets", "super-synclets",
                    "x attack", "o attack", "minions", "many-minions", "asteorids", "comets",
                    "starfire", "turretmob", "bumper bombs", "bumper array", "bumper assault", "rocket fire",
                    "rocket cluster", "flurry", "taser", "jackpot", "mega-jackpot", "ultra-jackpot", "lottery",
                    "kittens", "ghostlets", "wacky cluster", "kooky cluster", "crazy cluster", "chicken-fling",
                    "chicken-hurl", "chicken-launch", "pepper", "salt and pepper", "paprika", "cayenne", "needler",
                    "dual needler", "kernels", "popcorn", "burnt popcorn", "skeet", "olympic skeet", "heavy taser",
                    "jammer", "jiver", "rocker", "triple-bounsplode"],

        "deltaAngle": [("roller",-1), ("heavy roller",-1), ("groller",-1), ("back-roller",1),
                    ("heavy back-roller",1), ("back-groller",1), ("saw blade",-2), ("rip saw",-2), ("diamond blade",-2),
                    ("dead weight",2), ("permaroller",-3), ("heavy permaroller",-4), ("ringer",-1), ("heavy ringer",-2),
                    ("olympic ringer",-2), ("hover-ball",-3), ("heavy hover-ball",-3),]
        }

#Sonstiges
settings = json.load(open("settings.json"))
file_executed_in = os.getcwd()

tesseract = None
if settings["tesseract"] != "local": tesseract = settings["tesseract"]
else: tesseract = f"{file_executed_in}\Tesseract-OCR\\tesseract.exe"

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
        print(f"WAFFEN | {count} von {len(Lines)} geladen")

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
        print(f"WIND | {count} von {len(Lines)} geladen")

    WINDPIXELS_ACTIVE = True
    print("----------------------------------------------------------------")
    print("Trainings-Daten wurden geladen, schalte nun auf bessere Winderkennung um.")
    print("----------------------------------------------------------------")

#*Mache einen Screenshot von der Waffe
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
#*Gibt die Schussweite in Pixel wieder
def calculateDestiny(angle):
    Delta_Angle = (angle-90)*87
    return Delta_Angle

def pressKey(x, key):
    for _ in range(x):
        pyautogui.press(key)

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
def getBestAngleNORMAL(wind,myX,eX):
    delta = eX-myX
    bestangle = 0
    bestDeltaDif = float("inf")
    DeltaDif = 0
    for a in range(50,131):
        calcAngle = calculateDestiny(a)
        if abs(calcAngle - delta) < bestDeltaDif:
            bestangle = a
            bestDeltaDif = abs(calcAngle - delta)
            DeltaDif = calcAngle - delta
    WindAngleDelta = abs(round(wind/14))
    if myX >= eX and wind >= 0: WindAngleDelta *= -1
    elif myX <= eX and wind >= 0: WindAngleDelta *= -1

    print(f"Ich berechnen für diesen Schuss folgende Daten:\n{delta=} {bestangle=} {bestDeltaDif=} {WindAngleDelta=} {wind=}")
    return (bestangle + WindAngleDelta), 0

#*gibt mir den Besten Schusswinkel wieder KATEGORIE: straight
def getBestAngleSTRAIGHT(myPos, enemyPos):
    m = (myPos[1]-enemyPos[1])/(myPos[0]-enemyPos[0])
    angle = math.degrees(math.atan(m))
    if myPos[0] < enemyPos[0]: angle += 180
    print(round(angle))
    return round(angle), 0

#*gibt mir den Besten Schusswinkel wieder KATEGORIE: 45degrees
def getBestAngle45DEGREES(wind, myPos, enemyPos):
    distance = enemyPos[0] - myPos[0]
    angle = 0
    strengh = 0

    if distance < 0: angle = 45
    else: angle = 135

    windAngleDelta = round(wind/35)
    if myPos[0] >= enemyPos[0] and wind >= 0: windAngleDelta *= -1
    elif myPos[0] <= enemyPos[0] and wind >= 0: windAngleDelta *= -1

    radia = distance/RADIUS
    strengh = round(35 * math.sqrt(abs(radia)))
    return angle, (100-strengh + windAngleDelta)

#*gibt mir den Besten Schusswinkel wieder KATEGORIE: deltaAngle
def getBestAngleDELTAANGLE(wind,myX,eX, weapon):
    angle, _ = getBestAngleNORMAL(wind,myX,eX)
    
    delta = 0
    for w in WEPS["deltaAngle"]:
        if w[0] == weapon:
            delta = w[1]
            break
        
    if myX >= eX: angle += -1*delta
    else: angle += delta
    print(angle)
    return angle, 0

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
def moveMeToCenter(myPos, enemyPos):
    box1 = [480,720]
    box2 = [1200,1440]
    whichBox = 1
    key = ""
    if myPos[0] > enemyPos[0]: whichBox = 2
    if whichBox == 1:
        if myPos[0] >= box1[0] and myPos[0] <= box1[1]: return False
        else:
            if myPos[0] >= box1[1]: key = "a"
            else: key = "d"
    else:
        if myPos[0] >= box2[0] and myPos[0] <= box2[1]: return False
        else:
            if myPos[0] >= box2[1]: key = "a"
            else: key = "d"

    waitTime = 1.5
    move(key, waitTime)
    return True
    
#^Overview-Functions
#*Gibt die Koordinaten eines Gegners wieder und von mir
def getAverageTankCoordinates(tankColor):
    s = pyautogui.screenshot(region=(0,0,1920,927))
    pyautogui.FAILSAFE = False

    allds = []
    allcords = []
    tolerance=0.05

    for x in range(0,s.width,2):
        for y in range(0,s.height,2):
            color = s.getpixel((x, y))
            d = math.sqrt((color[0]-tankColor[0])**2+(color[1]-tankColor[1])**2+(color[2]-tankColor[2])**2)
            allds.append(d)
            allcords.append([x,y])
    min_d = min(allds)*(1-tolerance)
    max_d = min(allds)*(1+tolerance)

    newcords = []
    all_xs = []
    all_ys = []

    for x in range(len(allds)):
        if allds[x] >= min_d and allds[x] <= max_d:
            newcords.append(allcords[x])
            all_xs.append(allcords[x][0])
            all_ys.append(allcords[x][1])
    average_x, average_y = 0,0
    for x in newcords:
        average_x += x[0]
        average_y += x[1]
    average_x = average_x/len(newcords)
    average_y = average_y/len(newcords)

    return [int(average_x), int(average_y)]

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

    allds = []

    for x in range(0,s.width,2):
        for y in range(0,s.height,2):
            color = s.getpixel((x, y))
            d = math.sqrt((color[0]-tankColor[0])**2+(color[1]-tankColor[1])**2+(color[2]-tankColor[2])**2)
            allds.append(d)

    if min(allds) <= 5: return True
    return False
    
#*Wenn ich dran bin gibt dieser True zurück
def myTurn():
    myTurn = pyautogui.locateOnScreen("Images/FireButton.png", confidence=0.9)
    if myTurn == None: return False
    else: return True

#*Setzt meinen Schussradius auf 100,90 (probiert es zumindest LOL)
def resetAngle(myPos):
    myPos = getMyExcaktCoordinates(myPos)
    pyautogui.click(myPos[0], max(myPos[1]-300, 0))

    if myPos[1] <= 300:
        for x in range(40):
            pyautogui.press("up")
    else:
        for x in range(20):
            pyautogui.press("up")

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


#^Play-Loop
#*Dieser Loop wird solange ausgeführt, wie der Spiel sich im Spiel befindet
def play(waitTime=10, debug=False):
    while inLobby(): time.sleep(0.2)
    if not debug: time.sleep(waitTime)

    myPos = getAverageTankCoordinates(MyTank)
    enemyPos = getAverageTankCoordinates(EnemyTank)
    round = 1
    old_shoot_data = [90,0]
    print(f"Meine Position: {myPos}\nGegner Position: {enemyPos}")
    
    while True:
        while myTurn() == False:
            time.sleep(0.5)
            if inLobby(): return
        print(f"Ich bin nun dran! Wir befinden uns in Runde {round}")

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
                myPos = getAverageTankCoordinates(MyTank)
            else:
                print("Die Kalkulation hat ergeben ... Ich bin stehen geblieben!")
            if isTankInSameBox(enemyPos[0], enemyPos[1], EnemyTank) == False:
                print("Die Kalkulation hat ergeben ... Der Gegner hat sich bewegt!")
                enemyPos = getAverageTankCoordinates(EnemyTank)
            else: 
                print("Die Kalkulation hat ergeben ... Der Gegner ist stehen geblieben")

            #Bewegung
            if moveMeToCenter(myPos, enemyPos):
                print("Ich habe mich bewegt ... Ich berechne meine Position neu!")
                myPos = getAverageTankCoordinates(MyTank)
            print(f"Meine Position: {myPos}\nGegner Position: {enemyPos}")

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
            if weapon_cat == "normal": shoot_data = getBestAngleNORMAL(calc_wind ,myPos[0],enemyPos[0])
            elif weapon_cat == "straight": shoot_data = getBestAngleSTRAIGHT(myPos, enemyPos)
            elif weapon_cat == "45degrees": shoot_data = getBestAngle45DEGREES(calc_wind, myPos, enemyPos)
            elif weapon_cat == "deltaAngle": shoot_data = getBestAngleDELTAANGLE(calc_wind, myPos[0], enemyPos[0], weapon)
            

        print(f"Wind-Daten {wind=}")
        print(f"Waffen-Daten {weapon=} {weapon_cat=}")
        moveCannon(shoot_data[0], shoot_data[1], old_shoot_data[0], old_shoot_data[1], myPos)
        old_shoot_data[0], old_shoot_data[1] = shoot_data[0], shoot_data[1]
        shoot()
        print("Meinen Turn beendet")
        round += 1
        time.sleep(3)

#*Dieser Loop ist die Brücke zwischen Lobby und Spiel
def main(debug=False):
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

    first_xp = getXP()
    print(f"Deine aktuelle XP-Anzahl beträgt: {first_xp}")

    #Die Unendliche Schleife
    while True:
        try:
            pressReady()
            while inLobby() and not debug: time.sleep(1)
            play(debug=debug)
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
    
    main(debug=False)