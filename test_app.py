import pytest
from app import create_app, db
from app.models import Task


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


@pytest.fixture
def seeded_client(client):
    client.post('/tasks', json={"task": "Buy groceries"})
    client.post('/tasks', json={"task": "Read a book"})
    return client


class TestHome:
    def test_home_returns_200(self, client):
        res = client.get('/')
        assert res.status_code == 200

    def test_home_message(self, client):
        data = client.get('/').get_json()
        assert data["Message"] == "API is running"

class TestErrorHandlers:
    def test_404_unknown_route(self,client):
        res=client.get('/nonexistent')
        assert res.status_code==404
        assert "Error" in res.get_json()
    def test_405_wrong_method(self,client):
        res=client.delete('/')
        assert res.status_code==405
        assert "Error" in res.get_json()
class TestGetAllTasks:
    def test_empty_db_returns_empty_list(self, client):
        res = client.get('/tasks')
        assert res.status_code == 200
        assert res.get_json() == []

    def test_returns_all_tasks(self, seeded_client):
        res = seeded_client.get('/tasks')
        assert res.status_code == 200
        assert len(res.get_json()) == 2

    def test_task_shape(self, seeded_client):
        tasks = seeded_client.get('/tasks').get_json()
        for t in tasks:
            assert set(t.keys()) == {"id", "task", "done","created_at", "updated_at"}


class TestAddTask:
    def test_creates_task_and_returns_201(self, client):
        res = client.post('/tasks', json={"task": "Walk the dog"})
        assert res.status_code == 201

    def test_response_contains_correct_task(self, client):
        res = client.post('/tasks', json={"task": "Walk the dog"})
        data = res.get_json()
        assert data["task"] == "Walk the dog"
        assert data["done"] is False
        assert "id" in data

    def test_strips_whitespace(self, client):
        res = client.post('/tasks', json={"task": "  Trim me  "})
        assert res.get_json()["task"] == "Trim me"

    def test_missing_task_key_returns_400(self, client):
        res = client.post('/tasks', json={"wrong_key": "value"})
        assert res.status_code == 400

    def test_empty_task_string_returns_400(self, client):
        res = client.post('/tasks', json={"task": "   "})
        assert res.status_code == 400

    def test_no_body_returns_400(self, client):
        res = client.post('/tasks')
        assert res.status_code == 400


class TestAddBulkTasks:
    def test_adds_multiple_tasks(self, client):
        res = client.post('/tasks/bulk', json={"tasks": ["Task A", "Task B", "Task C"]})
        assert res.status_code == 201
        assert res.get_json()["Message"] == "3 task(s) added"

    def test_added_list_length_matches(self, client):
        res = client.post('/tasks/bulk', json={"tasks": ["Task A", "Task B"]})
        assert len(res.get_json()["added"]) == 2

    def test_skips_blank_strings(self, client):
        res = client.post('/tasks/bulk', json={"tasks": ["Valid task", "  ", ""]})
        data = res.get_json()
        assert len(data["added"]) == 1
        assert len(data["skipped"]) == 2

    def test_skips_non_string_items(self, client):
        res = client.post('/tasks/bulk', json={"tasks": ["Good task", 42, None]})
        data = res.get_json()
        assert len(data["added"]) == 1
        assert len(data["skipped"]) == 2

    def test_missing_tasks_key_returns_400(self, client):
        res = client.post('/tasks/bulk', json={"wrong": []})
        assert res.status_code == 400

    def test_non_list_tasks_value_returns_400(self, client):
        res = client.post('/tasks/bulk', json={"tasks": "not a list"})
        assert res.status_code == 400

    def test_empty_list_returns_400(self, client):
        res = client.post('/tasks/bulk', json={"tasks": []})
        assert res.status_code == 400

class TestTimeStamps:
    def test_created_at_present(self,client):
        res=client.post('/tasks',json={"task":"Test task"})
        assert "created_at" in res.get_json()

    def test_updated_at_present(self,client):
        res=client.post('/tasks',json={"task":"Test task"})
        assert "updated_at" in res.get_json()

    def test_updated_at_changes_on_update(self, seeded_client):
        original=seeded_client.get('/tasks/1').get_json()["updated_at"]
        seeded_client.put('/tasks/1',json={"task":"Changed"})
        updated=seeded_client.get('/tasks/1').get_json()["updated_at"]
        assert updated != original

class TestGetSingleTask:
    def test_returns_correct_task(self, seeded_client):
        res = seeded_client.get('/tasks/1')
        assert res.status_code == 200
        assert res.get_json()["task"] == "Buy groceries"

    def test_nonexistent_id_returns_404(self, client):
        res = client.get('/tasks/999')
        assert res.status_code == 404


class TestUpdateTask:
    def test_updates_task_text(self, seeded_client):
        res = seeded_client.put('/tasks/1', json={"task": "Buy organic groceries"})
        assert res.status_code == 200
        assert res.get_json()["task"]["task"] == "Buy organic groceries"

    def test_marks_task_done(self, seeded_client):
        res = seeded_client.put('/tasks/1', json={"done": True})
        assert res.status_code == 200
        assert res.get_json()["task"]["done"] is True

    def test_updates_both_fields_at_once(self, seeded_client):
        res = seeded_client.put('/tasks/1', json={"task": "New text", "done": True})
        data = res.get_json()["task"]
        assert data["task"] == "New text"
        assert data["done"] is True

    def test_strips_whitespace_on_update(self, seeded_client):
        res = seeded_client.put('/tasks/1', json={"task": "  Spaced out  "})
        assert res.get_json()["task"]["task"] == "Spaced out"

    def test_empty_task_string_returns_400(self, seeded_client):
        res = seeded_client.put('/tasks/1', json={"task": "   "})
        assert res.status_code == 400

    def test_no_body_returns_400(self, seeded_client):
        res = seeded_client.put('/tasks/1')
        assert res.status_code == 400

    def test_nonexistent_id_returns_404(self, client):
        res = client.put('/tasks/999', json={"task": "Ghost task"})
        assert res.status_code == 404

    def test_update_does_not_affect_other_tasks(self, seeded_client):
        seeded_client.put('/tasks/1', json={"task": "Changed"})
        res = seeded_client.get('/tasks/2')
        assert res.get_json()["task"] == "Read a book"


class TestDeleteTask:
    def test_deletes_task_and_returns_200(self, seeded_client):
        res = seeded_client.delete('/tasks/1')
        assert res.status_code == 200

    def test_task_no_longer_exists_after_delete(self, seeded_client):
        seeded_client.delete('/tasks/1')
        res = seeded_client.get('/tasks/1')
        assert res.status_code == 404

    def test_total_count_decreases(self, seeded_client):
        seeded_client.delete('/tasks/1')
        tasks = seeded_client.get('/tasks').get_json()
        assert len(tasks) == 1

    def test_nonexistent_id_returns_404(self, client):
        res = client.delete('/tasks/999')
        assert res.status_code == 404