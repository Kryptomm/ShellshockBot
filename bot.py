from time import sleep
from pyautogui import click, FAILSAFE, FailSafeException

import colors
from definitions import RULES
from environment import GameEnvironment
from coordinateManager import CoordinateManager
from tank import Tank, friendlyTank

DEBUG = True

def gameLoop(coordManager : CoordinateManager, gameEnvironment : GameEnvironment) -> None:
    """Runs as long as one game is going. Automatically assigns tanks to given boxes,
    shoots the friendlyTank and moves it.
    sends you back to the lobby and fast forwards the loading screen.

    Args:
        coordManager (CoordinateManager): initialized coordinateManager class
        gameEnvironment (GameEnvironment): initialized GameEnvironment class
    """    
    myTank = friendlyTank(colors.FRIENDLY_TANK, coordManager, gameEnvironment)
    enemyTank = Tank(colors.ENEMY_TANK, coordManager)
    
    sleep(8)
    myTank.getAverageCoordinatesBreadth()
    enemyTank.getAverageCoordinatesBreadth()
    
    while True:
        while not gameEnvironment.isMyTurn():
            if gameEnvironment.inLoadingScreen(): click(1013, 1050)
            if gameEnvironment.inLobby(): return
            
        gameEnvironment.isShootingState = True
        
        myTank.getAverageCoordinatesBreadth()
        enemyTank.getAverageCoordinatesBreadth()
        
        if myTank.getXCoordinate() <= enemyTank.getXCoordinate():
            myTank.BOUNDARIES = coordManager.TANK1BOX
            enemyTank.BOUNDARIES = coordManager.TANK2BOX
        else:
            myTank.BOUNDARIES = coordManager.TANK2BOX
            enemyTank.BOUNDARIES = coordManager.TANK1BOX
            
        try:
            if myTank.move():
                myTank.getAverageCoordinatesBreadth()
        except FailSafeException:
            pass
        
        myTank.shoot(enemyTank)
        gameEnvironment.isShootingState = False

def lobbyWrapperLoop(coordManager : CoordinateManager, gameEnvironment : GameEnvironment) -> None:
    """Takes control over everything that is happening in the lobby as pushing ready and waiting there until the game started

    Args:
        coordManager (CoordinateManager): initialized coordinateManager class
        gameEnvironment (GameEnvironment): initialized GameEnvironment class
    """
    while True:
        gameEnvironment.pressButton(gameEnvironment.ReadyButton)
        
        while gameEnvironment.inLobby():
            sleep(0.1)
        
        gameEnvironment.inLobbyState = False
        gameLoop(coordManager, gameEnvironment)
        gameEnvironment.inLobbyState = True

def main() -> None:
    """Initializes everything and starts up the bot
    """
    print(RULES)
    
    coordManager = CoordinateManager()
    gameEnvironment = GameEnvironment(coordManager)
    
    if gameEnvironment.inLobby() == False and not DEBUG:
        print("Starte von der Lobby aus!")
        return

    lobbyWrapperLoop(coordManager, gameEnvironment)

if __name__ == "__main__":
    wait = 3
    for x in range(wait):
        print(f"starting in {wait-x}...")
        sleep(1)
    main()