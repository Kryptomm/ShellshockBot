from coordinateManager import CoordinateManager, Point, Box
from environment import GameEnvironment
from tank import friendlyTank, TankCollection, Tank

import globals
import visualizer
import colors
import shootingStrategies
import time

CM = CoordinateManager()
GE = GameEnvironment(CM)

def testFunction(function, amount = 50):
    startTime = time.time()
    for i in range(amount):
        function()
    endTime = time.time() - startTime
    avg = f"{round(endTime / amount,3)}s"
    print(f"{avg=}")

def liveShot():
    globals.CREATE_PICTURE = True
    visualizer.createImage(CM)
    
    myTank = friendlyTank(colors.TANK_OWN, CM, GE, name="Mein Panzer")
    myTank.getCoordinatesBrute()
    myTank.paintTank()
    
    mateTanks = TankCollection(colors.TANK_MATE, CM, hideTanks=[myTank], minimum=0)
    mateTanks.paintTanks()
    
    ground = GE.getGroundColor()
    enemyColor = colors.convert_ground_to_enemy_color(ground)
    enemyTanks = TankCollection(enemyColor, CM, hideTanks=mateTanks.tanks + [myTank])
    enemyTanks.paintTanks()
    
    myTank.shoot(enemyTanks, executeShoot=False)

def calcShot():
    myTank = friendlyTank(colors.TANK_OWN, CM, GE, name="Mein Panzer")
    myTank.setPosition(Point(2140 / 2560, 660 / 1440))
    
    enemyTank1 = Tank(colors.TANK_ENEMY_DEFAULT, CM)
    enemyTank1.setPosition(Point(1300 / 2560, 760 / 1440))
    enemyTanks = TankCollection(colors.TANK_ENEMY_DEFAULT, CM, init=False)
    enemyTanks.tanks = [enemyTank1]
    
    ground = colors.GroundColor.BLUE
    
    weapon, weapon_category, weapon_extra_info = "shot", "normal", None
    wind, wind_richtung = 50, 1
    realwind = wind * wind_richtung
    
    buffTank = Tank(colors.GEAR, CM, name="x2", epsilon=0.02)
    buffTank.setPosition(Point(1650 / 2560, 260 / 1440))
    buffs = {"x3": [], "x2": [buffTank], "drone": [], "crate": []}
    
    calculations = shootingStrategies.getAngleAndPower(myTank, enemyTanks, weapon_category, realwind, weapon_extra_info, buffs, CM, ground, onlyOne=False)
    
def testVariousFunctions():
    GE.findPicture(GE.x2)

if __name__ == "__main__":
    startTime = time.time()
    
    #calcShot()
    liveShot()
    #testVariousFunctions()
    #testFunction(calcShot, amount=10)
    
    endTime = f"{round(time.time() - startTime,3)}s"
    print(f"{endTime=}")
    
    if globals.CREATE_PICTURE:
        visualizer.saveImage()
