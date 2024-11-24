import click
from datetime import datetime
from pathlib import Path
from typing import Optional
from event_planner.event import Event
from event_planner.event_manager import EventManager

def get_event_manager():
    """Helper to create EventManager instance with default storage"""
    storage_path = Path.home() / '.event_planner' / 'events.json'
    return EventManager(storage_path=storage_path)

@click.group()
def cli():
    """Gestionnaire d'événements en ligne de commande"""
    pass

@cli.command()
@click.option('--name', '-n', required=True, help='Nom de l\'événement')
@click.option('--start_time', '-s', required=True, 
              help='Date et heure de début (format: YYYY-MM-DD HH:MM)')
@click.option('--end_time', '-e', required=True,
              help='Date et heure de fin (format: YYYY-MM-DD HH:MM)')
@click.option('--description', '-d', help='Description de l\'événement')
def add(name: str, start_time: str, end_time: str, description: str = None):
    """Ajoute un nouvel événement"""
    try:
        # Parse les dates
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)
        
        # Crée l'événement
        event = Event(
            name=name,
            start_time=start_time,
            end_time=end_time,
            description=description
        )
        
        # Ajoute l'événement
        manager = get_event_manager()
        if manager.add_event(event):
            click.echo(f"Événement '{name}' ajouté avec succès (ID: {event.id})")
        else:
            click.echo("Erreur lors de l'ajout de l'événement", err=True)
            
    except ValueError as e:
        click.echo(f"Erreur: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Une erreur inattendue est survenue: {str(e)}", err=True)

@cli.command()
@click.argument('event_id')
def remove(event_id: str):
    """Supprime un événement par son ID"""
    manager = get_event_manager()
    if manager.remove_event(event_id):
        click.echo(f"Événement {event_id} supprimé avec succès")
    else:
        click.echo(f"Aucun événement trouvé avec l'ID {event_id}", err=True)

@cli.command()
@click.option('--conflicts', '-c', is_flag=True, help='Affiche uniquement les événements en conflit')
@click.option('--start', '-s', type=click.DateTime(formats=["%Y-%m-%d %H:%M"]), 
              help='Date de début (format: YYYY-MM-DD HH:MM)')
@click.option('--end', '-e', type=click.DateTime(formats=["%Y-%m-%d %H:%M"]), 
              help='Date de fin (format: YYYY-MM-DD HH:MM)')
def list(conflicts: bool, start: Optional[datetime] = None, end: Optional[datetime] = None):
    """Liste tous les événements ou affiche les conflits.
    
    Peut être filtré par période en spécifiant --start et/ou --end.
    """
    manager = get_event_manager()
    
    if conflicts:
        conflict_dict = manager.find_conflicts()
        if not conflict_dict:
            click.echo("Aucun conflit trouvé")
            return
            
        # Filtrer les conflits par date si nécessaire
        if start or end:
            filtered_conflicts = {}
            events_in_range = set(manager.list_events_between(start, end))
            
            for event_id, conflicting_events in conflict_dict.items():
                event = manager.get_event_by_id(event_id)
                if event and event in events_in_range:
                    # Ne garder que les événements en conflit qui sont aussi dans la période
                    filtered_conflicts[event_id] = [
                        e for e in conflicting_events 
                        if e in events_in_range
                    ]
                    if filtered_conflicts[event_id]:  # Supprimer si plus de conflits dans la période
                        continue
                    del filtered_conflicts[event_id]
            
            conflict_dict = filtered_conflicts
            
        if not conflict_dict:
            click.echo("Aucun conflit trouvé dans la période spécifiée")
            return
            
        click.echo("Conflits détectés:")
        for event_id, conflicting_events in conflict_dict.items():
            event = manager.get_event_by_id(event_id)
            if event:
                click.echo(f"\nÉvénement: {event.name} (ID: {event.id})")
                click.echo("En conflit avec:")
                for conf_event in conflicting_events:
                    click.echo(f"  - {conf_event.name} (ID: {conf_event.id})")
    else:
        events = manager.list_events_between(start, end)
        if not events:
            if start or end:
                click.echo("Aucun événement trouvé dans la période spécifiée")
            else:
                click.echo("Aucun événement trouvé")
            return
            
        # Afficher la période si spécifiée
        if start or end:
            click.echo("Liste des événements", nl=False)
            if start:
                click.echo(f" depuis le {start.strftime('%Y-%m-%d %H:%M')}", nl=False)
            if end:
                click.echo(f" jusqu'au {end.strftime('%Y-%m-%d %H:%M')}", nl=False)
            click.echo(":")
        else:
            click.echo("Liste des événements:")
            
        for event in events:
            click.echo(f"\nID: {event.id}")
            click.echo(f"Nom: {event.name}")
            click.echo(f"Début: {event.start_time}")
            click.echo(f"Fin: {event.end_time}")
            if event.description:
                click.echo(f"Description: {event.description}")
if __name__ == '__main__':
    cli()