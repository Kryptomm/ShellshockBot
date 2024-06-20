import math
import numpy as np
import visualizer
import colors
import globals

from typing import Union
from PIL import Image, ImageGrab
from scipy.ndimage import binary_dilation
from coordinateManager import CoordinateManager, Point
from decorators import timeit
from skimage.feature import canny

GRAVITY = 0.359413
WIND_FACTOR = 0.000252 / 2
EPSILON = 0.01
MINTIME = 0
MAXTIME = 10
ITERATIONS = 15

MIN_STRENGTH = 20
MAX_STRENGTH = 100

@timeit("Calculate Angle and Power", print_result=True)
def getAngleAndPower(myTank, enemyTanks, weapon_cat : str, wind : int, weapon_extra_info : Union[int, tuple], buffPosition, CM : CoordinateManager) -> dict[object, tuple[int, int]]:
    """based on Tank positions and wind and the weapon data, it generates the perfect angle and strength to shoot the enemy at

    Args:
        myTank (friendlyTank): initialized friendlyTank class
        enemyTanks (EnemyTanks): initialized EnemyTank class
        weapon_cat (str): Weapon Category, NOT the weapon itself
        wind (int): calculated wind. wind * wind direction. 68 to the left = -68
        extra_info (Union[int, tuple, None]): extra information provided by the weapon
        CM (CoordinateManager): initialized coordinateManager class

    Returns:
        tuple[int,int]: (angle, strength). angle starting at the right going up.
    """
    calculations = {}
    
    for enemyTank in enemyTanks.enemies:
        if weapon_cat == "normal": calculations[enemyTank] =  __normal(myTank, enemyTank, wind, buffPosition, CM)
        elif weapon_cat == "straight": calculations[enemyTank] = __straight(myTank, enemyTank)
        elif weapon_cat == "instant": calculations[enemyTank] = __instant()
        elif weapon_cat == "45degrees": calculations[enemyTank] = __45degrees(myTank, enemyTank, wind, buffPosition, CM)
        elif weapon_cat == "landing": calculations[enemyTank] = __landing(myTank, enemyTank, wind, buffPosition, CM)
        elif weapon_cat == "radius": calculations[enemyTank] = __radius(myTank, enemyTank, weapon_extra_info, CM)
        else: calculations[enemyTank] = __normal(myTank, enemyTank, wind, buffPosition, CM)
        
    return calculations



#HILFSMETHODEN ZUR BERECHNUNG

def __calculatePosition(angle : int, strength : int ,wind : int, time : float, coordManager : CoordinateManager, x_offset : float, y_offset : float) -> tuple[float,float]:
    """Formulas for calculating x,y positions at a given time t with
    angle: [0,359]
    wind: [-100,100]
    strength: [0,100]
    time: R
    gravity: [0:inf)

    Args:
        angle (int): angle of the desired shot [0,359]
        strength (int): strength of the desired shot [0,100]
        wind (int): wind the environment currently has [-100,100]
        time (float): position at time to calculate
        coordManager (CoordinateManager): initialized coordinateManager class
        x_offset (float): x offset of the shot, most likely your tank position
        y_offset (float): y offset of the shot, most likely your tank position

    Returns:
        tuple[float,float]: (x, y) position in relative coordinates
    """
    angle = math.radians(angle)
    strength = 0.009133*strength - 0.0009244
    wind = WIND_FACTOR*wind
    
    x = (strength * coordManager.getHeigthWidthRatio() * math.cos(angle) + wind * time) * time + x_offset
    y = -1 * (strength * math.sin(angle) * time - 0.5 * GRAVITY * time**2) + y_offset
    
    return x,y

def __isAngleAndPowerHitting(angle : int, strength : int , wind : int, coordManager : CoordinateManager, myTank, enemyTank) -> tuple[bool,float]:
    """checks if an angle and power is hitting by doing binary search on the time to search the time it hits
    the enemy tank and then checks if the y coordinate matches the enemytank at this point in time.

    Args:
        angle (int): angle of the desired shot [0,359]
        strength (int): strength of the desired shot [0,100]
        wind (int): wind the environment currently has [-100,100]
        coordManager (CoordinateManager): initialized coordinateManager class
        myTank (_type_): initialized friendlyTank class, can also be Tank class
        enemyTank (_type_): initialized Tank class

    Returns:
        tuple[bool, float]: True if it is hitting, False if not, returns also True if enemyTank = None. Also returns the time when it hits
    """
    if enemyTank == None: return (True,0)
    
    desiredX = enemyTank.getXCoordinate()
    time = MAXTIME / 2
    timeSize = MAXTIME / 4
    
    lookingFactor = 1 if myTank.getXCoordinate() <= enemyTank.getXCoordinate() else -1
    
    calculatedPosition = None
    for _ in range(ITERATIONS):
        calculatedPosition = __calculatePosition(angle, strength, wind, time, coordManager, myTank.getXCoordinate(), myTank.getYCoordinate())
        if calculatedPosition[0] >=  desiredX:
            time = time - timeSize * lookingFactor
        else:
            time = time + timeSize * lookingFactor
        timeSize = timeSize / 2
            
        if enemyTank.isPointHitting(calculatedPosition[0], calculatedPosition[1]): return (True, time)
    
    for i in range(-3,4):
        i = i/10
        if enemyTank.isPointHitting(calculatedPosition[0]+i, calculatedPosition[1]): return (True, time)
        
    return (False, time)

