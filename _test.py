def modTest(c,d,n):
    normalExp = c**d
    normalResult = normalExp % n
    
    expHeight = 5
    modErgebnis = 1
    while d >= 5:
        modErgebnis *= c ** expHeight
        d -= expHeight
        
    modErgebnis *= c ** d
    optErgebnis = modErgebnis % d
    
    return ((normalExp, normalResult),(optErgebnis))

ergebnis = 1
for i in range(0,51):
    ergebnis *= (5**4) % 207
ergebnis *= (5**3) % 207
    
print(ergebnis % 207)