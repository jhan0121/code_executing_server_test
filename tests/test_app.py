import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_run_code(client):
    response = client.post('/run_code', json={
        'code': 'print("Hello, World!")',
        'language': 'python',
        'quiz_id': 1
    })
    json_data = response.get_json()
    assert json_data['result'] == '정답' or json_data['result'] == '오답'