import colors

from threading import Thread
from time import sleep
from coordinateManager import CoordinateManager
from environment import GameEnvironment

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
    """    """"""
    while True:
        gameEnvironment.shootingStateEvent.wait()
        gameEnvironment.lobbyStateEvent.wait()

        #Implement gear detection here
        
        
        sleep(0.01)

thread_methods = [__gearDetection]

def initThreads(coordManager : CoordinateManager, gameEnvironment : GameEnvironment) -> None:
    for func in thread_methods:
        t = Thread(target=func, args=(coordManager, gameEnvironment))
        t.start()