def __getEdgesScreenshot(coordManager : CoordinateManager) -> Image:
    """Returns a screenshot where everything is black except the bumpers.

    Args:
        coordManager (CoordinateManager): initialized coordinateManager class

    Returns:
        Image: Leaves whites pixels everywhere where is a bumper
    """
    colors_to_preserve = [colors.BUMPER]
    image = ImageGrab.grab(bbox=coordManager.GAME_FIELD.getBoundariesNormalized(coordManager)).convert("RGBA")

    np_image = np.array(image)

    color_mask = np.zeros(np_image.shape[:2], dtype=bool)
    for color in colors_to_preserve:
        color_mask |= np.all(np_image[:, :, :3] == color, axis=2)
    dilated_mask = binary_dilation(color_mask, iterations=5)

    blue_channel = np_image[:, :, 2]
    edges = canny(blue_channel, sigma=10)
    dilated_edges = binary_dilation(edges, iterations=3)

    combined_mask = np.logical_or(dilated_mask, dilated_edges)
    
    np_image[combined_mask] = [255, 255, 255, 255]
    np_image[~combined_mask] = [0, 0, 0, 0]

    filtered_image = Image.fromarray(np_image)
    
    if globals.CREATE_PICTURE:
        globals.CURRENT_PICTURE.paste(filtered_image, (0, 0), mask=filtered_image)
    
    return filtered_image

def __isHittingEdge(angle : int, strength: int, wind : float, myTank, enemyTank, floatingTime : float ,bumperScreenshot : Image, buffTank, coordManager : CoordinateManager) -> bool:
    """Tells you if a shot is hitting a bumper

    Args:
        myTank (_type_): initialized friendlyTank class
        enemyTank (_type_): initialized Tank class
        floatingTime (float): the time it needs from start to end to hit the enemy
        bumperScreenshot (Image): the screenshot of the bumpers
        coordManager (CoordinateManager): initialized coordinateManager class

    Returns:
        bool: returns True if the shot is hitting a bumper, False if not
    """
    if buffTank:
        for x in range(coordManager.convertFloatToWidth(buffTank.getXCoordinate() - 0.03), coordManager.convertFloatToWidth(buffTank.getXCoordinate() + 0.03)):
            for y in range(coordManager.convertFloatToHeigth(buffTank.getYCoordinate() - 0.05), coordManager.convertFloatToHeigth(buffTank.getYCoordinate() + 0.05)):
                try: bumperScreenshot.putpixel((x,y),(0,0,0))
                except: pass
        
    timeSteps = floatingTime / abs(enemyTank.absX - myTank.absX) / 3
    ignoreTime = floatingTime * 0.04
    currentTime = 0 + ignoreTime
    while currentTime < (floatingTime - ignoreTime * 0.25):
        x,y = __calculatePosition(angle, strength, wind, currentTime, coordManager, myTank.getXCoordinate(), myTank.getYCoordinate())
        currentTime += timeSteps
        visualizer.paintPixels((x,y),1,(255,255,255),coordManager)
        x,y = coordManager.convertFloatToWidth(x), coordManager.convertFloatToHeigth(y)
        if not (0 <= x < bumperScreenshot.width and 0 <= y < bumperScreenshot.height):
            continue
        
        color = bumperScreenshot.getpixel((x,y))
        if color[0] == 255 and color[1] == 255 and color[2] == 255:
            return True
    
    return False

#HIER BEGINNEN DIE EIGENTLICHEN METHODEN ZUR BERECHNUNG

