# Event Planner

Un gestionnaire d'événements en ligne de commande permettant de créer, lister et gérer des événements avec détection de conflits.

## Installation avec Docker

```bash
# Construire l'image
docker build -t event-planner .

# Lancer un conteneur interactif
docker run -it event-planner bash
```

## Tests

Une fois dans le conteneur, lancez les tests avec pytest :

```bash
pytest
```
Les tests ne couvrent pas tout le code mais seulement la majorité la plus importante des fonctionalités.

## Utilisation de la CLI

Dans le conteneur, utilisez la commande `event-planner` suivie des sous-commandes.

Pour une description de l'utilisation, tapez`event-planner --help`.

### Créer quelques conflits 

```bash
event-planner add -n "Déjeuner royal" -s "2024-11-25 12:00" -e "2024-11-25 14:00" \
    -d "Restaurant avec tous les collaborateur.ices"

event-planner add -n "Réunion ULTRA importante" -s "2024-11-25 13:00" -e "2024-11-25 14:30" \
    -d "Réunion pour changer la biographie Linked In"

event-planner add -n "Micro-sieste" -s "2024-11-25 13:45" -e "2024-11-25 16:00" \
    -d "15 minutes qui se transforment mystérieusement en 2h15"

event-planner add -n "Debuggage de la prod" -s "2024-11-26 09:00" -e "2024-11-26 19:00" \
    -d "Quand un bug en prod englobe TOUS les autres événements de la journée"

event-planner add -n "Daily standup" -s "2024-11-26 10:00" -e "2024-11-26 10:15" \
    -d "Coincé entre deux bugs, mais toujours présent"
```

### Découvrir l'étendue des dégâts

```bash
# Lister tous les événements 
event-planner list

# Voir les conflits
event-planner list --conflicts
```

Voici ce que vous pourriez voir avec `list --conflicts` :

```
Conflits détectés:

Événement: Déjeuner royal (ID: 123e4567-e89b-12d3-a456-426614174000)
En conflit avec:
  - Réunion ULTRA importante
  - Micro-sieste
  - Debuggage de la prod

Événement: Debuggage de la prod (ID: 123e4567-e89b-12d3-a456-426614174001)
En conflit avec:
  - Daily standup
  - Déjeuner royal
  - Réunion ULTRA importante
  - Micro-sieste
```

Il est aussi possible de spécifier une fenêtre de temps pour lister (et/ou lister les conflits).

### Résoudre les conflits (ou pas)

```bash
# Supprimer la réunion
event-planner remove <id-de-la-reunion>
```

Les événements sont automatiquement sauvegardés dans `~/.event_planner/events.json`, mais dans le conteneur je n'ai pas paramétré de persistance de donnée.