from colorama import Fore
from enum import IntEnum

import numpy as np

TANK_OWN = (36, 245, 41)
TANK_ENEMY = (252,42,37)
TANK_MATE = (36,150,186)
GEAR = (253,251,119)
BUMPER = (253,253,253)

__COLOR_MAPPING = {
    (0, 0, 0): Fore.BLACK,
    (128, 0, 0): Fore.RED,
    (0, 128, 0): Fore.GREEN,
    (128, 128, 0): Fore.YELLOW,
    (0, 0, 128): Fore.BLUE,
    (128, 0, 128): Fore.MAGENTA,
    (0, 128, 128): Fore.CYAN,
    (192, 192, 192): Fore.WHITE,
    (128, 128, 128): Fore.LIGHTBLACK_EX,
    (255, 0, 0): Fore.LIGHTRED_EX,
    (0, 255, 0): Fore.LIGHTGREEN_EX,
    (255, 255, 0): Fore.LIGHTYELLOW_EX,
    (0, 0, 255): Fore.LIGHTBLUE_EX,
    (255, 0, 255): Fore.LIGHTMAGENTA_EX,
    (0, 255, 255): Fore.LIGHTCYAN_EX,
    (255, 255, 255): Fore.LIGHTWHITE_EX
}

class GroundColor(IntEnum):
    BLUE = 0
    RED = 1
    GREEN = 2
    GRAY_BLUE = 3
    PURPLE = 4
    YELLOW = 5
    ORANGE = 6
    PINK = 7
    BLUE_PURPLE = 8
    CYAN = 9

    def __str__(self):
        return self.name

__GROUND_MAPPING = {
    # Low grounds
    (75, 164, 232): GroundColor.BLUE,
    (199, 85, 85): GroundColor.RED,
    (62, 156, 57): GroundColor.GREEN,
    (156, 196, 230): GroundColor.GRAY_BLUE,
    (172, 55, 229): GroundColor.PURPLE,
    (187, 160, 33): GroundColor.YELLOW,
    (215, 140, 42): GroundColor.ORANGE,
    (244, 92, 225): GroundColor.PINK,
    (134, 128, 243): GroundColor.BLUE_PURPLE,
    (62, 185, 156): GroundColor.CYAN,
    
    # High Grounds
    (33, 96, 132): GroundColor.BLUE,
    (114, 56, 56): GroundColor.RED,
    (49, 96, 46): GroundColor.GREEN,
    (89, 110, 127): GroundColor.GRAY_BLUE,
    (97, 39, 126): GroundColor.PURPLE,
    (108, 95, 31): GroundColor.YELLOW,
    (120, 81, 33): GroundColor.ORANGE,
    (134, 55, 125): GroundColor.PINK,
    (76, 73, 134): GroundColor.BLUE_PURPLE,
    (45, 107, 93): GroundColor.CYAN
}

def convert_rgb_to_text_color(rgb : tuple[int,int,int]) -> Fore: # type: ignore
    """Converts a color of (r,g,b) to a text color

    Args:
        rgb (_type_): (r,g,b) Values

    Returns:
        colorama.AnsiFore: The closest color to it
    """
    closest_color = min(__COLOR_MAPPING.keys(), key=lambda c: sum(abs(a - b) for a, b in zip(rgb, c)))
    return __COLOR_MAPPING[closest_color]

def convert_rgb_to_ground_color(rgb : tuple[int,int,int]) -> GroundColor:
    closest_color = min(__GROUND_MAPPING.keys(), key=lambda c: sum(abs(a - b) for a, b in zip(rgb, c)))
    return __GROUND_MAPPING[closest_color]

def extract_color_channel(np_image: np.ndarray, channel: GroundColor) -> np.ndarray:
    """
    Extracts the yellow channel from an image using thresholds.

    Args:
        np_image (np.ndarray): An image in RGB format.
        channel (GroundColor): the channel

    Returns:
        np.ndarray: A binary image where the channel color regions are marked.
    """
    if channel == GroundColor.BLUE: return extract_blue_channel(np_image)
    elif channel == GroundColor.RED: return extract_red_channel(np_image)
    elif channel == GroundColor.GREEN: return extract_green_channel(np_image)
    elif channel == GroundColor.YELLOW: return extract_yellow_channel(np_image)
    elif channel == GroundColor.ORANGE: return extract_yellow_channel(np_image)
    
    else: return extract_blue_channel(np_image)

def extract_red_channel(np_image: np.ndarray) -> np.ndarray:
    """
    Extracts the red channel
    """
    red_channel = np_image[:, :, 0]
    return red_channel

def extract_green_channel(np_image: np.ndarray) -> np.ndarray:
    """
    Extracts the green channel from an image using thresholds.
    """
    red_channel = np_image[:, :, 0]
    green_channel = np_image[:, :, 1]
    blue_channel = np_image[:, :, 2]
    
    green_mask = (
        (green_channel >= 128) & 
        (red_channel <= 100) &   
        (blue_channel <= 100) 
    )
    
    # Convert the mask to a uint8 image
    green_channel_extracted = green_mask.astype(np.uint8) * 255
    
    return green_channel_extracted


def extract_blue_channel(np_image: np.ndarray) -> np.ndarray:
    """
    Extracts the blue channel
    """
    blue_channel = np_image[:, :, 2]
    return blue_channel

def extract_yellow_channel(np_image: np.ndarray) -> np.ndarray:
    """
    Extracts the yellow channel from an image using thresholds.
    """
    red_channel = np_image[:, :, 0]
    green_channel = np_image[:, :, 1]
    blue_channel = np_image[:, :, 2]
    
    # Create a binary mask for yellow regions
    yellow_mask = (
        (red_channel >= 128) &
        (green_channel >= 128) &
        (blue_channel <= 100)
    )
    
    # Convert the mask to a uint8 image
    yellow_channel = yellow_mask.astype(np.uint8) * 255
    
    return yellow_channel