from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
import warnings
import json
from pathlib import Path
from event_planner.event import Event

@dataclass
class EventManager:
    """
    Gestionnaire central pour les opérations sur les événements
    """
    storage_path: Path = field(default_factory=lambda: Path.home() / '.event_planner' / 'events.json')
    _events: List[Event] = field(default_factory=list)

    def __post_init__(self):
        """
        Initialisation après la création de l'instance.
        Crée le dossier de stockage si nécessaire et charge les événements.
        """
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_events()

    def _load_events(self) -> None:
        """
        Charge les événements depuis le fichier de stockage.
        Initialise une liste vide en cas d'erreur.
        """
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, 'r') as f:
                events_data = json.load(f)
                self._events = [Event.from_dict(event_data) for event_data in events_data]
        except json.JSONDecodeError:
            self._events = []

    def _save_events(self) -> None:
        """
        Sauvegarde les événements dans le fichier de stockage.
        """
        with open(self.storage_path, 'w') as f:
            json.dump([event.to_dict() for event in self._events], f, indent=2)

    def add_event(self, event: Event) -> bool:
        """
        Ajoute un événement après vérification des conflits.
        
        Args:
            event: L'événement à ajouter
            
        Returns:
            bool: True si l'ajout est réussi
        """
        if self.has_conflict(event):
            warnings.warn(
                "Événement en conflit avec un événement existant. Ajout tout de même.",
                UserWarning
            )
        
        self._events.append(event)
        self._save_events()
        return True


    def remove_event(self, event_id: str) -> bool:
        """
        Supprime un événement par son ID.
        
        Args:
            event_id: L'ID de l'événement à supprimer
            
        Returns:
            bool: True si l'événement a été supprimé, False sinon
        """
        initial_length = len(self._events)
        self._events = [evt for evt in self._events if str(evt.id) != event_id]
        
        if len(self._events) < initial_length:
            self._save_events()
            return True
        return False

    def clear_events(self) -> None:
        """
        Supprime tous les événements et le fichier de stockage.
        """
        self._events.clear()
        if self.storage_path.exists():
            self.storage_path.unlink()

    def has_conflict(self, event: Event) -> bool:
        """
        Vérifie si un événement est en conflit avec les événements existants.
        
        Args:
            event: L'événement à vérifier
            
        Returns:
            bool: True s'il y a un conflit, False sinon
        """
        for existing_event in self._events:
            if existing_event.overlaps(event):
                return True
        return False

    def list_events(self) -> List[Event]:
        """
        Retourne la liste de tous les événements par ordre chronologique
        
        Returns:
            List[Event]: Liste des événements
        """
        return sorted(
            self._events,
            key=lambda event: (event.start_time, event.end_time)
        )
    
    def list_events_between(self, start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[Event]:
        """
        Retourne la liste des événements entre deux dates, triés chronologiquement.
        Si start ou end ne sont pas spécifiés, ne filtre pas sur ces critères.
        
        C'est possible qu'un événement commence avant start ou finisse après end, le tout est qu'il empiète sur la fenêtre temporelle donnée
        
        Args:
            start (datetime, optional): Date de début de la période
            end (datetime, optional): Date de fin de la période
            
        Returns:
            List[Event]: Liste des événements dans la période
        """
        events = self.list_events()  # Déjà triés chronologiquement
        
        if start:
            events = [e for e in events if e.end_time >= start]
        if end:
            events = [e for e in events if e.start_time <= end]
            
        return events

    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """
        Récupère un événement par son ID.
        
        Args:
            event_id: L'ID de l'événement recherché
            
        Returns:
            Optional[Event]: L'événement trouvé ou None
        """
        return next((e for e in self._events if str(e.id) == event_id), None)    

    def find_conflicts(self) -> Dict[str, List[Event]]:
        """
        Trouve tous les conflits temporels entre les événements gérés.
        
        Returns:
            Dictionnaire avec les IDs des événements comme clés et 
            la liste de leurs événements en conflit comme valeurs
        """
        conflicts = {}
        
        # Comparer chaque événement avec tous les autres
        for i, event in enumerate(self._events):
            # On ne compare qu'avec les événements suivants pour éviter les doublons
            conflicting_events = [
                other_event 
                for other_event in self._events[i + 1:]
                if event.overlaps(other_event)
            ]
            
            if conflicting_events:
                # Si l'événement a des conflits, on l'ajoute au dictionnaire
                event_id = str(event.id)
                conflicts[event_id] = conflicting_events
                
                # On ajoute aussi la relation inverse pour chaque conflit
                for other_event in conflicting_events:
                    other_id = str(other_event.id)
                    if other_id not in conflicts:
                        conflicts[other_id] = []
                    conflicts[other_id].append(event)

        return conflicts