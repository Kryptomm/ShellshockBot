from globals import WEPS

WEAPON_FIELD = [713,1038,950,1064]
WEAPONPIXELS = []

def loadWeaponPixels():
    print("----------------------------------------------------------------")
    print("lade Waffen-Trainings-Daten")
    print("----------------------------------------------------------------")
    file1 = open('data/WeaponPixels.txt', 'r')
    Lines = file1.readlines()

    count = 0
    for line in Lines:
        count += 1
        txt = "{}".format(line.strip())
        d = txt.split(" ")
        for i in range(2,len(d)):
            d[i] = int(d[i])
        WEAPONPIXELS.append([d[2:], d[0].replace("#"," "), int(d[1])])
        if count % 10 == 0: print(f"WAFFEN | {count} von {len(Lines)} geladen")
        
if __name__ == "__main__":
    loadWeaponPixels()
    onlyNames = [x[1] for x in WEAPONPIXELS]
    print(onlyNames)
    
    print(set(["hi", "hi"]))