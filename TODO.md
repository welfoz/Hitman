# TO DO 
- coder les règles une par une et vérifier qu'elles fonctionnent


# rules 

1. 1 case contient 1 et 1 seul truc (reprendre sudoku)

2. les gardes et invités regardent dans une direction et une seule direction (est-ce important dans les clauses ??? --> pense pas, c'est à stocker en dehors des clauses juste pour compter les points)

3. il y a X gardes et Y invités

4. il y a 1 cible, 1 déguisement, 1 corde dans la piece 

5. un truc est soit: 
    - un garde -> S (security)
    - un invité -> G (guest)
    - un déguisement -> C (costume)
    - une corde -> R (rope)
    - la cible -> T (target)
    - un mur -> W (wall)
    - rien -> E (est-ce important de coder le vide ? du moment que si c'est pas un truc, c'est vide -> allège un peu les clauses non ? jsp)


## Additionnel: 
- hitman porte le déguisement ou pas (utile pour les points, qd il passe dessus il le prend)
- hitman a la corde ou pas (qd il passe dessus il la prend)
- hitman voit entre 1 et 3 cases (max) devant lui, sa vision s'arrête au premier obstacle
- hitman entend, autour de lui. Il sait le nb X de gardes et d'invités autour de lui. Donc il sait aussi X - 9 non gardes et non invités.
S'il voit un garde ou un invité devant lui, X - 1 gardes et invités restants autour de lui et 9 - (X - 1) non gardes et non invités restants autour de lui. 

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
-> Toutes les fonctions qui génèrent des clauses doivent utiliser les bons littéraux (ex si règle 1 utilise de 1 à 20, règle 2 doit utiliser à partir de 21). On peut passer à ces fonctions le nombre de litéraux déjà utilisés et qu'elles retourne un couple (BaseClauses, NouveauxNombreLitteraux).

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