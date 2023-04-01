from PIL.ImageOps import grayscale
import pytesseract, numpy, cv2, pyautogui, math, difflib, time, json, os
from PIL import Image, ImageEnhance, ImageFilter, ImageGrab
from datetime import datetime
from threading import Thread

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
WEAPON_FIELD = [707,1031,1013,1067]
SHOOTLINE_FIELD = [-30,-300,30,20]

#Faktoren
WIND_FACTOR = 6.467

#FARBEN
MyTank = (0, 220, 15)
EnemyTank = (194,3,3)

#Waffen
WEPS_STRAIGHT = ["glock","m9","desert eagle","moons","orbitals","shank","dagger","sword","uzi","mp5","p90","rampage","riot","m4","m16","ak-47",
                "laser beam","great beam","ultra beam","master beam","early bird","early worm","shockshell","shockshell trio","flintlock","blunderbuss",]
WEPS_INSTANT = ["earthquake","mega-quake","shockwave","sonic pulse","drone","heavy drone","attractoids"]

#Sonstiges
settings = json.load(open("settings.json"))
file_executed_in = os.getcwd()

tesseract = None
if settings["tesseract"] != "local": tesseract = settings["tesseract"]
else: tesseract = f"{file_executed_in}\Tesseract-OCR\\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = tesseract
pyautogui.FAILSAFE = False

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
    pyautogui.click(readyButton[0],readyButton[1])
    pyautogui.click(5,5)

#!Game-Functions
#^Schuss-Functions
#*Gibt die Schussweite in Pixel wieder
def calculateDestiny(angle):
    Delta_Angle = (angle-90)*87
    return Delta_Angle

#*Gibt mir meine aktuell ausgewählte Waffe wieder und zudem die Kategorie
def getSelectedWeapon():
    cap = ImageGrab.grab(bbox = (WEAPON_FIELD[0],WEAPON_FIELD[1],WEAPON_FIELD[2],WEAPON_FIELD[3]))
    filter = ImageEnhance.Color(cap)
    cap = filter.enhance(50)
    enhancer = ImageEnhance.Contrast(cap)
    cap = enhancer.enhance(1)

    newCap  = Image.new( mode = "RGB", size = (cap.width, cap.height), color = (0, 0, 0) )
    for x in range(0,cap.width):
        for y in range(0,cap.height):
            color = cap.getpixel((x, y))
            if color == (255,255,255):
                newCap.putpixel((x,y),(255,255,255))

    newCap = newCap.resize((cap.width*10,cap.height*10), resample=Image.HAMMING)
    wep_str =  pytesseract.image_to_string(cv2.cvtColor(numpy.array(newCap), cv2.COLOR_BGR2GRAY), lang="eng")

    wep_str = wep_str.lower().strip()
    highest_ratio = 0
    current_wep = wep_str
    category = "normal"

    for x in WEPS_STRAIGHT:
        r = difflib.SequenceMatcher(None, wep_str, x.lower()).ratio()
        if r > highest_ratio and r > 0.8:
            highest_ratio = r
            current_wep = x
            category = "straight"
            if r == 1:
                current_wep, category
    for x in WEPS_INSTANT:
        r = difflib.SequenceMatcher(None, wep_str, x.lower()).ratio()
        if r > highest_ratio and r > 0.8:
            highest_ratio = r
            current_wep = x
            category = "instant"
            if r == 1:
                current_wep, category
    

    return current_wep, category

#*gibt mir den Besten Schusswinkel wieder KATEGORIE: normal
def getBestAngleNORMAL(wind,myX,eX):
    delta = eX-myX
    bestangle = 0
    bestDeltaDif = 10000000
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
    return (bestangle + WindAngleDelta)

#*gibt mir den Besten Schusswinkel wieder KATEGORIE: straight
def getBestAngleSTRAIGHT(myPos, enemyPos):
    m = (myPos[1]-enemyPos[1])/(myPos[0]-enemyPos[0])
    angle = math.degrees(math.atan(m))
    if myPos[0] < enemyPos[0]: angle += 180
    print(round(angle))
    return round(angle)

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
    pyautogui.click(myPos[0], min(myPos[1]+250, 900))
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
def play(waitTime=10):
    while inLobby(): time.sleep(0.2)
    time.sleep(waitTime)
    myPos = getAverageTankCoordinates(MyTank)
    enemyPos = getAverageTankCoordinates(EnemyTank)
    round = 1
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
        wep_data = getSelectedWeapon()

        weapon = wep_data[0]
        weapon_cat = wep_data[1]
        
        shoot_data = 90
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
            wind = getWind()

            print(f"{weapon} wurde geschossen")

            delta_x = myPos[0] - enemyPos[0]
            calc_wind = wind[0]
            if delta_x >= 0: delta_x *= -1
            if wind[1] == "Links":
                calc_wind = wind[0] * -1
            #& Shoot-Category "normal"
            if weapon_cat == "normal": shoot_data = getBestAngleNORMAL(calc_wind,myPos[0],enemyPos[0])
            elif weapon_cat == "straight": shoot_data = getBestAngleSTRAIGHT(myPos,enemyPos)
            myPos = getMyExcaktCoordinates(myPos)
            resetAngle(myPos)
            print(f"Mein Winkel wurde zurückgesetzt! Ich habe nun genaue Koordinaten von {myPos}")

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
        time.sleep(3)

#*Dieser Loop ist die Brücke zwischen Lobby und Spiel
def main():
    #Regeln einmal printen
    print(RULES)

    #ErsterStart
    if inLobby() == False:
        print("Starte von der Lobby aus!")
        shoot()
        return
    first_xp = getXP()
    print(f"Deine aktuelle XP-Anzahl beträgt: {first_xp}")

    #Die Unendliche Schleife
    while True:
        pressReady()
        while inLobby(): time.sleep(1)
        play()
        nowXP = getXP()
        print(f"Deine aktuelle XP-Anzahl beträgt: {nowXP}\nSomit hast du {nowXP-first_xp} XP bisher gemacht!")

if __name__ == "__main__":
    wait = 3
    for x in range(wait):
        print(f"starting in {wait-x}...")
        time.sleep(1)

    #main()
    while True:
        try: main()
        except: pass