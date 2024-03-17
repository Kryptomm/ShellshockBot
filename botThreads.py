import colors

from pyautogui import moveTo
from threading import Thread
from time import sleep
from coordinateManager import CoordinateManager
from environment import GameEnvironment
from tank import Tank

"""
Threads should only run if the bot is currently waiting for something
GameEnvironment Class provides signals as:
-shootingStateEvent: passes through when bot is not shooting
-lobbyStateEvent: passes through when bot is not in the lobby
"""

def __gearDetection(coordManager : CoordinateManager, gameEnvironment : GameEnvironment) -> None:
    """automatic gear detection. automatically moves mouse to whereever a gear is

    Args:
        coordManager (CoordinateManager): initialized CoordinateManager Class
        gameEnvironment (GameEnvironment): initialized GameEnvironment Class
    """
    
    #Take a Tank as a blueprint for the gear since it has every function a gear needs.
    gear = Tank(colors.GEAR, coordManager, name="Gear")
    
    while True:
        gameEnvironment.shootingStateEvent.wait()
        gameEnvironment.lobbyStateEvent.wait()

        _, colorDistance = gear.getCoordinatesBrute()
        if colorDistance <= 10:
            moveTo(gear.absX, gear.absY)
            gear.getCoordinatesBreadth()
            moveTo(gear.absX, gear.absY)
        else:
            sleep(0.05)


def initThreads(coordManager : CoordinateManager, gameEnvironment : GameEnvironment) -> None:
    thread_methods = [__gearDetection]
    for func in thread_methods:
        t = Thread(target=func, args=(coordManager, gameEnvironment))
        t.start()
        

if __name__ == "__main__":
    CM = CoordinateManager()
    GE = GameEnvironment(CM)
    
    __gearDetection(CM, GE)