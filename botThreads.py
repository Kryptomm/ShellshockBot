import colors

from threading import Thread
from time import sleep
from coordinateManager import CoordinateManager
from environment import GameEnvironment


def __gearDetection(coordManager : CoordinateManager, gameEnvironment : GameEnvironment) -> None:
    while True:
        while gameEnvironment.isShootingState or gameEnvironment.inLobbyState:
            sleep(1)
        #Implement gear detection here

thread_methods = [__gearDetection]

def initThreads(coordManager : CoordinateManager, gameEnvironment : GameEnvironment) -> None:
    for func in thread_methods:
        t = Thread(target=func, args=(coordManager, gameEnvironment))
        t.start()