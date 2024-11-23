import click
from datetime import datetime
from pathlib import Path
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
@click.option('--start', '-s', required=True, 
              help='Date et heure de début (format: YYYY-MM-DD HH:MM)')
@click.option('--end', '-e', required=True,
              help='Date et heure de fin (format: YYYY-MM-DD HH:MM)')
@click.option('--description', '-d', help='Description de l\'événement')
def add(name: str, start: str, end: str, description: str = None):
    """Ajoute un nouvel événement"""
    try:
        # Parse les dates
        start_time = datetime.fromisoformat(start)
        end_time = datetime.fromisoformat(end)
        
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
def list(conflicts: bool):
    """Liste tous les événements ou affiche les conflits"""
    manager = get_event_manager()
    
    if conflicts:
        conflict_dict = manager.find_conflicts()
        if not conflict_dict:
            click.echo("Aucun conflit trouvé")
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
        events = manager.list_events()
        if not events:
            click.echo("Aucun événement trouvé")
            return
            
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