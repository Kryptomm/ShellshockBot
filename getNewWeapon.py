import pytesseract, numpy, cv2, pyautogui, difflib, time
from PIL import Image, ImageEnhance, ImageGrab
pyautogui.FAILSAFE = False

WEPS = {"normal": ["shot", "big shot", "heavy shot", "massive shot", "one-bounce", "three-bounce",
                    "five-bounce", "seven-bounce", "digger", "mega-digger", "grenade", "tri-nade",
                    "multi-nade", "grenade storm", "splitter", "double-splitter", "super-splitter",
                    "breaker", "double-breaker", "super-breaker", "breakerchain", "twinkler", "sparkler",
                    "crackler", "sniper", "sub-sniper", "smart snipe", "cactus", "cactus strike",
                    "bulger", "big bulger", "sinkhole", "area strike", "area attack", "gatling gun",
                    "tunneler", "torpedoes", "tunnel strike", "megatunneler", "horizon", "sweeper",
                    "air strike", "helicopter strike", "ac-130", "artillery", "flower", "bouquet",
                    "banana", "banana split", "banana bunch", "snake", "python", "cobra", "zipper",
                    "double zipper", "zipper quad", "bounsplode", "double-bounsplode", "triple-bounsplode",
                    "dead riser", "pixel", "mega-pixel", "super-pixel", "ultra-pixel",
                    "builder", "megabuilder", "static", "static link", "static chain", "molehill", "moles",
                    "hover-ball", "heavy hover-ball", "rainbow",
                    "megarainbow", "mini-pinger", "pinger", "ping flood", "bolt", "lightning", "2012",
                    "spiker", "super spiker", "disco ball", "groovy ball", "boomerang", "bigboomerang",
                    "mini-v", "flying-v", "yin yang", "yin yang yong", "fireworks", "grand finale",
                    "pyrotechnics", "water balloon", "magnets", "arrow", "bow & arrow", "flaming arrow",
                    "driller", "slammer", "quicksand", "desert", "jumper", "triple-jumper", "spaz",
                    "spazzer", "spaztastic", "pinata", "bounder", "double bounder", "triple bounder",
                    "sticky bomb", "mine layer", "sticky rain", "rain", "hail", "napalm", "heavy napalm",
                    "firestorm", "sunburst", "solar flare",
                    "payload", "magic shower", "shadow", "darkshadow", "deathshadow", "carpet bomb",
                    "carpet fire", "incendiary bombs", "baby seagull", "seagull", "mama seagull",
                    "shrapnel", "shredders", "penetrator", "penetrator v2",
                    "chunklet", "chunker", "bouncy ball", "super ball", "battering ram", "double ram",
                    "ram-squad", "double ram-squad", "asteroids", "spider", "tarantula", "daddy longlegs",
                    "black widow", "clover", "four leaf clover", "3d-bomb", "2x3d", "3x3d", "snowball",
                    "snowstorm", "spotter", "spotter xl", "spotter xxl", "fighter jet", "heavy jet",
                    "bounstrike", "bounstream", "bounstorm", "shooting star", "bee hive", "killer bees",
                    "wasps", "dual-roller", "spreader", "partition", "division", "bfg-1000", "bfg-9000",
                    "train", "express", "mini-turret", "kamikaze", "suicide bomber", "nuke", "meganuke",
                    "black hole", "cosmic rift", "breakermadness", "breakermania", "homing missile",
                    "homing rockets", "puzzler", "deceiver", "baffler", "pentagram", "pentaslam", "radar",
                    "sonar", "lidar", "tweeter", "squawker", "woofer", "acid rain", "acid hail", "sunflower",
                    "helianthus", "sausage", "bratwurst", "kielbasa", "recruiter", "enroller",
                    "enlister", "fury", "rage", "relocator", "displacement bomb", "stone", "boulder", "fireball",
                    "cat", "supercat", "cats and dogs", "asteroid storm",
                    "ghost bomb", "flasher", "strobie", "rave", "sprouter", "blossom", "square", "hexagon",
                    "octagon", "satellite", "ufo", "palm", "double palm", "triple palm", "fountain", 
                    "waterworks", "sprinkler", "flattener", "wall", "fortress", "funnel", "mad birds",
                    "furious birds", "livid birds", "beacon", "beaconator", "chopper", "apache", "skullshot",
                    "skeleton", "pinpoint", "needles", "pins and needles", "god rays", "deity", "hidden blade",
                    "secret blade", "concealed blade", "portal gun", "ashpd", "volcano", "eruption", "throwing star",
                    "multi-star", "ninja", "tangent fire", "tangent attack", "tangent assault", "summoner", "mage",
                    "travelers", "scavengers", "jack-o-lantern", "jack-o-vomit", "wicked witch", "witches broom",
                    "ghouls", "oddball", "oddbomb", "botherer", "tormentor", "punisher", "cropduster", "obnoxiousduster",
                    "toxicduster", "small potion", "medium potion", "large potion", "huge potion", "wanderer",
                    "double wanderer", "triple wanderer", "censorbar", "restrictedbar", "redactedbar",
                    "kiss", "french kiss", "smooch", "confuser", "super-confuser", "mega-confuser"],
        
        "straight": ["glock","m9","desert eagle","moons","orbitals","shank","dagger","sword","uzi","mp5","p90",
                    "rampage","riot","m4","m16","ak-47", "laser beam","great beam","ultra beam","master beam",
                    "early bird","early worm","shockshell","shockshell trio","flintlock","blunderbuss",
                    "fat stacks", "dolla bills", "make-it-rain"],

        "instant": ["earthquake","mega-quake","shockwave","sonic pulse","drone","heavy drone","attractoids",
                    "imploder", "ultimate imploder", "health aura", "health aura+", "health aura++"],

        "45degrees": ["three-ball", "five-ball", "eleven-ball", "twentyfive-ball", "stream", "creek", "river",
                    "tsunami", "flame", "blaze", "inferno", "splitterchain", "rapidfire", "shotgun", "burst-fire",
                    "gattling gun", "guppies", "minnows", "goldfish", "construction", "excavation", "counter 3000",
                    "counter 4000", "counter 5000", "counter 6000", "gravies", "gravits", "tadpoles", "frogs",
                    "bullfrog", "water trio", "water fight", "fiesta", "sticky trio", "fleet", "heavy fleet",
                    "super fleet", "squadron", "sillyballs", "wackyballs", "crazyballs", "synclets", "super-synclets",
                    "x attack", "o attack", "minions", "many-minions", "asteorids", "comets",
                    "starfire", "turretmob", "bumper bombs", "bumper array", "bumper assault", "rocket fire",
                    "rocket cluster", "flurry", "taser", "jackpot", "mega-jackpot", "ultra-jackpot", "lottery",
                    "kittens", "ghostlets", "wacky cluster", "kooky cluster", "crazy cluster", "chicken-fling",
                    "chicken-hurl", "chicken-launch", "pepper", "salt and pepper", "paprika", "cayenne", "needler",
                    "dual needler", "kernels", "popcorn", "burnt popcorn", "skeet", "olympic skeet", "heavy taser",
                    "jammer", "jiver", "rocker", "pongslam", "pyroslam"],

        "deltaAngle": [("roller",-1), ("heavy roller",-1), ("groller",-1), ("back-roller",1),
                    ("heavy back-roller",1), ("back-groller",1), ("saw blade",-2), ("rip saw",-2), ("diamond blade",-2),
                    ("dead weight",2), ("permaroller",-4), ("heavy permaroller",-4), ("ringer",-1), ("heavy ringer",-2), ("olympic ringer",-2)]
        }

