NEV = "asd"
TIPUS = "3D"
LEIRAS = "Saját 3D algoritmus leírása.\nItt módosíthatod, hogy mit csináljon."

def futtat(res_x, res_y, p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    
    # --- ALGORITMUS LOGIKÁJA IDE JÖN ---
    
    yield (x1, y1, (255, 255, 0)) # Sárga pont
    yield (x2, y2, (255, 100, 0)) # Narancs pont
