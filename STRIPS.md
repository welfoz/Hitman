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
### Etat initial : Init(...)
- In(H, 0, 0)
- Hitman(H)
- LooksN(H)
- In(T, 2, 3)
- Target(T)
- // pour guardes, civils, corde, costume (pas besoin de mettre les murs car Clear indiquera les endroits praticables)
- Clear(x, y) pour toutes les cases vides
### Goal : Goal(...)
- In(H, 0, 0)
- Dead(T)
- Hitman(H)
- Target(T)
### Actions :
- MoveN(H)
- // pour E, W, S
- TurnAnti(H)
- TurnClock(H)
- KillTarget(H, T, R)
- Neutralize(H, a)
- TakeCostume(H, C)
- PutCostume(H, C)
- TakeRope(H, R)
#### Code : MoveN(H)
PRECOND : Hitman(H), LooksN(H), In(H, x, y), Clear(x, y+1)
EFFECT : In(H, x, y+1), not In(H, x, y)