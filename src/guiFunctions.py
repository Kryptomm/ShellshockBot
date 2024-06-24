import colors
import globals
import visualizer
import shootingStrategies

from tank import Tank, friendlyTank, TankCollection
from environment import GameEnvironment
from coordinateManager import CoordinateManager

def runCheat(coordManager: CoordinateManager, gameEnvironment: GameEnvironment) -> dict:
    """Runs the cheat, generates the image and gives back Informations of the tanks and so on

    Args:
        coordManager (CoordinateManager): _description_
        gameEnvironment (GameEnvironment): _description_

    Returns:
        dict: {"Image", }
    """
    globals.CREATE_PICTURE = True
    visualizer.createImage(coordManager)
    
    myTank = friendlyTank(colors.TANK_OWN, coordManager, gameEnvironment, name="My Tank")
    myTank.getCoordinatesBrute()
    
    mateTanks = TankCollection(colors.TANK_MATE, coordManager, hideTanks = [myTank], minimum = 0)
    enemyTanks = TankCollection(colors.TANK_ENEMY, coordManager, hideTanks = mateTanks.tanks + [myTank], minimum=0)
    
    if len(enemyTanks.tanks) == 0:
        return None
    
    weapon, weapon_category, weapon_extra_info = gameEnvironment.getWeapon()
    wind, wind_richtung = gameEnvironment.getWind()
    
    buffs = gameEnvironment.findBuffs()
        
    #convert buffs to tanks
    key_to_epsilon = {"x3": 0.01, "x2": 0.02, "drone": 0.008, "crate": 0.005}
    for key in buffs:
        newList = []
        for buff in buffs[key]:
            buffTank = Tank(colors.GEAR, coordManager, name=key, epsilon=key_to_epsilon[key])
            buffTank.setPosition(buff)
            newList.append(buffTank)
        buffs[key] = newList
        
    calculations = shootingStrategies.getAngleAndPower(myTank, enemyTanks, weapon_category, wind, weapon_extra_info, buffs, coordManager, onlyOne=False)
    
    myTank.paintTank()
    mateTanks.paintTanks()
    enemyTanks.paintTanks()
    
    return {"Image": globals.CURRENT_PICTURE}