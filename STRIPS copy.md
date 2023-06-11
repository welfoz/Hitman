# Phase 2 - STRIPS

### Prédicats
- pos_rel(d,x1,y1,x2,y2) : pour la direction d, (x2,y2) est successeur de (x1,y1)
- target(x,y) : position de la cible
- dir_rel(d1,d2) : d2 est successeur de d1 (ex : dir_rel(N,E))
- dir_diff(d1,d2) : d1 /= d2

### Fluents :
- clear(x,y) : case vide
- hitman(x,y,d) : position d'Hitman
- guard(x,y,d) : position d'un garde
- civil(x,y,d) : position d'un civil
- rope(x,y) : position de la corde
- costume(x,y) : position du costume
- targetKilled() : la cible est éliminée
- hasCostume() : a le costume
- hasRope() : a la corde
- isDisguised() : est déguisé
- isNotWithCivil() : n'est pas sur la même case qu'un civil

### Etat initial : Init(...)
- pos_rel(d,x1,y1,x2,y2) pour toutes les cases de la carte
- dir_rel(N,E), dir_rel(N,W), ...
- dir_diff(N,E), dir_diff(N,W), dir_diff(N,S), ...
- target(x,y) avec x,y position de la cible
- clear(x,y) pour toutes les cases vides
- hitman(x,y,d) avec x,y position initiale d'Hitman
- guard(x,y,d) pour tous les gardes
- civil(x,y,d) pour tous les civils
- rope(x,y) avec x,y position de la corde
- costume(x,y) avec x,y position du costume

### Goal : Goal(...)
- targetKilled()
- Hitman(x,y) avec c,y position initiale d'Hitman

### Actions :

#### move(d) :
PRECOND : hitman(x,y,d) ^ clear(x1,y1) ^ pos_rel(d,x,y,x1,y1) ^ isNotWithCivil()
EFFECT : hitman(x1,y1,d) ^ not hitman(x,y,d) ^ clear(x,y) ^ not clear(x1,y1)

#### moveThroughCivil(d) :
PRECOND : hitman(x,y,d) ^ civil(x1,y1,d) ^ pos_rel(d,x,y,x1,y1)
EFFECT : hitman(x1,y1,d) ^ not hitman(x,y,d) ^ clear(x,y) ^ isWithCivil()

#### moveFromCivil(d) : 
PRECOND : hitman(x,y,d) ^ clear(x1,y1) ^ pos_rel(d,x,y,x1,y1) ^ civil(x,y,d1)
EFFECT : hitman(x1,y1,d) ^ not hitman(x,y,d) ^ not isWithCivil() ^ not clear(x1,y1)

// idée : mettre clear() sur les civils, target, costume et rope pour pouvoir se déplacer dessus

#### turn(d1,d2) :
PRECOND : hitman(x,y,d1) ^ dir_rel(d1,d2)
EFFECT : hitman(x,y,d2)

#### killTarget() :
PRECOND : hitman(x,y) ^ target(x,y) ^ hasRope()
EFFECT : targetKilled()

#### neutralizeGuard(d) :
PRECOND : hitman(x,y,d) ^ pos_rel(d,x,y,x1,y1) ^ guard(x1,y1,d1) ^ dir_diff(d,d1) ^ hasRope()
EFFECT : not guard(x1,y1,d1) ^ clear(x1,y1)

#### neutralizeCivil(d) :
PRECOND : hitman(x,y,d) ^ pos_rel(d,x,y,x1,y1) ^ civil(x1,y1,d1) ^ dir_diff(d,d1) ^ hasRope()
EFFECT : not civil(x1,y1,d1) ^ clear(x1,y1)

#### takeCostume() :
PRECOND : hitman(x,y,d) ^ costume(x,y)
EFFECT : hasCostume() ^ not costume(x,y)

#### putCostume() :
PRECOND : hasCostume()
EFFECT : isDisguised()

#### takeRope() :
PRECOND : hitman(x,y,d) ^ rope(x,y)
EFFECT : 

- TakeCostume(H, C)
- PutCostume(H)
- TakeRope(H, R)

### Code : MoveN(H)
PRECOND : Hitman(H), LooksN(H), In(H, x, y), Clear(x, y+1)

EFFECT : In(H, x, y+1), not In(H, x, y)

### Code : MoveE(H)
PRECOND : Hitman(H), LooksE(H), In(H, x, y), Clear(x+1, y)

EFFECT : In(H, x+1, y), not In(H, x, y)