def __normal(myTank, enemyTank, wind : int, buffTank, CM : CoordinateManager) -> tuple[int,int]:
    """calculates angle and power for the shot type "normal".
    Start from angle 90 and tries its best to find a strength to it.
    if not strength found for angle 90, it goes to 89, then 91, then 88, then 92, ...,45,135
    if nothing was found in all those angles (which is possibly only a bug and happens really rare)
    then a standart angle and strength is returned that will not hit, but wont crash the program

    Args:
        myTank (_type_): initialized friendlyTank class, can also be Tank class
        enemyTank (_type_): initialized Tank class
        wind (int): wind the environment currently has [-100,100]
        CM (CoordinateManager): initialized coordinateManager class

    Returns:
        tuple[int,int]: (angle, strength)
    """
    angle = 90
    bumperScreenshot = __getEdgesScreenshot(CM)
    
    hittingPosition = (angle, 100)
    foundOne = False
    for i in range(0,45):
        for s in range(MIN_STRENGTH, MAX_STRENGTH):
            isHitting, whenHitting = __isAngleAndPowerHitting(angle - i, s, wind, CM, myTank, enemyTank)
            if isHitting:
                if __isHittingEdge(angle - i, s, wind, myTank, enemyTank, whenHitting, bumperScreenshot, buffTank, CM): continue
                if not foundOne:
                    hittingPosition = (angle - i, s)
                    foundOne = True
                if __isAngleAndPowerHitting(angle - i, s, wind, CM, myTank, buffTank)[0]:
                    if buffTank:
                        print("Found a way to hit Buff AND Enemy")
                    return (angle - i, s)
            
            isHitting, whenHitting = __isAngleAndPowerHitting(angle + i, s, wind, CM, myTank, enemyTank)
            if isHitting:
                if __isHittingEdge(angle + i, s, wind, myTank, enemyTank, whenHitting, bumperScreenshot, buffTank, CM): continue
                if not foundOne:
                    hittingPosition = (angle + i, s)
                    foundOne = True
                if __isAngleAndPowerHitting(angle+i, s, wind, CM, myTank, buffTank)[0]:
                    if buffTank:
                        print("Found a way to hit Buff AND Enemy")
                    return (angle + i, s)
                
    if buffTank:  
        print("Did not find a way to hit Buff AND Enemy, now only hitting Enemy")
    return hittingPosition

def __45degrees(myTank, enemyTank, wind : int, buffTank, CM : CoordinateManager) -> tuple[int,int]:
    """Calculates angle and strength for the shot type "45degrees". Does it by calculating the
    strength for the angle 45, if non is found, go to angle 46, 47, 48, ... 65
    if really there was no strength found for all of them go to
    44, 43 ,42, ... 25.

    Args:
        myTank (_type_): initialized friendlyTank class, can also be Tank class
        enemyTank (_type_): initialized Tank class
        wind (int): wind the environment currently has [-100,100]
        CM (CoordinateManager): initialized coordinateManager class

    Returns:
        tuple[int,int]: (angle, strength)
    """
    angle = 45 if myTank.getXCoordinate() <= enemyTank.getXCoordinate() else 135

    bumperScreenshot = __getEdgesScreenshot(CM)

    hittingPosition = (angle, 100)
    foundOne = False
    for i in range(0,20):
        for s in range(MIN_STRENGTH, MAX_STRENGTH):
            isHitting, whenHitting = __isAngleAndPowerHitting(angle + i, s, wind, CM, myTank, enemyTank)
            if isHitting:
                if __isHittingEdge(angle + i, s, wind, myTank, enemyTank, whenHitting, bumperScreenshot, buffTank, CM): continue
                if not foundOne:
                    hittingPosition = (angle+i, s)
                    foundOne = True
                if __isAngleAndPowerHitting(angle+i, s, wind, CM, myTank, buffTank)[0]:
                    if buffTank:
                        print("Found a way to hit Buff AND Enemy")
                    return (angle + i, s)
            
    for i in range(0,20):
        for s in range(MIN_STRENGTH, MAX_STRENGTH):
            isHitting, whenHitting = __isAngleAndPowerHitting(angle - i, s, wind, CM, myTank, enemyTank)
            if isHitting:
                if __isHittingEdge(angle - i, s, wind, myTank, enemyTank, whenHitting, bumperScreenshot, buffTank, CM): continue
                if not foundOne:
                    hittingPosition = (angle-i, s)
                    foundOne = True
                if __isAngleAndPowerHitting(angle-i, s, wind, CM, myTank, buffTank)[0]:
                    if buffTank:
                        print("Found a way to hit Buff AND Enemy")
                    return (angle - i, s)
            
    if buffTank:  
        print("Did not find a way to hit Buff AND Enemy, now only hitting Enemy")
    return hittingPosition

