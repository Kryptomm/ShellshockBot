import math

from coordinateManager import CoordinateManager

GRAVITY = 0.359413
WIND_FACTOR = 0.000252 / 2

"""
Formulas for calculating x,y positions at a given time t with
    angle: [0,359]
    wind: [-100,100]
    time: N
    gravity: [0:N)
    strength: [0,N]
"""
def calculatePosition(angle : int, strength : int ,wind : int, time : float, coordManager : CoordinateManager, x_offset : float, y_offset : float) -> tuple[float,float]:
    angle = math.radians(angle)
    strength = 0.009133*strength - 0.0009244
    wind = WIND_FACTOR*wind
    
    x = (strength * CM.getScreenHeigth() / CM.getScreenWidth() * math.cos(angle) + wind * time) * time + x_offset
    y = -1* (strength * math.sin(angle) * time - 0.5 * GRAVITY * time**2) + y_offset
    
    return x,y

def getAngleAndPower(myTank, enemyTank, weapon_cat : str, wind : int, wind_richtung : int) -> tuple[int,int]:
    if weapon_cat == "normal": return __normal(myTank, enemyTank, wind, wind_richtung)
    
    return __normal(myTank, enemyTank, wind, wind_richtung)

def __normal(myTank, enemyTank, wind : int, wind_richtung : int) -> tuple[int,int]:
    distance = enemyTank.getXCoordinate() - myTank.getXCoordinate()
    
    angle = 90 + round(distance / myTank.SHOOTRADIUS * 4)
    angle += round(wind / 14) * wind_richtung
    
    return angle, 100

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from tank import friendlyTank
    from environment import GameEnvironment
    from visualizer import drawCirclesAroundPixels
    
    CM = CoordinateManager()
    GE = GameEnvironment(CM)
    
    myTank = friendlyTank(CM.TANK1BOX, (36, 245, 41), CM, GE)
    myTank.getAverageCoordinatesBreadth()
    
    angle = 54
    strength = 78
    wind = -44
    
    t = 0
    maxT = 5
    step = 0.01
    
    X = []
    Y = []
    firstXbelow0 = 0
    found = False
    while t < maxT:
        x,y = calculatePosition(angle, strength, wind, t, CM,myTank.getXCoordinate(),myTank.getYCoordinate())
        X.append(x)
        Y.append(y)
        t += step
        
        if y <= 0 and not found and x > 0.02:
            found = True
            firstXbelow0 = x
    
    connectedList = []
    colors = []
    for i in range(len(X)):
        connectedList.append([X[i]*CM.getScreenWidth(), Y[i]*CM.getScreenHeigth()])
        colors.append((255,255,255))
    
    drawCirclesAroundPixels(connectedList,5,colors,CM,"Z_bild.png")
    
    print(firstXbelow0)
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