import pytest
from click.testing import CliRunner
from pathlib import Path
import json
import shutil
from datetime import datetime, timedelta
from event_planner.cli import cli
from event_planner.event import Event
from event_planner.event_manager import EventManager

class TestCLI:
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Configure un environnement de test temporaire"""
        # Sauvegarde le chemin original
        self.original_home = Path.home()
        # Crée un dossier temporaire pour les tests
        self.test_home = tmp_path / "test_home"
        self.test_home.mkdir()
        # Configure le chemin de stockage des tests
        self.storage_path = self.test_home / '.event_planner' / 'events.json'
        # Crée le runner Click pour les tests
        self.runner = CliRunner()
        
        # Modifie la fonction get_event_manager pour utiliser le stockage de test
        from event_planner.cli import get_event_manager as original_get_manager
        def mock_get_manager():
            return EventManager(storage_path=self.storage_path)
        import event_planner.cli
        event_planner.cli.get_event_manager = mock_get_manager
        
        yield
        
        # Nettoyage après les tests
        if self.test_home.exists():
            shutil.rmtree(self.test_home)
        # Restore la fonction originale
        event_planner.cli.get_event_manager = original_get_manager

    def test_add_event(self):
        """Teste l'ajout d'un événement"""
        result = self.runner.invoke(cli, [
            'add',
            '-n', 'Test Event',
            '-s', '2024-12-01 10:00',
            '-e', '2024-12-01 11:00',
            '-d', 'Test Description'
        ])
        
        assert result.exit_code == 0
        assert "ajouté avec succès" in result.output
        
        # Vérifie que l'événement a été sauvegardé
        with open(self.storage_path) as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]['name'] == 'Test Event'
        assert data[0]['description'] == 'Test Description'

    def test_add_invalid_event(self):
        """Teste l'ajout d'un événement avec des dates invalides"""
        result = self.runner.invoke(cli, [
            'add',
            '-n', 'Invalid Event',
            '-s', '2024-12-01 11:00',  # Fin avant début
            '-e', '2024-12-01 10:00'
        ])
        assert "Erreur" in result.output

    def test_list_empty(self):
        """Teste l'affichage d'une liste vide"""
        result = self.runner.invoke(cli, ['list'])
        assert result.exit_code == 0
        assert "Aucun événement trouvé" in result.output

    def test_list_events(self):
        """Teste l'affichage de la liste des événements"""
        # Ajoute quelques événements
        self.runner.invoke(cli, [
            'add',
            '-n', 'Event 1',
            '-s', '2024-12-01 10:00',
            '-e', '2024-12-01 11:00'
        ])
        self.runner.invoke(cli, [
            'add',
            '-n', 'Event 2',
            '-s', '2024-12-01 14:00',
            '-e', '2024-12-01 15:00'
        ])
        
        # Liste les événements
        result = self.runner.invoke(cli, ['list'])
        assert result.exit_code == 0
        assert "Event 1" in result.output
        assert "Event 2" in result.output

    def test_remove_event(self):
        """Teste la suppression d'un événement"""
        # Ajoute un événement
        add_result = self.runner.invoke(cli, [
            'add',
            '-n', 'Event to Remove',
            '-s', '2024-12-01 10:00',
            '-e', '2024-12-01 11:00'
        ])
        # Extrait l'ID de l'événement du message de succès
        event_id = add_result.output.split('ID: ')[1].strip(')\n')
        
        # Supprime l'événement
        result = self.runner.invoke(cli, ['remove', event_id])
        assert result.exit_code == 0
        assert "supprimé avec succès" in result.output
        
        # Vérifie que l'événement a été supprimé
        list_result = self.runner.invoke(cli, ['list'])
        assert "Aucun événement trouvé" in list_result.output

    def test_remove_nonexistent_event(self):
        """Teste la suppression d'un événement inexistant"""
        result = self.runner.invoke(cli, ['remove', 'nonexistent-id'])
        assert "Aucun événement trouvé" in result.output

    def test_list_conflicts(self):
        """Teste l'affichage des conflits"""
        # Ajoute deux événements qui se chevauchent
        self.runner.invoke(cli, [
            'add',
            '-n', 'Event A',
            '-s', '2024-12-01 10:00',
            '-e', '2024-12-01 11:30'
        ])
        self.runner.invoke(cli, [
            'add',
            '-n', 'Event B',
            '-s', '2024-12-01 11:00',
            '-e', '2024-12-01 12:00'
        ])
        
        # Vérifie les conflits
        result = self.runner.invoke(cli, ['list', '--conflicts'])
        assert result.exit_code == 0
        assert "Conflits détectés" in result.output
        assert "Event A" in result.output
        assert "Event B" in result.output

    def test_add_event_invalid_date_format(self):
        """Teste l'ajout d'un événement avec un format de date invalide"""
        result = self.runner.invoke(cli, [
            'add',
            '-n', 'Invalid Date Event',
            '-s', 'invalid-date',
            '-e', '2024-12-01 11:00'
        ])

        assert "Erreur" in result.output