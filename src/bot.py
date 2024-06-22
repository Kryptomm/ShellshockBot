from time import sleep
from pyautogui import click, FailSafeException

import colors
import globals
import os
import glob
import visualizer
import colorama
from colorama import Fore, Back, Style
from environment import GameEnvironment
from coordinateManager import CoordinateManager, Box
from tank import Tank, friendlyTank, TankCollection
from botThreads import initThreads
from decorators import timeit

@timeit("Play Game")
def gameLoop(coordManager : CoordinateManager, gameEnvironment : GameEnvironment) -> None:
    """Runs as long as one game is going. Automatically assigns tanks to given boxes,
    shoots the friendlyTank and moves it.
    sends you back to the lobby and fast forwards the loading screen.

    Args:
        coordManager (CoordinateManager): initialized coordinateManager class
        gameEnvironment (GameEnvironment): initialized GameEnvironment class
    """    

    #Wait until screen is fully there
    if not globals.DEBUG: sleep(12)
    
    #initialize Tanks
    #Search for the first time
    myTank = friendlyTank(colors.TANK_OWN, coordManager, gameEnvironment, name="My Tank")
    myTank.getCoordinatesBrute()
    
    mateTanks = TankCollection(colors.TANK_MATE, coordManager, hideTanks = [myTank], minimum = 0)
    enemyTanks = TankCollection(colors.TANK_ENEMY, coordManager, hideTanks = mateTanks.tanks + [myTank])
    
    while True:
        while not gameEnvironment.isMyTurn():
            #click on fast forward
            if gameEnvironment.inLoadingScreen(): click(coordManager.convertFloatToWidth(0.527604), coordManager.convertFloatToHeigth(0.9722222))
            if gameEnvironment.inLobby(): 
                return
            
        gameEnvironment.isShootingState = True
        
        if not myTank.isInSameSpot():
            myTank.getCoordinatesBreadth()
        print(myTank)
        
        mateTanks.updateTankCollection(hideTanks = [myTank])
        enemyTanks.updateTankCollection(hideTanks = mateTanks.tanks + [myTank])
        
        if globals.CREATE_PICTURE:
            visualizer.createImage(coordManager)
            
        myTank.shoot(enemyTanks)
        gameEnvironment.isShootingState = False
        
        if globals.CREATE_PICTURE:
            myTank.paintTank()
            mateTanks.paintTanks()
            enemyTanks.paintTanks()
            visualizer.saveImage()

def lobbyWrapperLoop(coordManager : CoordinateManager, gameEnvironment : GameEnvironment) -> None:
    """Takes control over everything that is happening in the lobby as pushing ready and waiting there until the game started

    Args:
        coordManager (CoordinateManager): initialized coordinateManager class
        gameEnvironment (GameEnvironment): initialized GameEnvironment class
    """
    roundsPlayed = 0
    while True:
        gameEnvironment.pressButton(gameEnvironment.ReadyButton)
        click(50,50)
        
        while gameEnvironment.inLobby():
            sleep(0.1)
        
        gameEnvironment.inLobbyState = False
        gameLoop(coordManager, gameEnvironment)
        roundsPlayed += 1
        print(f"Rounds already played: {roundsPlayed}")
        gameEnvironment.inLobbyState = True

def main() -> None:
    """Initializes everything and starts up the bot
    """
    coordManager = CoordinateManager()
    gameEnvironment = GameEnvironment(coordManager)
    
    png_files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), "*.png"))
    for file_path in png_files:
        os.remove(file_path)
        
    print(globals.RULES)
    
    wait = 3
    for x in range(wait,0,-1):
        print(f"starting in {x}...")
        sleep(1)
    
    colorama.init()
    globals.initializeGlobals()
    if globals.CREATE_PICTURE:
        visualizer.createImage(coordManager)
        visualizer.saveImage()
    
    if gameEnvironment.inLobby() == False and not globals.DEBUG:
        print("Starte von der Lobby aus!")
        return

    #initThreads(coordManager, gameEnvironment)
    lobbyWrapperLoop(coordManager, gameEnvironment)

if __name__ == "__main__":
    main()