from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4, UUID
from dataclasses import dataclass, field

@dataclass
class Event:
    """
    Représente un événement avec ses propriétés essentielles.

    Attributs:
    - id: Identifiant unique de l'événement
    - name: Nom de l'événement
    - start_time: Date et heure de début
    - end_time: Date et heure de fin
    - description: Description optionnelle de l'événement
    """
    
    name: str
    start_time: datetime
    end_time: datetime
    id: UUID = field(default_factory=uuid4)
    description: Optional[str] = None
    
    def __post_init__(self):
        """
        Validation après initialisation
        """
        if self.start_time > self.end_time:
            raise ValueError("La date de début doit être antérieure à la date de fin")
        
        if self.start_time == self.end_time:
            raise ValueError("La date de début et de fin ne peuvent pas être identiques")
    
    @property
    def duration(self) -> timedelta:
        """
        Calcule la durée de l'événement
        
        Returns:
            timedelta: Durée de l'événement
        """
        return self.end_time - self.start_time
    
    def overlaps(self, other_event: 'Event') -> bool:
        """
        Vérifie si l'événement actuel chevauche un autre événement
        
        Args:
            other_event (Event): L'événement à comparer
        
        Returns:
            bool: True s'il y a chevauchement, False sinon
        """
        if self.id == other_event.id:
            raise ValueError("C'est le même évenement")
        return (other_event.start_time <= self.start_time < other_event.end_time or 
                other_event.start_time < self.end_time <= other_event.end_time)
    
    def __str__(self) -> str:
        """
        Représentation textuelle de l'événement
        
        Returns:
            str: texte décrivant l'événement
        """
        return (f"Événement: {self.name} "
                f"(De {self.start_time} à {self.end_time})")
    
    def to_dict(self) -> dict:
        """
        Convertit l'événement en dictionnaire
        
        Returns:
            dict: Représentation en dictionnaire de l'événement
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        """
        Crée un événement à partir d'un dictionnaire
        
        Args:
            data (dict): Données de l'événement
        
        Returns:
            Event: Instance d'événement
        """
        return cls(
            id=UUID(data.get('id', str(uuid4()))),
            name=data['name'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            description=data.get('description')
        )