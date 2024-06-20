import globals
from PIL import ImageGrab, ImageDraw
from coordinateManager import CoordinateManager, Point

def paintPixels(point : Point, size : int, color : tuple[int,int,int], coordManager : CoordinateManager) -> None:
    if not globals.CREATE_PICTURE: return
    image = globals.CURRENT_PICTURE
    draw = ImageDraw.Draw(image)

    x = coordManager.convertFloatToWidth(point.getX())
    y = coordManager.convertFloatToHeigth(point.getY())
    
    top_left = (x - size, y - size)
    bottom_right = (x + size, y + size)

    draw.ellipse([top_left, bottom_right], outline="white", fill=color)

def saveImage() -> None:
    if not globals.CREATE_PICTURE: return
    image = globals.CURRENT_PICTURE
    image.save(globals.PICTURE_PATH)

def createImage(coordManager : CoordinateManager) -> None:
    if not globals.CREATE_PICTURE: return
    image = ImageGrab.grab(bbox=coordManager.GAME_FIELD.getBoundariesNormalized(coordManager))
    globals.CURRENT_PICTURE = image

if __name__ == "__main__":
    import glob,os
    CM = CoordinateManager()

    png_files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), "*.png"))
    for file_path in png_files:
        os.remove(file_path)
    
    createImage(CM)
    paintPixels(Point(0.5,0.5), 50, (255,255,255), CM)
    saveImage()