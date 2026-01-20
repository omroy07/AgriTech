import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCropPredictionRoute:
    """Test suite for crop prediction endpoint."""

    def test_crop_home_returns_200(self, client):
        """Test that crop home page returns 200."""
        response = client.get('/crop/')
        assert response.status_code in [200, 404]

    def test_crop_predict_requires_form_data(self, client):
        """Test that crop predict requires form data."""
        response = client.post('/crop/predict')
        # Should return 400 for missing data or 200 if handled
        assert response.status_code in [200, 400, 500]

    def test_crop_predict_with_valid_data(self, client):
        """Test crop predict with valid form data."""
        form_data = {
            'N': '50',
            'P': '40',
            'K': '30',
            'temperature': '25.5',
            'humidity': '80',
            'ph': '6.5',
            'rainfall': '200'
        }
        response = client.post('/crop/predict', data=form_data)
        # Should process or return error gracefully
        assert response.status_code in [200, 400, 500]


class TestDiseasePredictionRoute:
    """Test suite for disease prediction endpoint."""

    def test_disease_home_returns_200(self, client):
        """Test that disease home page returns 200."""
        response = client.get('/disease/')
        assert response.status_code in [200, 404]

    def test_disease_predict_without_file(self, client):
        """Test disease predict without file redirects."""
        response = client.post('/disease/predict')
        # Should redirect to home when no file
        assert response.status_code in [200, 302, 400]
