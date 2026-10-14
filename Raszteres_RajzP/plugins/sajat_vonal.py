NEV = "sajat_vonal"
TIPUS = "2D"
LEIRAS = "Saját 2D algoritmus leírása.\nItt módosíthatod, hogy mit csináljon."

def futtat(res_x, res_y, p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    szin = (0, 255, 0) # (R, G, B) formátum: Zöld szín

    # Ha vízszintes a vonal (az Y koordináta megegyezik)
    if y1 == y2:
        # Végigmegyünk a kisebbik X-től a nagyobbik X-ig
        for x in range(min(x1, x2), max(x1, x2) + 1):
            yield (x, y1, szin)
            
    # Ha függőleges a vonal (az X koordináta megegyezik)
    elif x1 == x2:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            yield (x1, y, szin)
            
    # Ha átlósan kattintottál, csak lerak két piros pontot hibajelzésként
    else:
        yield (x1, y1, (255, 0, 0))
        yield (x2, y2, (255, 0, 0))