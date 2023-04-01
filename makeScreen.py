from PIL import ImageGrab
import keyboard  # using module keyboard
from time import sleep

GAME_FIELD = [0,0,1919,920]
startNumber = 0

def makeScreenOfField():
    global startNumber
    cap = ImageGrab.grab(bbox = (GAME_FIELD[0],GAME_FIELD[1],GAME_FIELD[2],GAME_FIELD[3]))
    cap.save(f"./TestImages/gear_{startNumber}.jpg")
    startNumber += 1

if __name__ == "__main__":
    while True:  # making a loop
        try:  # used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('q'):  # if key 'q' is pressed 
                makeScreenOfField()
                sleep(0.3)
        except Exception as e:
            print(e)
            pass  # if user pressed a key other than the given key the loop will break