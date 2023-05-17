import math

from coordinateManager import CoordinateManager

GRAVITY = 0.359413
WIND_FACTOR = 0.000252 / 2
EPSILON = 0.010208
MINTIME = 0
MAXTIME = 10
ITERATIONS = 20

def getAngleAndPower(myTank, enemyTank, weapon_cat : str, wind : int, wind_richtung : int) -> tuple[int,int]:
    return __normal(myTank, enemyTank, wind, wind_richtung)

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

def __isAngleAndPowerHitting(angle : int, strength : int , wind : int, coordManager : CoordinateManager, x_offset : float, y_offset : float, enemyTank) -> bool:
    desiredX = enemyTank.getXCoordinate()
    time = MAXTIME / 2
    timeSize = MAXTIME / 4
    
    lookingFactor = 1 if x_offset <= enemyTank.getXCoordinate() else -1
    
    calculatedPosition = None
    for _ in range(ITERATIONS):
        calculatedPosition = __calculatePosition(angle, strength, wind, time, CM, x_offset, y_offset)
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

def __normal(myTank, enemyTank, wind : int, wind_richtung : int) -> tuple[int,int]:
    distance = enemyTank.getXCoordinate() - myTank.getXCoordinate()
    
    angle = 90 + round(distance / myTank.SHOOTRADIUS * 4)
    angle += round(wind / 14) * wind_richtung
    
    return angle, 100

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from tank import friendlyTank, Tank
    from environment import GameEnvironment
    from visualizer import drawCirclesAroundPixels
    
    CM = CoordinateManager()
    GE = GameEnvironment(CM)
    
    myTank = friendlyTank(CM.TANK1BOX, (36, 245, 41), CM, GE)
    myTank.getAverageCoordinatesBreadth()
    
    enemyTank = Tank((194,3,3), CM)
    enemyTank.getAverageCoordinatesBreadth()
    
    strength = 100
    angle = 99
    wind = 0
    for a in range(0,360):
        for s in range(0,101):
            if __isAngleAndPowerHitting(a,s,wind,CM,myTank.getXCoordinate(),myTank.getYCoordinate(),enemyTank):
                print("Strength:",s,"Angle",a)
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
    
    fig, ax = plt.subplots()

    # Plot all coordinates as scatter points
    ax.scatter(X,Y)

    # Color the first coordinate differently
    ax.scatter(X[0], Y[0], color='red')

    # Set axes limits
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 2)

    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')