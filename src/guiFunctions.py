import colors
import globals
import visualizer
import shootingStrategies
import win32gui
import time

from tank import Tank, friendlyTank, TankCollection
from environment import GameEnvironment
from coordinateManager import CoordinateManager

def runCheat(coordManager: CoordinateManager, gameEnvironment: GameEnvironment) -> dict:
    """Runs the cheat, generates the image and gives back Informations of the tanks and so on

    Args:
        coordManager (CoordinateManager): _description_
        gameEnvironment (GameEnvironment): _description_

    Returns:
        dict: With Information as show on the bottom or None if not worked.
    """
    foreground_window = win32gui.GetForegroundWindow()
    current_window_title = win32gui.GetWindowText(foreground_window)
    if current_window_title != "ShellShock Live": return None
    if not gameEnvironment.isMyTurn(): return None
    
    globals.CREATE_PICTURE = True
    visualizer.createImage(coordManager)
    
    myTank = friendlyTank(colors.TANK_OWN, coordManager, gameEnvironment, name="My Tank")
    myTank.getCoordinatesBrute()
    
    mateTanks = TankCollection(colors.TANK_MATE, coordManager, hideTanks = [myTank], minimum = 0, maximum=4,name="Mate")
    ground = gameEnvironment.getGroundColor()
    enemyColor = colors.convert_ground_to_enemy_color(ground)
    enemyTanks = TankCollection(enemyColor, coordManager, hideTanks = mateTanks.tanks + [myTank], minimum=0)
    
    if len(enemyTanks.tanks) == 0:
        return None
    
    weapon, weapon_category, weapon_extra_info = gameEnvironment.getWeapon()
    wind, wind_richtung = gameEnvironment.getWind()
    realwind = wind * wind_richtung
    
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
    
    groundColor = gameEnvironment.getGroundColor()
    calculations = shootingStrategies.getAngleAndPower(myTank, enemyTanks, weapon_category, realwind, weapon_extra_info, buffs, coordManager, groundColor, onlyOne=False)
    
    #Painting Part
    myTank.paintTank()
    mateTanks.paintTanks()
    enemyTanks.paintTanks()
    
    for array in buffs.values():
        for b in array:
            b.paintTank()
    
    return {"Image": globals.CURRENT_PICTURE,
            "MyTank": myTank,
            "enemyTanks": sorted(enemyTanks.tanks, key=lambda x: x.getXCoordinate()),
            "mateTanks": mateTanks.tanks,
            "buffs": buffs,
            "calculations": calculations,
            "wind": wind,
            "wind_dir": wind_richtung, #1 = Rechts, -1 = Links
            "weapon": weapon,
            "weapon_cat": weapon_category}
    
def convertAngleToStr(angle : int) -> str:
    """Converts an Angle to an appropriate str

    Args:
        angle (int): the angle

    Returns:
        str: the represantation
    """
    if angle == 90: return "90N"
    if angle == 270: return "-90N"
    if 90 <= angle <= 180: return f"{-angle % 90}L"
    if 180 <= angle <= 270: return f"-{angle % 90}L"
    if 0 <= angle <= 90: return f"{angle % 90}R"
    if 270 <= angle <= 360: return f"-{-angle % 90}R"