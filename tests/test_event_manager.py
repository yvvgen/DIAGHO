import pytest
from datetime import datetime
import tempfile
from pathlib import Path
from event_planner.event_manager import EventManager
from event_planner.event import Event

class TestEventManager:
    @pytest.fixture
    def temp_storage(self):
        """Fixture qui crée un fichier temporaire pour les tests"""
        with tempfile.NamedTemporaryFile(suffix='.json') as tf:
            yield Path(tf.name)

    @pytest.fixture
    def manager(self, temp_storage):
        """Fixture qui crée un EventManager avec stockage temporaire"""
        return EventManager(temp_storage)

    @pytest.fixture
    def sample_events(self):
        """Fixture qui crée des événements de test"""
        return [
            Event("Event 1", 
                 datetime(2024, 1, 1, 10, 0),
                 datetime(2024, 1, 1, 11, 0)),
            Event("Event 2",
                 datetime(2024, 1, 1, 11, 0),
                 datetime(2024, 1, 1, 12, 0)),
            Event("Event 3",
                 datetime(2024, 1, 1, 10, 30),
                 datetime(2024, 1, 1, 11, 30))
        ]

    def test_add_event(self, manager, sample_events):
        """Test l'ajout d'événements"""
        manager.add_event(sample_events[0])
        assert len(manager._events) == 1
        
        # Test ajout avec conflit qui génère un warning
        with pytest.warns(UserWarning):
            manager.add_event(sample_events[2])

    def test_remove_event(self, manager, sample_events):
        """Test la suppression d'événements"""
        manager.add_event(sample_events[0])
        event_id = str(sample_events[0].id)
        
        assert manager.remove_event(event_id)
        assert len(manager._events) == 0
        
        # Test suppression événement inexistant
        assert not manager.remove_event("nonexistent-id")

    def test_list_events(self, manager, sample_events):
        """Test que get_events retourne les événements triés"""
        # Ajout dans un ordre différent
        manager.add_event(sample_events[1])  # 11:00
        manager.add_event(sample_events[0])  # 10:00
        
        events_sorted = manager.list_events()
        assert len(events_sorted) == 2
        assert events_sorted[0].start_time < events_sorted[1].start_time

    def test_find_conflicts(self, manager, sample_events):
        """Test la détection des conflits"""
        manager.add_event(sample_events[0])  # 10:00-11:00
        manager.add_event(sample_events[1])  # 11:00-12:00
        
        conflicts = manager.find_conflicts()
        assert not conflicts  # Pas de conflits
        
        # Ajout d'un événement qui chevauche
        with pytest.warns(UserWarning):
            manager.add_event(sample_events[2])  # 10:30-11:30

    def test_storage(self, manager, sample_events, temp_storage):
        """Test la persistance des données"""
        manager.add_event(sample_events[0])
        
        # Créer un nouveau manager avec le même stockage
        new_manager = EventManager(temp_storage)
        loaded_events = new_manager._events
        
        assert len(loaded_events) == 1
        assert loaded_events[0].name == sample_events[0].name
        
    def test_clear_events(self, manager, sample_events, temp_storage):
        """Test si les événements sont supprimés"""
        for event in sample_events:
            manager.add_event(event)
            
        assert len(manager._events) == 3
        
        manager.clear_events()
        
        assert len(manager._events) == 0
        assert not temp_storage.exists()
        
    def test_get_event_by_id(self, manager, sample_events, temp_storage):
        """Test si l'événement ramené est bien du bon id"""
        event = sample_events[0]
        event_id = str(event.id)
        manager.add_event(event)
        
        assert str(manager.get_event_by_id(event_id).id) == event_id