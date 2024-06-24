import json
import os
import keyboard
import environment, coordinateManager
from collections import deque
from pyautogui import locateOnScreen, click
from time import sleep
from threading import Thread
from pynput.keyboard import Listener

settings = None
try:
    settings = json.load(open("settings.json", encoding='utf-8'))
except:
    settings = json.load(open(f"{os.getcwd()}/src/settings.json", encoding='utf-8'))

targettedWeapons = settings["macro"]["shooting_weapons"]

coordManager = coordinateManager.CoordinateManager()
gameEnvironment = environment.GameEnvironment(coordManager)

OVERCHARGEWITHWEPS = False
def press_key(key, timer=0):
    keyboard.press(key)
    sleep(timer)
    keyboard.release(key)

def isVisible(picture, region):
    visible = locateOnScreen(f"Images/{picture}.png", grayscale=True, confidence=0.9, region=region)
    if visible: return True
    else: return False

def overcharge():
    global OVERCHARGEWITHWEPS
    while True:
        sleep(1)

        if not OVERCHARGEWITHWEPS: continue
        
        lastFoundWeapons = deque(maxlen=4)
        currentDirection = False
        adjusted = False

        while OVERCHARGEWITHWEPS:
            click(530,1000)
            sleep(0.25)
            
            #Solange ich noch nicht Pressen kann
            isGonnaShoot = False
            checks, maxChecks = 0, 8
            while not (isVisible("FireButton", region=(1000,900, 1420, 1100))):
                if checks >= maxChecks: continue
                
                selected_weapon = gameEnvironment.getWeapon()
                isGonnaShoot = selected_weapon[0] in targettedWeapons
                if not isGonnaShoot:
                    #In eine Richtung bewegen beim Waffen sortieren
                    if selected_weapon in lastFoundWeapons and selected_weapon != "undefined":
                        print("changing search direction")
                        currentDirection = not currentDirection
                        lastFoundWeapons.clear()
                    lastFoundWeapons.append(selected_weapon)
                    if currentDirection:
                        press_key("s")
                    else:
                        press_key("w")
                        
                checks += 1
                    
            if isGonnaShoot: 
                print("shooting")
                if not adjusted:
                    for _ in range(100):
                        press_key("down", timer=0.05)
                    
                    for _ in range(3):
                        sleep(0.2)
                        press_key("up",timer=0.05)
                    adjusted = True
                gameEnvironment.pressButton(gameEnvironment.FireButton)
            else:
                print("Overcharge")
                click(493,460)
                
            if currentDirection:
                press_key("s")
            else:
                press_key("w")

def on_press(key):
    global OVERCHARGEWITHWEPS
    key = "{0}".format(key).replace("'","")

    if key == settings["macro"]["overchargewithweps"]:
        OVERCHARGEWITHWEPS = not OVERCHARGEWITHWEPS
        if OVERCHARGEWITHWEPS: print(f"Overcharge with Weapons activated")
        else: print(f"Overcharge with Weapons deactivated")

def on_release(key):
    pass

if __name__ == "__main__":
    with Listener(on_press=on_press, on_release=on_release) as listener:
        Thread(target=overcharge).start()
        print("Makro Ready")
        listener.join()