def __landing(myTank, enemyTank, wind : int, buffTank, CM : CoordinateManager) -> tuple[int,int]:
    """Calculates angle and strength for the shot type "landing". Does it by calculating the
    strength for the angle 67, if non is found, go to angle 68, 69, 70, ... 86
    if really there was no strength found for all of them go to
    66, 65 ,64, ... 48.

    Args:
        myTank (_type_): initialized friendlyTank class, can also be Tank class
        enemyTank (_type_): initialized Tank class
        wind (int): wind the environment currently has [-100,100]
        CM (CoordinateManager): initialized coordinateManager class

    Returns:
        tuple[int,int]: (angle, strength)
    """
    angle = 67 if myTank.getXCoordinate() <= enemyTank.getXCoordinate() else 113
    
    bumperScreenshot = __getEdgesScreenshot(CM)
    
    hittingPosition = (angle, 100)
    foundOne = False
    for i in range(0,20):
        for s in range(MIN_STRENGTH, MAX_STRENGTH):
            isHitting, whenHitting = __isAngleAndPowerHitting(angle + i, s, wind, CM, myTank, enemyTank)
            if isHitting:
                if __isHittingEdge(angle + i, s, wind, myTank, enemyTank, whenHitting, bumperScreenshot, buffTank, CM): continue
                if not foundOne:
                    hittingPosition = (angle+i, s)
                    foundOne = True
                if __isAngleAndPowerHitting(angle+i, s, wind, CM, myTank, buffTank)[0]:
                    if buffTank:
                        print("Found a way to hit Buff AND Enemy")
                    return (angle + i, s)
            
    for i in range(0,20):
        for s in range(MIN_STRENGTH, MAX_STRENGTH):
            isHitting, whenHitting = __isAngleAndPowerHitting(angle - i, s, wind, CM, myTank, enemyTank)
            if isHitting:
                if __isHittingEdge(angle - i, s, wind, myTank, enemyTank, whenHitting, bumperScreenshot, buffTank, CM): continue
                if not foundOne:
                    hittingPosition = (angle-i, s)
                    foundOne = True
                if __isAngleAndPowerHitting(angle-i, s, wind, CM, myTank, buffTank)[0]:
                    if buffTank:
                        print("Found a way to hit Buff AND Enemy")
                    return (angle - i, s)
            
    if buffTank:  
        print("Did not find a way to hit Buff AND Enemy, now only hitting Enemy")
    return hittingPosition

def __straight(myTank, enemyTank) -> tuple[int,int]:
    """calculates the angle for myTank to shoot at enemyTank if it has a weapon that goes straight at him.
    calculates the slope between them. multiplies by -1, because the y-coordinate 0 is on top.
    then takes the atan to take the angle and converts it to degrees.
    Adds 360 to not be in the negatives. and adds 180 if im on the left because slope would have said shoot left.

    Args:
        myTank (_type_): initialized friendlyTank class, can also be Tank class
        enemyTank (_type_): initialized Tank class

    Returns:
        tuple[int,int]: (angle, strength)
    """
    m = -1 * (myTank.absY - enemyTank.absY) / (myTank.absX - enemyTank.absX)
    angle = math.degrees(math.atan(m))

    angle += 360
    if enemyTank.getXCoordinate() < myTank.getXCoordinate():
        angle += 180
    
    return (round(angle) % 360, 100)

def __instant() -> tuple[int,int]:
    """does nothing than returning the basic angle 90 and 100

    Returns:
        tuple[int,int]: (90,100)
    """
    return 90,100

def __radius(myTank, enemyTank, delta ,CM : CoordinateManager) -> tuple[int,int]:
    """Calculates Angle AND Strength for a weapon that needs to go straight at someone with a needed strength.
    does it by getting the angle from the __straight function and the calculates the distance to the other tank
    calculats then the amount of radia it needs to shoot at. this then converts into strength.

    Args:
        myTank (_type_): initialized friendlyTank class, can also be Tank class
        enemyTank (_type_): initialized Tank class
        wind (int): wind the environment currently has [-100,100]
        CM (CoordinateManager): initialized coordinateManager class
        
    Returns:
        tuple[int,int]: (angle, strength)
    """
    angle = __straight(myTank, enemyTank)[0]
    distance = math.sqrt((myTank.getXCoordinate() - enemyTank.getXCoordinate())**2 +
                         ((myTank.getYCoordinate() - enemyTank.getYCoordinate()) * CM.getScreenHeigth() / CM.getScreenWidth())**2)
    
    radia = distance / CM.RADIUS
    strengh = min(round(radia * delta),100)
    
    return angle, strengh



if __name__ == "__main__":
    from tank import friendlyTank, Tank, EnemyTanks
    from environment import GameEnvironment
    from time import sleep
    import os, glob
    
    CM = CoordinateManager()
    GE = GameEnvironment(CM)
    
    globals.CREATE_PICTURE = True
    sleep(1)
    visualizer.createImage(CM)
    
    myTank = friendlyTank(colors.FRIENDLY_TANK, CM, GE, name="Mein Panzer")
    myTank.getCoordinatesBrute()
    
    enemyTanks = EnemyTanks(colors.ENEMY_TANK, CM, myTank)
    enemyTanks.paintEnemies()

    visualizer.paintPixels(myTank.getPosition()(), 15, colors.FRIENDLY_TANK, CM)
    
    myTank.shoot(enemyTanks)
    sleep(7)
    myTank.shoot(enemyTanks)
    visualizer.saveImage()
