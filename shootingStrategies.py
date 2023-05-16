def getAngleAndPower(myTank, enemyTank, weapon_cat : str, wind : int, wind_richtung : int) -> tuple[int,int]:
    if weapon_cat == "normal": return __normal(myTank, enemyTank, wind, wind_richtung)
    
    return __normal(myTank, enemyTank, wind, wind_richtung)

def __normal(myTank, enemyTank, wind : int, wind_richtung : int) -> tuple[int,int]:
    distance = enemyTank.getXCoordinate() - myTank.getXCoordinate()
    
    angle = 90 + round(distance / myTank.SHOOTRADIUS * 4)
    angle += round(wind / 14) * wind_richtung
    
    return angle, 100