WEAPON_FIELD = [713,1038,950,1064]

def makeScreen():
    cap = ImageGrab.grab(bbox = (WEAPON_FIELD[0],WEAPON_FIELD[1],WEAPON_FIELD[2],WEAPON_FIELD[3]))
    filter = ImageEnhance.Color(cap)
    cap = filter.enhance(50)
    enhancer = ImageEnhance.Contrast(cap)
    cap = enhancer.enhance(1)
    
    newCap  = Image.new(mode = "RGB", size = (cap.width, cap.height), color = (0, 0, 0))
    for x in range(cap.width):
        for y in range(cap.height):
            color = cap.getpixel((x, y))
            if color[0] >= 230 and color[1] >= 230 and color[2] >= 230: 
                newCap.putpixel((x,y),(255,255,255))
            else:
                newCap.putpixel((x,y),(0,0,0))
    return newCap

def getName(cap):
    wep_str =  pytesseract.image_to_string(cv2.cvtColor(numpy.array(cap), cv2.COLOR_BGR2GRAY))
    wep_str = wep_str.lower().strip()
    highest_ratio = 0
    current_wep = wep_str
    for wep_cat in WEPS:
        for wep in WEPS[wep_cat]:
            if type(wep) is tuple: wep = wep[0]
            r = difflib.SequenceMatcher(None, wep_str, wep.lower()).ratio()
            if r > highest_ratio:
                highest_ratio = r
                current_wep = wep
    return current_wep

def convertTo1DArray(cap):
    arr = []
    num = 0
    for x in range(cap.width):
        for y in range(cap.height):
            color = cap.getpixel((x, y))
            c = round(0.2989 * color[0] + 0.5870 * color[1] + 0.1140 * color[2])
            if c == 255:
                arr.append(1)
                num += 1
            else: arr.append(0)
    return arr, num

if __name__ == "__main__":
    wait = 3
    time.sleep(wait)
    while True:
        time.sleep(1)

        cap = makeScreen()
        name = getName(cap)
        data, num = convertTo1DArray(cap)
        name = name.replace(" ", "#")

        text = f"{name} {num} "
        for p in data: text += str(p) + " "
        text += "\n"

        with open('WeaponPixels.txt', 'a') as f:
            f.write(text)

        print(name)
        pyautogui.keyDown("w")
        pyautogui.keyUp("w")