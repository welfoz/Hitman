# Phase 2 - STRIPS

## Fonctionnement de STRIPS :

STRIPS (Stanford Research Institute Problem Solver) est un système de planification automatisé qui a été développé dans les années 1970. Il est basé sur la représentation des états du monde et des actions qui peuvent changer ces états. Voici comment vous pouvez modéliser un problème en utilisant STRIPS :

**Définir les états** : Un état dans STRIPS est une collection de littéraux. Par exemple, si vous modélisez un problème de robotique, un état pourrait être {RobotAtLocationA, BoxAtLocationB}.

**Définir les actions** : Chaque action dans STRIPS est définie par trois ensembles : les préconditions, les effets d'ajout et les effets de suppression. 

- Les préconditions sont les conditions qui doivent être remplies pour que l'action puisse être effectuée. 
- Les effets d'ajout sont les littéraux qui sont ajoutés à l'état après l'exécution de l'action, et les effets de suppression sont les littéraux qui sont supprimés de l'état après l'exécution de l'action. Par exemple, une action pourrait être MoveRobotToLocationB, avec les préconditions {RobotAtLocationA}, les effets d'ajout {RobotAtLocationB} et les effets de suppression {RobotAtLocationA}.

**Définir le but** : Le but dans STRIPS est également une collection de littéraux. L'objectif du système de planification est de trouver une séquence d'actions qui transforme l'état initial en un état qui satisfait le but. Par exemple, si le but est {RobotAtLocationB, BoxAtLocationB}, le système de planification doit trouver une séquence d'actions qui déplace le robot et la boîte à l'emplacement B.

**Planification** : Une fois que vous avez défini les états, les actions et le but, vous pouvez utiliser un algorithme de planification pour trouver une séquence d'actions qui atteint le but à partir de l'état initial. Il existe de nombreux algorithmes de planification différents que vous pouvez utiliser, comme l'algorithme A* ou l'algorithme de recherche en profondeur d'abord.

---

## Hitman

### Fluents :
- In(a, x, y) : position d'un élément en (x,y)
- Clear(x, y) : case vide
- Dead(a) : élément neutralisé
- LooksN(a) : élément tourné vers le nord
- LooksE, LooksW, LooksS : idem
- hasCostume(H)
- hasRope(H)
- isDisguised(H)
### Etat initial : Init(...)
- In(H, 0, 0) : (pour simplifier Hitman démarre et termine en 0,0)
- Hitman(H)
- LooksN(H)
- In(T, 2, 3)
- Target(T)
- Guard(G)
- Civil(C)
- Rope(R)
- Costume(C)
- Clear(x, y) : pour toutes les cases vides (pas besoin de mettre les murs car Clear indiquera les endroits praticables)
### Goal : Goal(...)
- In(H, 0, 0)
- Dead(T)
- Hitman(H)
- Target(T)
### Actions :
- MoveN(H)
- MoveE, MoveW, MoveS
- TurnNToW(H)
- TurnNToE, TurnEToN, TurnEToS, TurnWToN, TurnWToS, TurnSToW, TurnSToW
- KillTarget(H, T, R)
- NeutralizeGuardN(H, G)
- NeutralizeGuardE, NeutralizeGuardW, NeutralizeGuardS
- NeutralizeCivilN(H, C)
- NeutralizeCivilE, NeutralizeCivilW, NeutralizeCivilS
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