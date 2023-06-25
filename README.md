# Installation

Merci de mettre l'éxécutable gophersat dans le dossier ```/gophersat/``` et de vérifier le chemin dans la fonction ```exec_gophersat``` (satUtils.py, l246).
Pensez également à effectuer les commandes suivantes pour initialiser le submodule arbitre_hitman :
```bash
cd arbitre_hitman
git submodule init
git submodule update
```

<br>

# Utilisation

```python
def main():
    referee = HitmanReferee()
    map = phase1(referee)
    phase2(referee, map)
```

<br>

# Modélisation STRIPS

La modélisation est détaillée dans le fichier ```STRIPS.md```

<br>

# Fonctionnement de notre projet


## Modélisation en SAT pour la phase 1

Nous nous sommes basés sur les fonctions uniqueX(), atLeast() et atMost() (satUtils.py, 45:80) vues en TP, en les améliorant.

### Historique des systèmes en SAT réalisés :

1. **modéliser l'ensemble de la carte en SAT et déduire la position des gardes à partir de toutes les informations** : fonctionnel et précis mais le nombre de clauses explose trop rapidement (10 millions pour la carte 6*7), surtout quand le nombre de gardes et de civils augmente.
2. **faire un grand nombre d'appels au solveur pour calculer la probabilité qu'un garde se trouve sur une case** (nombre de solutions avec le garde / grand nombre d'appels au solveur) : impossible d'avoir des déductions cohérentes, le solveur n'est pas fait pour cela.
3. **modéliser à chaque tour uniquement les cases inconnues dans un rayon de 25 cases autour du Hitman (portée de l'écoute) et faire abstraction de la direction des gardes pour savoir si une case est sans danger** : fonctionne bien, en général moins de 1000 clauses, cependant les décisions sont prises sans faire de déductions au delà de la portée de l'écoute. C'est la version actuelle.

<br>

---

<br>

### Modélisation SAT :

Notre modélisation permet de déduire si une case est sans danger.

Types possibles pour une case :
```python
MAP_GUARD_INDEX = {
    'empty': 1,
    'blocking': 2,
    'guard': 3,
    'civil': 4
}
````
La fonction ```is_position_safe_opti()``` utilise la carte connue, la position à tester, la carte des informations entendues, et la carte des informations de is_in_guard_range de l'arbitre.

Elle génère des clauses pour les cases dans un rayon de 2 autour du Hitman :
- extraction de la sous-carte
- génération des clauses des types de case
- générations des clauses liées à l'écoute
- génération des clauses liées à la vision
- génération des clauses liées aux cases connues
- génération des clauses liées aux positions où Hitman à été vu

La fonction ```is_position_safe()``` regarde ensuite si un modèle SAT avec un garde existe pour tous les environs. Si aucun modèle n'existe, la case est sans danger.

Cette modélisation SAT est ensuite utilisée dans la fonction de coût de notre algorithme A* pour choisir la direction à prendre.

### Améliorations possibles :

- prendre en compte toutes les informations d'écoute (actullement la fonction ne génère des clauses qu'avec les cases où aucun garde/civil n'est entendu pour réduire le nombre de clauses)

<br>

---

<br>

## Algorithme A* pour la phase 1 :

Nous utilisons un algorithme A* pour déterminer la route à prendre dans la phase 1. Cette algorithme utilise la modélisation SAT dans son calcul du coût des chemins, uniquement au niveau 1 de l'arbre.

Il calcule le chemin de coût minimal pour visiter toutes les cases encore inconnues. Ce calcul est fait à nouveau à chaque action de Hitman, et difficile à cause des parties inconnues.

**Heuristique** :

On utilise la somme entre les distances entre chaque case inconnue, ce qu'on appelle *clustering*. <br>
Plus le nombre de cases inconnues diminue, plus *clustering* diminue.
Plus les cases sont proches les unes des autres et donc plus facile à voir ensemble, plus *clustering* est faible. <br>
Cela permet de récompenser à la fois la diminution du nombre de cases inconnue mais également leur rapprochement.

### Améliorations possibles :
- Améliorer l'heuristique en intégrant la position du Hitman dans l'évaluation
- Recalculer le chemin uniquement lorsque l'on a de nouvelles informations
- Faire un portfolio d'heuristiques, lancer les résolutions en parallèle et prendre la premiere réponse

<br>

---

<br>

## Modélisation STRIPS :

La modélisation est détaillée dans le fichier ```STRIPS.md```

<br>

---

<br>

## Algorithme A* pour la phase 2 :

Nous utilisons le même algorithme que dans la phase 1. Cette fois ci, il calcule le chemin de coût minimal pour aller tuer la cible. Ce parcours est séparé en 4 buts : prendre la corde de piano, aller sur la case de la cible, la tuer, revenir au départ.

**Heuristique** :

Ditance de manhattan, pour trouver le plus court chemin.

### Améliorations possibles :
- Faire un portfolio d'heuristiques, lancer les résolutions en parallèle et prendre la premiere réponse

<br>

# Forces et faiblesses de notre projet

## Forces :

- Déductions SAT si une case est sans danger
- Rapidité du SAT, faible nombre de clauses générées
- Heuristique simple (la distance entre les cases inconnues) mais relativement efficace en phase 1
- Résolution efficace de la phase 2 grâce à l'utilisation de la distance de Manhattan

## Faiblesses :

- Les heuristiques utilisées pourraient surestimer le coût réel
- Déductions SAT limitées autour d'Hitman