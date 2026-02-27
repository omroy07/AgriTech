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

if __name__ == '__main__':
    unittest.main()
