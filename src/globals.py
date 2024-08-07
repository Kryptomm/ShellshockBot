import sys
from random import randint

#Setting Variables
DEBUG = True
CREATE_PICTURE = False
ID = "VIZU_PIC" #randint(0,sys.maxsize)
PICTURE_PATH = f"{ID}.png"
CURRENT_PICTURE = None

#Definitions
WEPS = {"normal": ["shot", "big shot", "heavy shot", "massive shot", "one-bounce", "three-bounce", "five-bounce", "seven-bounce", "digger", "mega-digger",   
                    "breaker", "double-breaker", "super-breaker", "breakerchain", "twinkler", "sparkler", "crackler", "sniper", "sub-sniper", "smart snipe",
                    "cactus", "bulger", "big bulger", "sinkhole", "area strike", "area attack", "gatling gun", "tunneler", "torpedoes", "tunnel strike",
                    "megatunneler", "horizon", "sweeper", "flower", "bouquet", "banana", "banana split", "banana bunch", "snake", "python",
                    "cobra", "zipper", "double zipper", "zipper quad", "dead riser", "pixel", "mega-pixel", "super-pixel", "ultra-pixel", "builder",
                    "megabuilder", "static", "static link", "static chain", "molehill", "moles", "rainbow", "megarainbow", "mini-pinger", "pinger",
                    "ping flood", "bolt", "lightning", "2012", "spiker", "super spiker", "boomerang", "bigboomerang", "mini-v", "flying-v",
                    "yin yang", "yin yang yong", "fireworks", "grand finale", "pyrotechnics", "water balloon", "magnets", "arrow", "bow & arrow", "flaming arrow",
                    "driller", "slammer", "quicksand", "desert", "jumper", "triple-jumper", "spaz", "spazzer", "spaztastic", "bounder",
                    "double bounder", "triple bounder", "sticky bomb", "mine layer", "napalm", "heavy napalm", "sunburst", "solar flare", "payload", "magic shower",
                    "shadow", "darkshadow", "deathshadow", "baby seagull", "seagull", "mama seagull", "penetrator", "penetrator v2", "chunklet", "chunker",
                    "bouncy ball", "super ball", "battering ram", "double ram", "ram-squad", "double ram-squad", "asteroids", "spider", "tarantula", "daddy longlegs",
                    "black widow", "clover", "four leaf clover", "snowball", "spotter", "spotter xl", "spotter xxl", "fighter jet", "heavy jet", "bee hive",
                    "killer bees", "wasps", "dual-roller", "partition", "division", "mini-turret", "nuke", "meganuke",
                    "black hole", "cosmic rift", "breakermadness", "breakermania", "homing missile", "homing rockets", "puzzler", "deceiver", "baffler", "pentagram",
                    "pentaslam", "radar", "sonar", "lidar", "tweeter", "squawker", "woofer", "sunflower", "helianthus", "sausage",
                    "bratwurst", "kielbasa", "fury", "rage", "relocator", "displacement bomb", "stone", "boulder", "fireball", "cat",
                    "supercat", "cats and dogs", "asteroid storm", "ghost bomb", "flasher", "strobie", "rave", "sprouter", "blossom", "square",
                    "hexagon", "octagon", "satellite", "ufo", "palm", "double palm", "triple palm", "fountain", "waterworks", "sprinkler",
                    "flattener", "wall", "fortress", "funnel", "mad birds", "furious birds", "livid birds", "beacon", "beaconator", "skullshot", "skeleton", "hidden blade", "secret blade",
                    "concealed blade", "portal gun", "ashpd", "volcano", "eruption", "tangent fire", "tangent attack", "tangent assault", "summoner", "mage",
                    "travelers", "scavengers", "wicked witch", "witches broom", "ghouls", "oddball", "oddbomb", "botherer", "tormentor", "punisher",
                    "cropduster", "obnoxiousduster", "toxicduster", "small potion", "medium potion", "large potion", "huge potion", "wanderer", "double wanderer", "triple wanderer",
                    "censorbar", "restrictedbar", "redactedbar", "kiss", "french kiss", "smooch", "confuser", "super-confuser", "mega-confuser",
                    "roller", "heavy roller", "groller", "back-roller", "heavy back-roller", "back-groller", "saw blade", "rip saw", "diamond blade", "dead weight"
                    ,"permaroller", "heavy permaroller", "train", "express", "throwing star", "multi-star", "ninja", "hover-ball", "heavy hover-ball"],
        
        "straight": ["glock", "m9", "desert eagle", "moons", "orbitals", "shank", "dagger", "sword", "uzi", "mp5", "p90", "rampage", "riot", "m4", "m16",
                    "ak-47", "laser beam", "great beam", "ultra beam", "master beam", "shockshell", "shockshell trio", "flintlock", "blunderbuss", "fat stacks", "dolla bills", "make-it-rain"],

        "instant": ["earthquake", "mega-quake", "shockwave", "sonic pulse", "drone", "heavy drone", "attractoids", "imploder", "ultimate imploder", "health aura", "health aura+", "health aura++"],

        "45degrees": ["three-ball", "five-ball", "eleven-ball", "twentyfive-ball", "stream", "creek", "river", "tsunami", "flame", "blaze",
                    "inferno", "splitterchain", "rapidfire", "shotgun", "burst-fire", "gattling gun", "guppies", "minnows", "goldfish", "construction",
                    "excavation", "counter 3000", "counter 4000", "counter 5000", "counter 6000", "gravies", "gravits", "tadpoles", "frogs", "bullfrog",
                    "water trio", "water fight", "fiesta", "sticky trio", "fleet", "heavy fleet", "super fleet", "squadron", "sillyballs", "wackyballs",
                    "crazyballs", "synclets", "super-synclets", "x attack", "o attack", "minions", "many-minions", "asteorids", "comets", "starfire",
                    "turretmob", "bumper bombs", "bumper array", "bumper assault", "rocket fire", "rocket cluster", "flurry", "taser", "jackpot", "mega-jackpot",
                    "ultra-jackpot", "lottery", "kittens", "ghostlets", "wacky cluster", "kooky cluster", "crazy cluster", "chicken-fling", "chicken-hurl", "chicken-launch",
                    "pepper", "salt and pepper", "paprika", "cayenne", "needler", "dual needler", "kernels", "popcorn", "burnt popcorn", "skeet",
                    "olympic skeet", "heavy taser", "jammer", "jiver", "rocker", "bounsplode", "double-bounsplode", "triple-bounsplode", "pongslam", "pyroslam",
                    "splitter", "double-splitter", "super-splitter"],

        "deltaAngle": [("ringer",1), ("heavy ringer",3), ("olympic ringer",2)],

        "radius": [("3d-bomb",33), ("2x3d",33), ("3x3d",33), ("early bird",100), ("early worm",67)],

        "landing": ["grenade", "tri-nade", "multi-nade", "grenade storm", "cactus strike", "air strike", "helicopter strike", "ac-130", "artillery", "disco ball",
                    "groovy ball", "pinata", "sticky rain", "rain", "hail", "carpet bomb", "carpet fire", "incendiary bombs", "shrapnel", "shredders",
                    "bounstrike", "bounstream", "bounstorm", "jack-o-lantern", "jack-o-vomit", "recruiter", "enroller", "enlister", "pinpoint", "needles",
                    "pins and needles", "god rays", "deity", "spreader", "kamikaze", "suicide bomber", "acid rain", "acid hail", "shooting star", "snowstorm", "firestorm"],
        
        "extraWind": [("bfg-1000", 2), ("bfg-9000", 2), ("chopper", 2), ("apache", 2)]
        }

