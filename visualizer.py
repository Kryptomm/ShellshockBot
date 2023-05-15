from PIL import ImageGrab, ImageDraw
from coordinateManager import CoordinateManager

def drawSquareAroundPixel(px : int, py : int, size : int, coordManager : CoordinateManager ,path : str) -> None:
    image = ImageGrab.grab(bbox = (0,0,coordManager.getScreenWidth(),coordManager.getScreenHeigth()))
    
    draw = ImageDraw.Draw(image)

    # Define the coordinates of the square
    top_left = (px - size, py - size)
    bottom_right = (px + size, py + size)

    # Draw the red square
    draw.ellipse([top_left, bottom_right], outline="red", fill="white")
    
    if path:
        image.save(path)
    
if __name__ == "__main__":
    CM = CoordinateManager()
    drawSquareAroundPixel(500,500,15, CM , "Z_Bild.png")