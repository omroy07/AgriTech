import pytest
from Crop_Planning.app import app as crop_planning_app

def test_crop_planning_home():
    client = crop_planning_app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b'Crop Planner AI' in response.data
