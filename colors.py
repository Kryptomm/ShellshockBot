import colorama
from colorama import Fore

FRIENDLY_TANK = (36, 245, 41)
ENEMY_TANK = (253,57,64)
GEAR = (253,251,119)
BUMPER = (253,253,253)

COLOR_MAPPING = {
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

def convert_rgb_to_text_color(rgb : tuple[int,int,int]) -> Fore:
    """Converts a color of (r,g,b) to a text color

    Args:
        rgb (_type_): (r,g,b) Values

    Returns:
        colorama.AnsiFore: The closest color to it
    """
    closest_color = min(COLOR_MAPPING.keys(), key=lambda c: sum(abs(a - b) for a, b in zip(rgb, c)))
    return COLOR_MAPPING[closest_color]