RULES = """
        ~~~DAS IST EIN FARMBOT FÜR XP~~~
            UMGEBUNG:
                -Fenster: Vollbild
                -Auflösung: Alle 16:9 Auflösungen werden unterstützt
            SPIEL-REGELN:
                -Map-Color: Yellow, andere Farben machen es etwas kaputt, funktioniert dennoch
                -Map-Mode: Generated  / Secure: Eine Flache Map
                -Mode: Deathmatch
                -Players: Egal
                -Wind: Low-High, Recommended: High
                -Shot-Type: Alles möglich
                -Mod: Recommended: One-Wep
                -Obstacles: Recommended: Med, Secure: Low (Less XP)
            Aktiviere den Bot in der Lobby und sei nicht bereit!
        """


def __get_argument_value(arg_name):
    """Retrieve the value of the command-line argument with the specified name."""
    for i, arg in enumerate(sys.argv):
        if arg == arg_name and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None

def initializeGlobals() -> None:
    """Initialzes globals to standart values or through given things from command line
    """    
    global DEBUG
    global CREATE_PICTURE
    
    debug = bool(__get_argument_value("--debug"))
    picture = __get_argument_value("--picture")
    
    if debug and type(debug) == bool:
        DEBUG = True
        
    if picture and type(picture) == bool:
        CREATE_PICTURE = True
        
    print(f"{DEBUG=}\n{CREATE_PICTURE=}\n{ID=}")