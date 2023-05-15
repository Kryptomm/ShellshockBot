from tank import Tank, friendlyTank

def getAngleAndPower(myTank : friendlyTank, enemyTank : Tank, weapon_cat : str, wind : int, wind_richtung : str) -> tuple[int,int]:
    if weapon_cat == "normal": return __normal(myTank, enemyTank, wind, wind_richtung)
    return (90 , 100)

def __normal(myTank : friendlyTank, enemyTank : Tank, wind : int, wind_richtung : str) -> tuple[int,int]:
    distance = enemyTank.getXCoordinate() - myTank.getXCoordinate()
    
    angle = 90 + round(distance/myTank.SHOOTRADIUS * 4)
    
    return angle, 100