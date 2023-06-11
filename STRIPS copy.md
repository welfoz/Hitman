# Phase 2 - STRIPS

### Prédicats
- pos_rel(d,x1,y1,x2,y2) : pour la direction d, (x2,y2) est successeur de (x1,y1)
- target(x,y) : position de la cible
- dir_rel(d1,d2) : d2 est successeur de d1 (ex : dir_rel(N,E))
- dir_diff(d1,d2) : d1 /= d2

### Fluents :
- practicable(x,y) : case praticable (tout sauf mur et garde)
- hitman(x,y,d) : position d'Hitman
- guard(x,y,d) : position d'un garde
- civil(x,y,d) : position d'un civil
- rope(x,y) : position de la corde
- costume(x,y) : position du costume
- targetKilled() : la cible est éliminée
- hasCostume() : a le costume
- hasRope() : a la corde
- isDisguised() : est déguisé

### Etat initial : Init(...)
- pos_rel(d,x1,y1,x2,y2) pour toutes les cases de la carte
- dir_rel(N,E), dir_rel(N,W), ...
- dir_diff(N,E), dir_diff(N,W), dir_diff(N,S), ...
- target(x,y) avec x,y position de la cible
- practicable(x,y) pour toutes les cases praticables
- hitman(x,y,d) avec x,y position initiale d'Hitman
- guard(x,y,d) pour tous les gardes
- civil(x,y,d) pour tous les civils
- rope(x,y) avec x,y position de la corde
- costume(x,y) avec x,y position du costume

### Goal : Goal(...)
- targetKilled()
- Hitman(x,y) avec x,y position initiale d'Hitman

## Actions :

### move(d) :
PRECOND : hitman(x,y,d) ^ practicable(x1,y1) ^ pos_rel(d,x,y,x1,y1)

EFFECT : hitman(x1,y1,d) ^ not hitman(x,y,d)

### turn(d1,d2) :
PRECOND : hitman(x,y,d1) ^ dir_rel(d1,d2)

EFFECT : hitman(x,y,d2)

### killTarget() :
PRECOND : hitman(x,y,d) ^ target(x,y) ^ hasRope()

EFFECT : targetKilled()

### neutralizeGuard(d) :
PRECOND : hitman(x,y,d) ^ pos_rel(d,x,y,x1,y1) ^ guard(x1,y1,d1) ^ dir_diff(d,d1) ^ hasRope()

EFFECT : not guard(x1,y1,d1) ^ practicable(x1,y1)

### neutralizeCivil(d) :
PRECOND : hitman(x,y,d) ^ pos_rel(d,x,y,x1,y1) ^ civil(x1,y1,d1) ^ dir_diff(d,d1) ^ hasRope()

EFFECT : not civil(x1,y1,d1)

### takeCostume() :
PRECOND : hitman(x,y,d) ^ costume(x,y)

EFFECT : hasCostume() ^ not costume(x,y)

### putCostume() :
PRECOND : hasCostume()

EFFECT : isDisguised()

### takeRope() :
PRECOND : hitman(x,y,d) ^ rope(x,y)

EFFECT : hasRope() ^ not rope(x,y)