import pygame
import random
import sys

# ════════════════════════════════════════════════
#  EINSTELLUNGEN
# ════════════════════════════════════════════════
BREITE      = 400
HOEHE       = 400
FELDER      = 20
FELDGR      = BREITE // FELDER

SCHWARZ     = (13, 17, 23)
DUNKEL      = (22, 27, 34)
GITTER_F    = (30, 36, 44)
GRUEN       = (57, 211, 83)
GRUEN_KOPF  = (80, 230, 100)
ROT         = (248, 81, 73)
WEISS       = (230, 237, 243)
GRAU        = (139, 148, 158)

FPS_START   = 8


# ════════════════════════════════════════════════
#  HILFSFUNKTIONEN
# ════════════════════════════════════════════════
def apfel_platzieren(schlange):
    while True:
        pos = (random.randint(0, FELDER - 1),
               random.randint(0, FELDER - 1))
        if pos not in schlange:
            return pos


def zeichne_feld(flaeche, schlange, apfel):
    flaeche.fill(DUNKEL)

    # Gitter
    for i in range(FELDER):
        pygame.draw.line(flaeche, GITTER_F, (i * FELDGR, 0), (i * FELDGR, HOEHE))
        pygame.draw.line(flaeche, GITTER_F, (0, i * FELDGR), (BREITE, i * FELDGR))

    # Schlange
    for index, (gx, gy) in enumerate(schlange):
        farbe = GRUEN_KOPF if index == 0 else GRUEN
        if index > 0:
            faktor = max(0.4, 1 - index * 0.04)
            farbe = tuple(int(c * faktor) for c in GRUEN)

        rect = pygame.Rect(gx * FELDGR + 1, gy * FELDGR + 1,
                           FELDGR - 2, FELDGR - 2)
        pygame.draw.rect(flaeche, farbe, rect, border_radius=4)

    # Apfel
    mx = apfel[0] * FELDGR + FELDGR // 2
    my = apfel[1] * FELDGR + FELDGR // 2
    pygame.draw.circle(flaeche, ROT, (mx, my), FELDGR // 2 - 2)
    pygame.draw.line(flaeche, GRAU,
                     (mx, my - FELDGR // 2 + 3),
                     (mx + 3, my - FELDGR // 2 - 1), 2)


# ════════════════════════════════════════════════
#  HAUPTPROGRAMM
# ════════════════════════════════════════════════
def main():
    pygame.init()
    flaeche = pygame.display.set_mode((BREITE, HOEHE + 40))
    pygame.display.set_caption("🐍 Snake")
    uhr = pygame.time.Clock()

    schrift_gross  = pygame.font.SysFont("Courier New", 48, bold=True)
    schrift_mittel = pygame.font.SysFont("Courier New", 28, bold=True)
    schrift_klein  = pygame.font.SysFont("Courier New", 18)

    highscore = 0

    # ── SPIELFUNKTION ──
    def spiel_loop():
        nonlocal highscore

        schlange = [(10, 10), (9, 10), (8, 10)]
        richtung = (1, 0)
        naechste = (1, 0)
        apfel = apfel_platzieren(schlange)
        punkte = 0
        level = 1
        fps = FPS_START
        pausiert = False

        while True:
            uhr.tick(fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        pausiert = not pausiert

                    if event.key == pygame.K_w and richtung != (0, 1):
                        naechste = (0, -1)
                    if event.key == pygame.K_s and richtung != (0, -1):
                        naechste = (0, 1)
                    if event.key == pygame.K_a and richtung != (1, 0):
                        naechste = (-1, 0)
                    if event.key == pygame.K_d and richtung != (-1, 0):
                        naechste = (1, 0)

            if pausiert:
                pause_text = schrift_mittel.render("PAUSE (P = weiter)", True, WEISS)
                flaeche.blit(pause_text, pause_text.get_rect(center=(BREITE//2, HOEHE//2)))
                pygame.display.flip()
                continue

            richtung = naechste

            kopf = (schlange[0][0] + richtung[0],
                    schlange[0][1] + richtung[1])

            if not (0 <= kopf[0] < FELDER and 0 <= kopf[1] < FELDER):
                return punkte

            if kopf in schlange:
                return punkte

            schlange.insert(0, kopf)

            if kopf == apfel:
                punkte += 1
                if punkte > highscore:
                    highscore = punkte
                apfel = apfel_platzieren(schlange)
                level = punkte // 5 + 1
                fps = min(FPS_START + (level - 1) * 2, 20)
            else:
                schlange.pop()

            zeichne_feld(flaeche, schlange, apfel)

            status_rect = pygame.Rect(0, HOEHE, BREITE, 40)
            pygame.draw.rect(flaeche, SCHWARZ, status_rect)

            p_text = schrift_klein.render(f"Punkte: {punkte}", True, GRUEN)
            h_text = schrift_klein.render(f"Highscore: {highscore}", True, GRUEN)
            l_text = schrift_klein.render(f"Level: {level}", True, GRAU)

            flaeche.blit(p_text, (10, HOEHE + 12))
            flaeche.blit(l_text, (BREITE//2 - l_text.get_width()//2, HOEHE + 12))
            flaeche.blit(h_text, (BREITE - h_text.get_width() - 10, HOEHE + 12))

            pygame.display.flip()

    # ── HAUPTSCHLEIFE ──
    while True:
        flaeche.fill(SCHWARZ)

        t1 = schrift_gross.render("SNAKE", True, GRUEN)
        t2 = schrift_klein.render("Drücke LEERTASTE zum Starten", True, GRAU)
        t3 = schrift_klein.render("W A S D = Richtung   P = Pause", True, GRAU)

        flaeche.blit(t1, t1.get_rect(center=(BREITE//2, 160)))
        flaeche.blit(t2, t2.get_rect(center=(BREITE//2, 240)))
        flaeche.blit(t3, t3.get_rect(center=(BREITE//2, 270)))

        pygame.display.flip()

        warten = True
        while warten:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    warten = False

        endpunkte = spiel_loop()

        flaeche.fill(SCHWARZ)

        t1 = schrift_gross.render("GAME OVER", True, ROT)
        t2 = schrift_mittel.render(f"Punkte: {endpunkte}   Highscore: {highscore}", True, WEISS)
        t3 = schrift_klein.render("LEERTASTE = Nochmal   ESC = Beenden", True, GRAU)

        flaeche.blit(t1, t1.get_rect(center=(BREITE//2, 160)))
        flaeche.blit(t2, t2.get_rect(center=(BREITE//2, 230)))
        flaeche.blit(t3, t3.get_rect(center=(BREITE//2, 290)))

        pygame.display.flip()

        warten = True
        while warten:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        warten = False
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()


if __name__ == "__main__":
    main()
