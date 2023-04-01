import win32gui
import win32api
from PIL import ImageGrab
import math
import queue
import numpy as np

dc = win32gui.GetDC(0)

white = win32api.RGB(255, 255, 255)

MyTank = (0, 220, 15)
EnemyTank = (194,3,3)
GAME_FIELD = [0,0,1920,920]

RADIUS = 343

Nums = np.array([[[1,1,1],
                [1,0,1],
                [1,0,1],
                [1,0,1],
                [1,1,1]],
                
                [[0,1,0],
                [0,1,0],
                [0,1,0],
                [0,1,0],
                [0,1,0]],
                
                [[1,1,1],
                [0,0,1],
                [1,1,1],
                [1,0,0],
                [1,1,1]],
                
                [[1,1,1],
                [0,0,1],
                [1,1,1],
                [0,0,1],
                [1,1,1]],
                
                [[1,0,1],
                [1,0,1],
                [1,1,1],
                [0,0,1],
                [0,0,1]],
                
                [[1,1,1],
                [1,0,0],
                [1,1,1],
                [0,0,1],
                [1,1,1]],
                
                [[1,1,1],
                [1,0,0],
                [1,1,1],
                [1,0,1],
                [1,1,1]],
                
                [[1,1,1],
                [0,0,1],
                [0,0,1],
                [0,0,1],
                [0,0,1]],

                [[1,1,1],
                [1,0,1],
                [1,1,1],
                [1,0,1],
                [1,1,1]],
                
                [[1,1,1],
                [1,0,1],
                [1,1,1],
                [0,0,1],
                [1,1,1]],

                [[0,0,0],
                [0,0,0],
                [0,0,0],
                [1,1,0],
                [1,1,0]]])

def getAverageCoordinatesBreadth(capColor, lastX, lastY, everyPixel=2):
    s = ImageGrab.grab(bbox = (GAME_FIELD[0],GAME_FIELD[1],GAME_FIELD[2],GAME_FIELD[3]))
    q = queue.Queue()
    visited = np.zeros((GAME_FIELD[2],GAME_FIELD[3]), dtype=bool)

    q.put([lastX, lastY])
    visited[lastX][lastY] = True
    minD = [0,0,float("inf")]

    while not q.empty():
        field = q.get()
        color = s.getpixel((field[0], field[1]))
        d = math.sqrt((color[0]-capColor[0])**2+(color[1]-capColor[1])**2+(color[2]-capColor[2])**2)
        if d < minD[2]: minD = [field[0], field[1], d]

        if d < 15: return minD

        if field[0] + everyPixel < GAME_FIELD[2] and not visited[field[0] + everyPixel][field[1]]:
            q.put([field[0] + everyPixel, field[1]])
            visited[field[0] + everyPixel][field[1]] = True
        if field[0] - everyPixel > GAME_FIELD[0] and not visited[field[0] - everyPixel][field[1]]:
            q.put([field[0] - everyPixel, field[1]])
            visited[field[0] - everyPixel][field[1]] = True
        if field[1] + everyPixel < GAME_FIELD[3] and not visited[field[0]][field[1] + everyPixel]:
            q.put([field[0], field[1] + everyPixel])
            visited[field[0]][field[1] + everyPixel] = True
        if field[1] - everyPixel > GAME_FIELD[1] and not visited[field[0]][field[1] - everyPixel]:
            q.put([field[0], field[1] - everyPixel])
            visited[field[0]][field[1] - everyPixel] = True
            
    return minD

def drawInformation(radia):
    #Radia
    for n, b in enumerate(str(radia)):
        if b == ".":
            pass
        else:
            for y in range(0,len(Nums[n])):
                for x in range(0,len(Nums[n][y])):
                    win32gui.SetPixel(dc, x, y, white)

def drawLine(m,b,first,second):
    for _ in range(0,100):
        for x in range(min(first[0], second[0]), max(first[0], second[0])):
            y = int(m * x + b)
            win32gui.SetPixel(dc, x, y, white)

def main():
    first = getAverageCoordinatesBreadth(MyTank, int(GAME_FIELD[2]/2),int(GAME_FIELD[3]/2), everyPixel=4)
    second = getAverageCoordinatesBreadth(EnemyTank, int(GAME_FIELD[2]/2),int(GAME_FIELD[3]/2), everyPixel=4)
    while True:
        first = getAverageCoordinatesBreadth(MyTank, first[0], first[1], everyPixel=4)
        second = getAverageCoordinatesBreadth(EnemyTank, second[0], second[1], everyPixel=4)

        m = (first[1] - second[1]) / (first[0] - second[0])
        b = -1* (m * first[0] - first[1])

        radia = round(abs(first[0] - second[0]) / RADIUS,3)

        drawInformation(radia)
        drawLine(m,b,first,second)

if __name__ == "__main__":
    main()