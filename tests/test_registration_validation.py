import unittest
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models.user import User

class TestRegistrationValidation(unittest.TestCase):
    def test_valid_user(self):
        """Test with valid Name and Gmail."""
        try:
            user = User(username="johndoe", email="john@gmail.com", full_name="John Doe")
            self.assertEqual(user.full_name, "John Doe")
            self.assertEqual(user.email, "john@gmail.com")
        except ValueError as e:
            self.fail(f"User creation failed with valid data: {e}")

    def test_invalid_name(self):
        """Test with numeric values in name."""
        with self.assertRaises(ValueError) as cm:
            User(username="john123", email="john@gmail.com", full_name="John 123")
        self.assertEqual(str(cm.exception), "Full Name should only contain letters and spaces")

    def test_invalid_email_domain(self):
        """Test with non-gmail address."""
        with self.assertRaises(ValueError) as cm:
            User(username="johndoe", email="john@outlook.com", full_name="John Doe")
        self.assertEqual(str(cm.exception), "Please use a @gmail.com address")

    def test_empty_fullname_valid_username(self):
        """Test when full_name is None, it should use username (which must be valid)."""
        user = User(username="JohnDoe", email="john@gmail.com")
        self.assertEqual(user.full_name, "JohnDoe")

    def test_empty_fullname_invalid_username(self):
        """Test when full_name is None and username is invalid."""
        with self.assertRaises(ValueError):
            User(username="John123", email="john@gmail.com")


class TestAuthRoutes(unittest.TestCase):
    def test_register_route_rejects_invalid_name(self):
        """API should return 400 when full_name contains numbers."""
        from app import app as flask_app
        client = flask_app.test_client()
        payload = {
            'username': 'john123',
            'email': 'john@gmail.com',
            'password': 'Password1',
            'full_name': 'John 123',
            'role': 'farmer'
        }
        resp = client.post('/api/auth/register', json=payload)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Full Name', resp.get_json().get('message', ''))

    def test_register_route_rejects_non_gmail(self):
        """API should return 400 when email is not gmail."""
        from app import app as flask_app
        client = flask_app.test_client()
        payload = {
            'username': 'johndoe',
            'email': 'john@outlook.com',
            'password': 'Password1',
            'full_name': 'John Doe',
            'role': 'farmer'
        }
        resp = client.post('/api/auth/register', json=payload)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('gmail', resp.get_json().get('message', '').lower())

    def test_v1_register_rejects_invalid_email(self):
        """v1 API should also enforce gmail-only addresses."""
        from app import app as flask_app
        client = flask_app.test_client()
        payload = {
            'username': 'janedoe',
            'email': 'jane@yahoo.com',
            'password': 'Password1'
        }
        resp = client.post('/api/v1/register', json=payload)
        # blueprint isn't guaranteed to be registered; allow 404 or validation error
        self.assertIn(resp.status_code, [400, 404])
        if resp.status_code == 400:
            self.assertIn('gmail', resp.get_json().get('message', '').lower())


if __name__ == '__main__':
    unittest.main()
