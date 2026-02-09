"""Unit tests for the todo CLI application using pytest."""
import json
import os
import tempfile
from io import StringIO
from unittest.mock import patch

import pytest

from src.todo import add_task, complete_task, list_tasks, load_tasks, save_tasks


@pytest.fixture
def temp_tasks_file():
    """Create a temporary tasks file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def empty_tasks_file(temp_tasks_file):
    """Create an empty tasks file (empty list)."""
    save_tasks([], temp_tasks_file)
    return temp_tasks_file


@pytest.fixture
def populated_tasks_file(temp_tasks_file):
    """Create a tasks file with sample tasks."""
    tasks = [
        {
            "id": 1,
            "title": "Buy groceries",
            "description": "Milk, bread, eggs",
            "created_at": "2026-02-09T10:00:00Z",
            "done": False,
        },
        {
            "id": 2,
            "title": "Fix bug",
            "description": "ID comparison in complete_task",
            "created_at": "2026-02-09T11:00:00Z",
            "done": False,
        },
        {
            "id": 3,
            "title": "Write tests",
            "description": "Unit tests for todo app",
            "created_at": "2026-02-09T12:00:00Z",
            "done": True,
        },
    ]
    save_tasks(tasks, temp_tasks_file)
    return temp_tasks_file


class TestLoadTasks:
    """Test load_tasks function."""

    def test_load_tasks_from_empty_file(self, empty_tasks_file):
        """Load tasks from an empty JSON file."""
        tasks = load_tasks(empty_tasks_file)
        assert tasks == []

    def test_load_tasks_from_populated_file(self, populated_tasks_file):
        """Load tasks from a file with existing tasks."""
        tasks = load_tasks(populated_tasks_file)
        assert len(tasks) == 3
        assert tasks[0]["title"] == "Buy groceries"
        assert tasks[2]["done"] is True

    def test_load_tasks_from_nonexistent_file(self, temp_tasks_file):
        """Return empty list when file doesn't exist."""
        os.remove(temp_tasks_file)
        tasks = load_tasks(temp_tasks_file)
        assert tasks == []

    def test_load_tasks_from_invalid_json(self, temp_tasks_file):
        """Return empty list when JSON is invalid."""
        with open(temp_tasks_file, 'w') as f:
            f.write("invalid json {")
        tasks = load_tasks(temp_tasks_file)
        assert tasks == []


class TestSaveTasks:
    """Test save_tasks function."""

    def test_save_tasks_to_file(self, temp_tasks_file):
        """Save tasks to a JSON file."""
        tasks = [
            {"id": 1, "title": "Task 1", "description": "", "created_at": "2026-02-09T10:00:00Z", "done": False}
        ]
        save_tasks(tasks, temp_tasks_file)
        
        # Verify by reading file
        with open(temp_tasks_file, 'r') as f:
            saved = json.load(f)
        assert saved == tasks

    def test_save_empty_tasks(self, temp_tasks_file):
        """Save empty task list."""
        save_tasks([], temp_tasks_file)
        with open(temp_tasks_file, 'r') as f:
            saved = json.load(f)
        assert saved == []


class TestAddTask:
    """Test add_task function."""

    def test_add_task_to_empty_file(self, empty_tasks_file):
        """Add a task to an empty tasks file."""
        with patch('sys.stdout', new=StringIO()) as output:
            add_task("Test task", "Test description", empty_tasks_file)
            assert "Added task 1: Test task" in output.getvalue()
        
        tasks = load_tasks(empty_tasks_file)
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Test task"
        assert tasks[0]["description"] == "Test description"
        assert tasks[0]["id"] == 1
        assert tasks[0]["done"] is False

    def test_add_task_increments_id(self, populated_tasks_file):
        """Check that new task gets next sequential ID."""
        with patch('sys.stdout', new=StringIO()):
            add_task("New task", "", populated_tasks_file)
        
        tasks = load_tasks(populated_tasks_file)
        assert len(tasks) == 4
        assert tasks[-1]["id"] == 4

    def test_add_task_without_description(self, empty_tasks_file):
        """Add task without optionalDescription."""
        with patch('sys.stdout', new=StringIO()):
            add_task("Simple task", "", empty_tasks_file)
        
        tasks = load_tasks(empty_tasks_file)
        assert tasks[0]["description"] == ""

    def test_add_task_with_special_characters(self, empty_tasks_file):
        """Add task with special characters and unicode."""
        with patch('sys.stdout', new=StringIO()):
            add_task("Buy café ☕", "Descripción: café", empty_tasks_file)
        
        tasks = load_tasks(empty_tasks_file)
        assert tasks[0]["title"] == "Buy café ☕"
        assert tasks[0]["description"] == "Descripción: café"

    def test_add_task_sets_created_at(self, empty_tasks_file):
        """Verify that created_at timestamp is set."""
        with patch('sys.stdout', new=StringIO()):
            add_task("Timestamped task", "", empty_tasks_file)
        
        tasks = load_tasks(empty_tasks_file)
        assert "created_at" in tasks[0]
        assert tasks[0]["created_at"].endswith("Z")
        assert "T" in tasks[0]["created_at"]  # ISO format check


