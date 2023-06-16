# SAT super opti:

à chaque tour generer les clauses de 0:

1. de notre position actuelle définir la sous-map et notre position relative à cette sous-map correspondant à notre zone d'écoute (reprendre une partie du code de addInfoListening)

2. générer clauses initiales sur cette sous-map (fonction generateInitialClauses) avec
    - n_col et n_lig = dimensions de la sous map
    - n_guards = status["hear"]
    - n_civils = status["hear"]
    -> faire gaffe: on veut pas que les clauses disent qu'il y a n_guards ET n_civils dans la sous-map, mais OU

3. parcourir la sous-map, quand on connait la valeur d'une case => l'ajouter aux clauses en la traduisant avec MAP_GUARD_INDEX 

4. appeller is_position_safe avec n_col et n_lig de la sous-map, known_map = sous_map, position = position relative à la sous-map (et non dans la map globale sinon ca va crash)

5. finito
