import math

from coordinateManager import CoordinateManager

GRAVITY = 0.359413
WIND_FACTOR = 0.000252 / 2
EPSILON = 0.015
MINTIME = 0
MAXTIME = 10
ITERATIONS = 20

MIN_STRENGTH = 20
MAX_STRENGTH = 100

def getAngleAndPower(myTank, enemyTank, weapon_cat : str, wind : int, extra_info ,CM : CoordinateManager) -> tuple[int,int]:
    if weapon_cat == "normal": return __normal(myTank, enemyTank, wind, CM)
    if weapon_cat == "straight": return __straight(myTank, enemyTank)
    if weapon_cat == "instant": return __instant()
    if weapon_cat == "45degrees": return __45degrees(myTank, enemyTank, wind, CM)
    if weapon_cat == "landing": return __landing(myTank, enemyTank, wind, CM)
    if weapon_cat == "radius": return __radius(myTank, enemyTank, extra_info, CM)
    
    return __normal(myTank, enemyTank, wind, CM)

"""
Formulas for calculating x,y positions at a given time t with
    angle: [0,359]
    wind: [-100,100]
    time: N
    gravity: [0:N)
    strength: [0,N]
"""
def __calculatePosition(angle : int, strength : int ,wind : int, time : float, coordManager : CoordinateManager, x_offset : float, y_offset : float) -> tuple[float,float]:
    angle = math.radians(angle)
    strength = 0.009133*strength - 0.0009244
    wind = WIND_FACTOR*wind
    
    x = (strength * coordManager.getScreenHeigth() / coordManager.getScreenWidth() * math.cos(angle) + wind * time) * time + x_offset
    y = -1* (strength * math.sin(angle) * time - 0.5 * GRAVITY * time**2) + y_offset
    
    return x,y

def __isCoordinateHitting(x : float, y : float, enemyTank) -> bool:
    if not (enemyTank.getXCoordinate() - EPSILON <= x <= enemyTank.getXCoordinate() + EPSILON): return False
    if not (enemyTank.getYCoordinate() - EPSILON <= y <= enemyTank.getYCoordinate() + EPSILON): return False
    return True

def __isAngleAndPowerHitting(angle : int, strength : int , wind : int, coordManager : CoordinateManager, myTank, enemyTank) -> bool:
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

def __normal(myTank, enemyTank, wind : int, CM : CoordinateManager) -> tuple[int,int]:
    angle = 90

    for i in range(0,45):
        for s in range(MAX_STRENGTH,MIN_STRENGTH,-1):
            if __isAngleAndPowerHitting(angle-i, s, wind, CM, myTank, enemyTank):
                return (angle-i, s)
            if __isAngleAndPowerHitting(angle+i, s, wind, CM, myTank, enemyTank):
                return (angle+i, s)
    
    #Einfach davon ausgehen das sowieso was hittet
    return angle,100

def __straight(myTank, enemyTank) -> tuple[int,int]:
    m = -1 * (myTank.absY - enemyTank.absY) / (myTank.absX - enemyTank.absX)
    angle = math.degrees(math.atan(m))

    angle += 360
    if enemyTank.getXCoordinate() < myTank.getXCoordinate():
        angle += 180
    
    return round(angle), 100

def __instant() -> tuple[int,int]:
    return 90,100

def __45degrees(myTank, enemyTank, wind : int, CM : CoordinateManager) -> tuple[int,int]:
    angle = 45 if myTank.getXCoordinate() <= enemyTank.getXCoordinate() else 135

    for i in range(0,20):
        for s in range(MAX_STRENGTH,MIN_STRENGTH,-1):
            if __isAngleAndPowerHitting(angle+i,s,wind,CM,myTank,enemyTank):
                return (angle-i, s)
            
    for i in range(0,20):
        for s in range(MAX_STRENGTH,MIN_STRENGTH,-1):
            if __isAngleAndPowerHitting(angle-i,s,wind,CM,myTank,enemyTank):
                return (angle-i, s)
            
    
    #Einfach davon ausgehen das sowieso was hittet
    return angle,100

def __landing(myTank, enemyTank, wind : int, CM : CoordinateManager) -> tuple[int,int]:
    angle = 67 if myTank.getXCoordinate() <= enemyTank.getXCoordinate() else 113

    for i in range(0,20):
        for s in range(MAX_STRENGTH,MIN_STRENGTH,-1):
            if __isAngleAndPowerHitting(angle+i,s,wind,CM,myTank,enemyTank):
                return (angle-i, s)
            
    for i in range(0,20):
        for s in range(MAX_STRENGTH,MIN_STRENGTH,-1):
            if __isAngleAndPowerHitting(angle-i,s,wind,CM,myTank,enemyTank):
                return (angle-i, s)
            
    
    #Einfach davon ausgehen das sowieso was hittet
    return angle,100

def __radius(myTank, enemyTank, delta ,CM : CoordinateManager) -> tuple[int,int]:
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
    enemyTank.getAverageCoordinatesBreadth()
    
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