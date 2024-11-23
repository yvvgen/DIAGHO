import pytest
from datetime import datetime, timedelta
from uuid import UUID
from event_planner.event import Event

class TestEvent:
    def test_event_creation(self):
        """Test la création basique d'un événement"""
        start = datetime(2024, 1, 1, 10, 0)
        end = datetime(2024, 1, 1, 11, 0)
        event = Event("Réunion", start, end)
        
        assert event.name == "Réunion"
        assert event.start_time == start
        assert event.end_time == end
        assert isinstance(event.id, UUID)

    def test_invalid_dates(self):
        """Test qu'une exception est levée si end_time < start_time"""
        start = datetime(2024, 1, 1, 11, 0)
        end = datetime(2024, 1, 1, 10, 0)
        
        with pytest.raises(ValueError):
            Event("Réunion", start, end)

    def test_overlaps_same_time(self):
        """Test le chevauchement pour des événements au même moment"""
        start = datetime(2024, 1, 1, 10, 0)
        end = datetime(2024, 1, 1, 11, 0)
        
        event1 = Event("Event 1", start, end)
        event2 = Event("Event 2", start, end)
        
        assert event1.overlaps(event2)
        assert event2.overlaps(event1)

    def test_overlaps_partial(self):
        """Test le chevauchement partiel"""
        event1 = Event("Event 1", 
                      datetime(2024, 1, 1, 10, 0),
                      datetime(2024, 1, 1, 12, 0))
        
        event2 = Event("Event 2",
                      datetime(2024, 1, 1, 11, 0),
                      datetime(2024, 1, 1, 13, 0))
        
        assert event1.overlaps(event2)
        assert event2.overlaps(event1)

    def test_no_overlap(self):
        """Test l'absence de chevauchement"""
        event1 = Event("Event 1",
                      datetime(2024, 1, 1, 10, 0),
                      datetime(2024, 1, 1, 11, 0))
        
        event2 = Event("Event 2",
                      datetime(2024, 1, 1, 12, 0),
                      datetime(2024, 1, 1, 13, 0))
        
        assert not event1.overlaps(event2)
        assert not event2.overlaps(event1)

    def test_to_dict(self):
        """Test la sérialisation en dictionnaire"""
        start = datetime(2024, 1, 1, 10, 0)
        end = datetime(2024, 1, 1, 11, 0)
        event = Event("Réunion", start, end)
        
        event_dict = event.to_dict()
        assert event_dict["name"] == "Réunion"
        assert event_dict["start_time"] == start.isoformat()
        assert event_dict["end_time"] == end.isoformat()
        assert UUID(event_dict["id"])

    def test_from_dict(self):
        """Test la désérialisation depuis un dictionnaire"""
        event_dict = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Réunion",
            "start_time": "2024-01-01T10:00:00",
            "end_time": "2024-01-01T11:00:00"
        }
        
        event = Event.from_dict(event_dict)
        assert event.name == "Réunion"
        assert event.start_time == datetime(2024, 1, 1, 10, 0)
        assert event.end_time == datetime(2024, 1, 1, 11, 0)
        assert str(event.id) == "123e4567-e89b-12d3-a456-426614174000"
        
    def test_duration(self):
        """Test la propriété durée d'un Event"""
        start = datetime(2024, 1, 1, 10, 0)
        end = datetime(2024, 1, 1, 11, 0)
        event = Event("Réunion", start, end)
        
        assert event.duration == timedelta(hours=1)
        
    def test_overlap_same_event(self):
        """Test si la bonne exception est levée lorsque l'on cherche un overlap d'un event sur lui même"""
        start = datetime(2024, 1, 1, 10, 0)
        end = datetime(2024, 1, 1, 11, 0)
        event = Event("Réunion", start, end)
        
        with pytest.raises(ValueError):
            event.overlaps(event)