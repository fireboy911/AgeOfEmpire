import curses
import time

# Configuration de la grille
TAILLE_GRILLE_X = 50
TAILLE_GRILLE_Y = 50
TROUPE = "T"  # Représentation de la troupe
FACTEUR_X=2
# Initialisation de l'écran
def initialiser_ecran(stdscr):
    # Désactive le curseur et le mode de saisie immédiate
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)  # Temps d'attente entre chaque boucle (en millisecondes)

# Initialiser les couleurs
    curses.start_color()  # Démarrer le module de couleurs
    curses.use_default_colors()  # <- clé pour enlever le fond noir
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)    # Troupe : rouge sur fond noir
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Terrain : vert sur fond noir

# Fonction pour afficher la grille
def afficher_grille(stdscr, troupes):
    stdscr.clear()  # Effacer l'écran avant de redessiner

    

    # Affichage de la grille
    for y in range(TAILLE_GRILLE_Y):
        for x in range(TAILLE_GRILLE_X):
            # Vérifier si une troupe est présente sur cette case
            found = False
            for troupe in troupes:
                if troupe["x"] == x and troupe["y"] == y:
                    stdscr.addstr(y, x*FACTEUR_X, TROUPE, curses.color_pair(1))  # Placer la troupe
                    found = True
                    break
            if not found:
                stdscr.addstr(y, x*FACTEUR_X, ".", curses.color_pair(2))  # Terrain vide

    # Rafraîchir l'écran
    stdscr.refresh()

# Fonction pour vérifier si une case est occupée par une autre troupe
def case_occupee(troupes, x, y):
    for troupe in troupes:
        if troupe["x"] == x and troupe["y"] == y:
            return True
    return False
# Fonction pour gérer les mouvements des troupes
def mouvement(troupes, key):
    for troupe in troupes:
        new_x, new_y = troupe["x"], troupe["y"]

        if key == curses.KEY_UP and troupe["y"] > 0:  # Déplacer vers le haut
            new_y -= 1
        elif key == curses.KEY_DOWN and troupe["y"] < TAILLE_GRILLE_Y - 1:  # Déplacer vers le bas
            new_y += 1
        elif key == curses.KEY_LEFT and troupe["x"] > 0:  # Déplacer vers la gauche
            new_x -= 1
        elif key == curses.KEY_RIGHT and troupe["x"] < TAILLE_GRILLE_X - 1:  # Déplacer vers la droite
            new_x += 1
 # Si la case cible est libre, on déplace la troupe
        if not case_occupee(troupes, new_x, new_y):
            troupe["x"] = new_x
            troupe["y"] = new_y

# Fonction principale du jeu
def jeu(stdscr):
    initialiser_ecran(stdscr)

    # Initialiser plusieurs troupes
    troupes = [
        {"x": TAILLE_GRILLE_X // 4, "y": TAILLE_GRILLE_Y // 4},  # Troupe 1
        {"x": TAILLE_GRILLE_X // 2, "y": TAILLE_GRILLE_Y // 2},  # Troupe 2
        {"x": 3 * TAILLE_GRILLE_X // 4, "y": 3 * TAILLE_GRILLE_Y // 4},  # Troupe 3
    ]
    
    while True:
        afficher_grille(stdscr, troupes)

        # Capturer l'entrée utilisateur
        key = stdscr.getch()

        if key == 27:  # Si l'utilisateur appuie sur 'Esc', quitter le jeu
            break

        mouvement(troupes, key)  # Met à jour la position des troupes

        time.sleep(0.1)

# Lancer le jeu avec curses.wrapper qui gère l'initialisation et la fermeture proprement
if __name__ == "__main__":
    curses.wrapper(jeu)
