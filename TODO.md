# TO DO 
### phase 1 todo 
- on est sûr de connaitre la premiere case ? -> tjrs (0, 0)
- comment les infos de l'ouie peuvent nous servir dans le choix du déplacement ? (pour plus tard)
- SAT pour l'ouie @Pol
- utiliser SAT @Fabien

### phase 2 TODO 
- apres opti petit à petit
- neutralize: attention aux points
- TODO: nb de fois vu en train de neutraliser quelqu’un * 100
neutraliser_garde et neutraliser_civil : il faut regarder le garde ou le civil, être sur une case adjacente et qu’il ne vous regarde pas. La corde de piano n’est pas nécessaire. Une fois neutralisée, la personne n’apparaît plus dans les visions et sa case est libérée.

Opti a*: 
- red blob 
- algo zobrist
- utiliser numpy (et non des tableaux) pour optimiser la recherche (pour plus tard)
- typer stateTree

### rapport ? 
- readme

# rules 

1. 1 case contient 1 et 1 seul type, un type est soit: 
    - un garde -> S (security)
    - un invité -> G (guest)
    - un déguisement -> C (costume)
    - une corde -> R (rope)
    - la cible -> T (target)
    - un mur -> W (wall)
    - rien -> E 

2. les gardes et invités regardent dans une direction et une seule direction (est-ce important dans les clauses ??? --> pense pas, c'est à stocker en dehors des clauses juste pour compter les points)

3. il y a X gardes et Y invités

4. il y a 1 cible, 1 déguisement, 1 corde dans la piece 



## Additionnel: 
- hitman porte le déguisement ou pas (utile pour les points, qd il passe dessus il le prend)
- hitman a la corde ou pas (qd il passe dessus il la prend)
- hitman voit entre 1 et 3 cases (max) devant lui, sa vision s'arrête au premier obstacle
- hitman entend, autour de lui. Il sait le nb X de gardes et d'invités autour de lui. Donc il sait aussi X - 9 non gardes et non invités.
S'il voit un garde ou un invité devant lui, X - 1 gardes et invités restants autour de lui et 9 - (X - 1) non gardes et non invités restants autour de lui. 
- si hitman est sur la meme case qu'un civil, il est caché par le civil
- on ne peut pas avancer sur un garde
- on peut etre sur la meme case qu'un invité en disant "pardon"
- on ne peut pas avancer sur un mur
- la case de départ est forcement une bordure
- quand on voit une bordure -> en déduire des clauses (on en déduit des clauses ou plutot des infos qui servent pour le déplacement ?) 
- à partir de 5 (gardes + invités) autour de nous on en entend 5+
- La distance d'audition va passer à 2 au lieu de 1.


### Notes
- le choix du déplacement + la phase 2 de recherche des états est à faire en python
- ca doit tourner en salle de TP 

### Questionnements ???
- est-ce qu'on enlève des clauses au fur et à mesure pour soulager le prg ?? (à voir si on veut optimiser le temps de calcul ou pas)


<br>

### actions 
1 action: 
- tourner horaire 90°
- tourner antihoraire 90°
- avancer d’une case (dans le sens où on est tourné)

résultat de l'action, nouvelles informations: 
- position et type du premier objet/personne en face de vous (dépendant de votre orientation)
- nb de personnes entendues

<br>

# code structure 
- taille de la map n * m (ligne * colonne)
- position des cases (ligne, colonne)
- type de la case (S, G, C, R, T, W, E)

    ```python 
    # init map 4 * 5, init with -1 as we don't know what's in the map yet
    certaintyMap =  [
        [-1, -1, -1, -1],
        [-1, -1, -1, -1],
        [-1, -1, -1, -1],
        [-1, -1, -1, -1],
        [-1, -1, -1, -1]
    ]

    certaintyMap =  [
        [E, C, -1, -1],
        [-1, -1, -1, -1],
        [-1, T, -1, -1],
        [-1, -1, -1, -1],
        [-1, -1, -1, -1]
    ]

    ```

    -> end of the phase 1 when we have 1 C, 1 T, 1 R, X S, Y G and no -1 in the map

# déroulement Phase 1

- prise en entrée du programme la map 
- déduction n et m
- tq la map qu'il y a des -1 dans notre map (que la solution du SAT n'est pas unique)--> faire
    - action 
    - si on est dans le champ de vision d'un garde --> +1
    - mettre à jour la map avec les cases découvertes
    - ajout nouvelles clauses grâces aux cases découvertes 

comptage des points 

# nombre de clauses SAT :
Paramètres :
n_col colonnes et n_lig lignes
n_gar gardes et n_civ civils

- règle 1 (options possibles pour une case) : n_col * n_lig * 7
    - 1 : vide
    - 2 : mur
    - 3 : garde
    - 4 : civil
    - 5 : cible
    - 6 : corde
    - 7 : costume

- règle 2 (contraintes sur le nombre de gardes) : n_gar parmi (n_col * n_lig)

- règle 3 (contraintes sur le nombre de civils) : n_civ parmi (n_col * n_lig)

...

# Choix de l'action
Garder à l'esprit que le but est de connaître toutes les cases en un minimum d'actions

3 choix possibles: 
- avancer
- tourner 90
- tourner -90

Afin de faire le meilleur choix, pour chaque choix on va calculer le meilleur choix à faire (ou éviter le pire).
Le plus de tour d'avancer on calculera le meilleur nos choix seront.

Données pour calculer le meilleur choix: 
- notre position
- dans quelle direction on regarde
- la map (avec les cases qu'on connait déjà, et celles où on a des déductions (grâce à l'ouie))

Pour chaque action possible: 
    - calculer à quel point elle va nous apporter de l'information
Choisir l'action qui apporte le plus de points d'informations

Si on regarde en face d'un mur ou d'une bordure:
- avancer: 0 pts
- tourner: X pts

Pour chaque nouvelle case potentiellement vue: Y pts

Optimisation choix du déplacement:
--> Faire une sorte de minimax avec profondeur limitée, et évaluation function 
--> optimisation: alpha beta pruning
--> evaluation function --> minimize the number of unknown cases

