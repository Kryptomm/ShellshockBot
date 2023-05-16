import math

GRAVITY = 0.359413

"""
Formulas for calculating x,y positions at a given time t with
    angle: [0,2*π]
    wind: [-100,100]
    time: N
    gravity: [0:N)
    speed: [0,N]
    
    x = (speed * cos(winkel) + wind * time) * time
    y = speed * sin(winkel) * time - 0.5 * gravity * time^2
"""
def calculatePosition(angle : int, strength : int ,wind : int, time : float) -> tuple[float,float]:
    angle = math.radians(angle)
    strength = -0.000003*strength**3 + 0.000492*strength**2 + -0.017763*strength**1 + 0.505767
    
    x = (strength * math.cos(angle) + wind * time) * time
    y = strength * math.sin(angle) * time - 0.5 * GRAVITY * time**2
    
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
    
    angle = 86
    strength = 100
    wind = 0
    
    t = 0
    maxT = 5
    step = 0.01
    
    X = []
    Y = []
    while t < maxT:
        x,y = calculatePosition(angle, strength, wind, t)
        X.append(x)
        Y.append(y)
        t += step
        
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
    
    plt.show()