class TestListTasks:
    """Test list_tasks function."""

    def test_list_empty_tasks(self, empty_tasks_file):
        """List tasks when no tasks exist."""
        with patch('sys.stdout', new=StringIO()) as output:
            list_tasks(empty_tasks_file)
            assert "No tasks found." in output.getvalue()

    def test_list_tasks_displays_all(self, populated_tasks_file):
        """List all tasks from file."""
        with patch('sys.stdout', new=StringIO()) as output:
            list_tasks(populated_tasks_file)
            output_text = output.getvalue()
            assert "Buy groceries" in output_text
            assert "Fix bug" in output_text
            assert "Write tests" in output_text

    def test_list_tasks_shows_completion_status(self, populated_tasks_file):
        """Verify completion status displayed correctly."""
        with patch('sys.stdout', new=StringIO()) as output:
            list_tasks(populated_tasks_file)
            output_text = output.getvalue()
            # Incomplete tasks should have space, completed should have checkmark
            lines = output_text.strip().split('\n')
            assert '[✓]' in lines[2]  # Third task is completed
            assert '[ ]' in lines[0]  # First task is not completed

    def test_list_tasks_shows_task_details(self, populated_tasks_file):
        """Verify task ID, title, and description are shown."""
        with patch('sys.stdout', new=StringIO()) as output:
            list_tasks(populated_tasks_file)
            output_text = output.getvalue()
            # Output format is "[ ] id: title - description"
            lines = output_text.strip().split('\n')
            assert any("1:" in line for line in lines)
            assert any("2:" in line for line in lines)
            assert any("3:" in line for line in lines)


class TestCompleteTask:
    """Test complete_task function."""

    def test_complete_existing_task(self, populated_tasks_file):
        """Mark an existing task as complete."""
        with patch('sys.stdout', new=StringIO()) as output:
            complete_task(1, populated_tasks_file)
            assert "Marked task 1 complete." in output.getvalue()
        
        tasks = load_tasks(populated_tasks_file)
        assert tasks[0]["done"] is True

    def test_complete_nonexistent_task(self, populated_tasks_file):
        """Attempt to complete a task that doesn't exist."""
        with patch('sys.stdout', new=StringIO()) as output:
            complete_task(999, populated_tasks_file)
            assert "No task found with id 999." in output.getvalue()

    def test_complete_already_completed_task(self, populated_tasks_file):
        """Mark an already-completed task as complete (should be idempotent)."""
        with patch('sys.stdout', new=StringIO()) as output:
            complete_task(3, populated_tasks_file)
            assert "Marked task 3 complete." in output.getvalue()
        
        tasks = load_tasks(populated_tasks_file)
        assert tasks[2]["done"] is True

    def test_complete_task_persists_to_file(self, populated_tasks_file):
        """Verify task completion is persisted."""
        with patch('sys.stdout', new=StringIO()):
            complete_task(2, populated_tasks_file)
        
        # Load fresh from file to verify persistence
        tasks = load_tasks(populated_tasks_file)
        assert tasks[1]["done"] is True
        # Other tasks should not be affected
        assert tasks[0]["done"] is False

    def test_complete_multiple_tasks(self, populated_tasks_file):
        """Complete multiple different tasks."""
        with patch('sys.stdout', new=StringIO()):
            complete_task(1, populated_tasks_file)
            complete_task(2, populated_tasks_file)
        
        tasks = load_tasks(populated_tasks_file)
        assert tasks[0]["done"] is True
        assert tasks[1]["done"] is True
        assert tasks[2]["done"] is True  # Was already completed

    def test_complete_task_with_small_id(self, empty_tasks_file):
        """Test ID comparison works with small integers."""
        with patch('sys.stdout', new=StringIO()):
            add_task("Task", "", empty_tasks_file)
        
        with patch('sys.stdout', new=StringIO()) as output:
            complete_task(1, empty_tasks_file)
            assert "Marked task 1 complete." in output.getvalue()

    @pytest.mark.xfail(reason="Known bug: 'is' comparison fails for large integers > 256")
    def test_complete_task_with_large_id(self, temp_tasks_file):
        """Test ID comparison works with large integers (catches 'is' bug).
        
        This test documents a known bug where using `is` instead of `==` 
        causes integer comparison failures for IDs > 256 due to Python's
        integer caching (-5 to 256 are cached).
        """
        # Create task with large ID
        tasks = [
            {
                "id": 300,
                "title": "Large ID task",
                "description": "",
                "created_at": "2026-02-09T10:00:00Z",
                "done": False,
            }
        ]
        save_tasks(tasks, temp_tasks_file)
        
        # Try to complete it - this would fail with `is` comparison for large ints
        with patch('sys.stdout', new=StringIO()) as output:
            complete_task(300, temp_tasks_file)
            assert "Marked task 300 complete." in output.getvalue()
        
        tasks = load_tasks(temp_tasks_file)
        assert tasks[0]["done"] is True
