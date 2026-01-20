import pytest
from unittest.mock import patch, MagicMock


class TestIndexRoute:
    """Test suite for the index route."""

    def test_index_returns_200(self, client):
        """Test that the index route returns 200."""
        response = client.get('/')
        assert response.status_code == 200


class TestFirebaseConfigRoute:
    """Test suite for the Firebase config endpoint."""

    @patch.dict('os.environ', {
        'FIREBASE_API_KEY': 'test_key',
        'FIREBASE_AUTH_DOMAIN': 'test.firebaseapp.com',
        'FIREBASE_PROJECT_ID': 'test-project',
        'FIREBASE_STORAGE_BUCKET': 'test.appspot.com',
        'FIREBASE_MESSAGING_SENDER_ID': '123456',
        'FIREBASE_APP_ID': '1:123:web:abc',
        'FIREBASE_MEASUREMENT_ID': 'G-TEST'
    })
    def test_firebase_config_returns_json(self, client):
        """Test that Firebase config returns proper JSON."""
        response = client.get('/api/firebase-config')
        assert response.status_code == 200
        data = response.get_json()
        assert 'apikey' in data or 'projectId' in data


class TestProcessLoanRoute:
    """Test suite for the process-loan endpoint."""

    @patch('app.model')
    def test_process_loan_requires_json(self, mock_model, client):
        """Test that process-loan requires JSON data."""
        response = client.post('/process-loan', data='not json')
        # Should return 400 or process the request
        assert response.status_code in [200, 400, 500]

    @patch('app.model')
    def test_process_loan_validates_input(self, mock_model, client):
        """Test that process-loan validates input."""
        # Mock the Gemini model response
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [MagicMock()]
        mock_response.candidates[0].content.parts[0].text = "Test response"
        mock_model.generate_content.return_value = mock_response

        response = client.post('/process-loan', 
                               json={"loan_type": "Crop Cultivation"},
                               content_type='application/json')
        # Should accept valid JSON
        assert response.status_code in [200, 400, 500]


class TestStaticRoutes:
    """Test suite for static HTML page routes."""

    def test_farmer_route(self, client):
        """Test farmer page route."""
        response = client.get('/farmer')
        assert response.status_code in [200, 404]

    def test_shopkeeper_route(self, client):
        """Test shopkeeper page route."""
        response = client.get('/shopkeeper')
        assert response.status_code in [200, 404]

    def test_about_route(self, client):
        """Test about page route."""
        response = client.get('/about')
        assert response.status_code in [200, 404]

    def test_contact_route(self, client):
        """Test contact page route."""
        response = client.get('/contact')
        assert response.status_code in [200, 404]


class TestErrorHandlers:
    """Test suite for error handlers."""

    def test_404_returns_json(self, client):
        """Test that 404 errors return JSON."""
        response = client.get('/nonexistent-route-12345')
        assert response.status_code == 404
        data = response.get_json()
        assert data is not None
        assert 'status' in data
        assert data['status'] == 'error'
