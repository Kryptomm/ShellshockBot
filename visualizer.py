from PIL import ImageGrab, ImageDraw
from coordinateManager import CoordinateManager

def drawCirclesAroundPixels(points : list[tuple[int,int]], size : int, colors : list[tuple[int,int]], coordManager : CoordinateManager, path : str) -> None:
    image = ImageGrab.grab(bbox = (0,0,coordManager.getScreenWidth(),coordManager.getScreenHeigth()))
    draw = ImageDraw.Draw(image)

    index = 0
    for px,py in points:
        # Define the coordinates of the square
        top_left = (px - size, py - size)
        bottom_right = (px + size, py + size)

        # Draw the red square
        draw.ellipse([top_left, bottom_right], outline="white", fill=colors[index])
        index += 1
    
    if path:
        image.save(path)
    else:
        image.show()
    
if __name__ == "__main__":
    CM = CoordinateManager()
    drawCirclesAroundPixels(500,500,15, CM , "Z_Bild.png")