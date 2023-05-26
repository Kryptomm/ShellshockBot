import math

from typing import Union
from coordinateManager import CoordinateManager, Point
from decorators import timeit

GRAVITY = 0.359413
WIND_FACTOR = 0.000252 / 2
EPSILON = 0.01
MINTIME = 0
MAXTIME = 10
ITERATIONS = 15

MIN_STRENGTH = 20
MAX_STRENGTH = 100

@timeit("Calculate Angle and Power", print_result=True)
def getAngleAndPower(myTank, enemyTank, weapon_cat : str, wind : int, weapon_extra_info : Union[int, tuple], buffPosition, CM : CoordinateManager) -> tuple[int,int]:
    """based on Tank positions and wind and the weapon data, it generates the perfect angle and strength to shoot the enemy at

    Args:
        myTank (friendlyTank): initialized friendlyTank class
        enemyTank (Tank): initialized Tank class
        weapon_cat (str): Weapon Category, NOT the weapon itself
        wind (int): calculated wind. wind * wind direction. 68 to the left = -68
        extra_info (Union[int, tuple, None]): extra information provided by the weapon
        CM (CoordinateManager): initialized coordinateManager class

    Returns:
        tuple[int,int]: (angle, strength). angle starting at the right going up.
    """    
    if weapon_cat == "normal": return __normal(myTank, enemyTank, wind, buffPosition, CM)
    if weapon_cat == "straight": return __straight(myTank, enemyTank)
    if weapon_cat == "instant": return __instant()
    if weapon_cat == "45degrees": return __45degrees(myTank, enemyTank, wind, buffPosition, CM)
    if weapon_cat == "landing": return __landing(myTank, enemyTank, wind, buffPosition, CM)
    if weapon_cat == "radius": return __radius(myTank, enemyTank, weapon_extra_info, CM)
    
    return __normal(myTank, enemyTank, wind, CM)

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
    y = -1* (strength * math.sin(angle) * time - 0.5 * GRAVITY * time**2) + y_offset
    
    return x,y

def __isCoordinateHitting(x : float, y : float, tank) -> bool:
    """checks if a given coordinate is in hit range to an tank.
    it compares the relative coordinates of the tank!

    Args:
        x (float): x coordinate.
        y (float): y coordinate.
        enemyTank (Tank): initialized Tank class

    Returns:
        bool: _description_
    """
    if not (tank.getXCoordinate() - EPSILON       <= x <= tank.getXCoordinate() + EPSILON):       return False
    if not (tank.getYCoordinate() - EPSILON * 0.5 <= y <= tank.getYCoordinate() + EPSILON * 0.5): return False
    return True

def __isAngleAndPowerHitting(angle : int, strength : int , wind : int, coordManager : CoordinateManager, myTank, enemyTank) -> bool:
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
        bool: True if it is hitting, False if not, returns also True if enemyTank = None
    """
    if enemyTank == None: return True
    
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
            
        if __isCoordinateHitting(calculatedPosition[0], calculatedPosition[1], enemyTank): return True
    
    for i in range(-3,4):
        i = i/10
        if __isCoordinateHitting(calculatedPosition[0]+i, calculatedPosition[1], enemyTank): return True
    return False

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
    
    hittingPosition = (angle, 100)
    foundOne = False
    for i in range(0,45):
        for s in range(MAX_STRENGTH,MIN_STRENGTH,-1):
            if __isAngleAndPowerHitting(angle - i, s, wind, CM, myTank, enemyTank):
                if not foundOne:
                    hittingPosition = (angle - i, s)
                if __isAngleAndPowerHitting(angle - i, s, wind, CM, myTank, buffTank):
                    return hittingPosition
            
            if __isAngleAndPowerHitting(angle + i, s, wind, CM, myTank, enemyTank):
                if not foundOne:
                    hittingPosition = (angle + i, s)
                if __isAngleAndPowerHitting(angle+i, s, wind, CM, myTank, buffTank):
                    return hittingPosition
                    
    #Einfach davon ausgehen das sowieso was hittet
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

    hittingPosition = (angle, 100)
    foundOne = False
    for i in range(0,20):
        for s in range(MIN_STRENGTH,MAX_STRENGTH):
            if __isAngleAndPowerHitting(angle+i,s,wind,CM,myTank,enemyTank):
                if not foundOne:
                    hittingPosition = (angle-i, s)
                if __isAngleAndPowerHitting(angle+i, s, wind, CM, myTank, buffTank):
                    return hittingPosition
            
    for i in range(0,20):
        for s in range(MIN_STRENGTH,MAX_STRENGTH):
            if __isAngleAndPowerHitting(angle-i,s,wind,CM,myTank,enemyTank):
                if not foundOne:
                    hittingPosition = (angle-i, s)
                if __isAngleAndPowerHitting(angle+i, s, wind, CM, myTank, buffTank):
                    return hittingPosition
            
    #Einfach davon ausgehen das sowieso was hittet
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
    
    hittingPosition = (angle, 100)
    foundOne = False
    for i in range(0,20):
        for s in range(MAX_STRENGTH,MIN_STRENGTH,-1):
            if __isAngleAndPowerHitting(angle+i,s,wind,CM,myTank,enemyTank):
                if not foundOne:
                    hittingPosition = (angle-i, s)
                if __isAngleAndPowerHitting(angle+i, s, wind, CM, myTank, buffTank):
                    return hittingPosition
            
    for i in range(0,20):
        for s in range(MAX_STRENGTH,MIN_STRENGTH,-1):
            if __isAngleAndPowerHitting(angle-i,s,wind,CM,myTank,enemyTank):
                if not foundOne:
                    hittingPosition = (angle-i, s)
                if __isAngleAndPowerHitting(angle+i, s, wind, CM, myTank, buffTank):
                    return hittingPosition
            
    #Einfach davon ausgehen das sowieso was hittet
    return hittingPosition

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
    from tank import friendlyTank, Tank
    from environment import GameEnvironment
    from visualizer import drawCirclesAroundPixels
    
    CM = CoordinateManager()
    GE = GameEnvironment(CM)
    
    myTank = friendlyTank((36, 245, 41), CM, GE)
    myTank.getAverageCoordinatesBreadth()
    
    enemyTank = Tank((194,3,3), CM)
    enemyTank.setPosition(Point(0.721875, 0.7833333333333333))
    
    print(enemyTank.getPosition())
    
    myTank.shoot(enemyTank)
    exit()
    strength = 100
    angle = 99
    wind = 37
    
    print(__normal(myTank, enemyTank, wind, 1, CM))
    print(enemyTank.getPosition())

    t = 0
    maxT = 5
    step = 0.01
    
    X = []
    Y = []
    while t < maxT:
        x,y = __calculatePosition(angle, strength, wind, t, CM,myTank.getXCoordinate(),myTank.getYCoordinate())
        if __isCoordinateHitting(x,y,enemyTank):
            print("Ja",t)
        X.append(x)
        Y.append(y)
        t += step
        
    
    connectedList = []
    colors = []
    for i in range(len(X)):
        connectedList.append([X[i]*CM.getScreenWidth(), Y[i]*CM.getScreenHeigth()])
        colors.append((255,255,255))
    
    drawCirclesAroundPixels(connectedList,5,colors,CM,"Z_bild.png")