### Code : MoveW(H)
PRECOND : Hitman(H), LooksE(H), In(H, x, y), Clear(x-1, y)

EFFECT : In(H, x-1, y), not In(H, x, y)

### Code : MoveS(H)
PRECOND : Hitman(H), LooksN(H), In(H, x, y), Clear(x, y-1)

EFFECT : In(H, x, y-1), not In(H, x, y)

### Code : TurnNToW(H)
PRECOND : Hitman(H), LooksN(H)

EFFECT : LooksW(H), not LooksN(H)

### Code : TurnNToE(H)
PRECOND : Hitman(H), LooksN(H)

EFFECT : LooksE(H), not LooksN(H)

### Code : TurnEToN(H)
PRECOND : Hitman(H), LooksE(H)

EFFECT : LooksN(H), not LooksE(H)

### Code : TurnEToS(H)
PRECOND : Hitman(H), LooksE(H)

EFFECT : LooksS(H), not LooksE(H)

### Code : TurnSToE(H)
PRECOND : Hitman(H), LooksS(H)

EFFECT : LooksE(H), not LooksS(H)

### Code : TurnSToW(H)
PRECOND : Hitman(H), LooksS(H)

EFFECT : LooksW(H), not LooksS(H)

### Code : TurnWToS(H)
PRECOND : Hitman(H), LooksW(H)

EFFECT : LooksS(H), not LooksW(H)

### Code : TurnWToN(H)
PRECOND : Hitman(H), LooksW(H)

EFFECT : LooksN(H), not LooksW(H)

### KillTarget(H, T)
PRECOND : Hitman(H), Target(T), HasRope(H), In(H, x, y), In(T, x, y) 

EFFECT : Dead(T)

### NeutralizeGuardN(H, G)
PRECOND : Hitman(H), Guard(G), In(H, x, y), In(G, x, y+1), LooksN(H), not LooksS(G)

EFFECT : Dead(G), not In(G, x, y+1), Clear(x, y+1)

### NeutralizeGuardS(H, G)
PRECOND : Hitman(H), Guard(G), In(H, x, y), In(G, x, y-1), LooksS(H), not LooksN(G)

EFFECT : Dead(G), not In(G, x, y-1), Clear(x, y-1)

### NeutralizeGuardE(H, G)
PRECOND : Hitman(H), Guard(G), In(H, x, y), In(G, x+1, y), LooksE(H), not LooksW(G)

EFFECT : Dead(G), not In(G, x+1, y), Clear(x+1, y)

### NeutralizeGuardW(H, G)
PRECOND : Hitman(H), Guard(G), In(H, x, y), In(G, x-1, y), LooksW(H), not LooksE(G)

EFFECT : Dead(G), not In(G, x-1, y), Clear(x-1, y)

### NeutralizeCivilN(H, G)
PRECOND : Hitman(H), Civil(G), In(H, x, y), In(G, x, y+1), LooksN(H), not LooksS(G)

EFFECT : Dead(G), not In(G, x, y+1), Clear(x, y+1)

### NeutralizeCivilS(H, G)
PRECOND : Hitman(H), Civil(G), In(H, x, y), In(G, x, y-1), LooksS(H), not LooksN(G)

EFFECT : Dead(G), not In(G, x, y-1), Clear(x, y-1)

### NeutralizeCivilE(H, G)
PRECOND : Hitman(H), Civil(G), In(H, x, y), In(G, x+1, y), LooksE(H), not LooksW(G)

EFFECT : Dead(G), not In(G, x+1, y), Clear(x+1, y)

### NeutralizeCivilW(H, G)
PRECOND : Hitman(H), Civil(G), In(H, x, y), In(G, x-1, y), LooksW(H), not LooksE(G)

EFFECT : Dead(G), not In(G, x-1, y), Clear(x-1, y)

### TakeCostume(H, C)
PRECOND : Hitman(H), Costume(C), In(H, x, y), In(C, x, y)

EFFECT : not In(C, x, y), hasCostume(H)

### PutCostume(H)
PRECOND : Hitman(H), hasCostume(H)

EFFECT : not hasCostume(H), isDisguised(H)

### TakeRope(H, R)
PRECOND : Hitman(H), Rope(R), In(H, x, y), In(R, x, y)

EFFECT : not In(R, x, y), hasRope(H)


# Réflexions
- tous les duplicatas d'actions en fonction de l'orientation sont lourds mais j'ai pas réussi à trouver des fonctions génériques
- hasCostume ne sert dans aucune action
- comment utiliser cette modélisation ?