import unittest
from unittest.mock import MagicMock
from django.test import TestCase
from api.models import User
from .utils import check_access, encode_token, get_token, decode_token
from rest_framework.exceptions import AuthenticationFailed

class UtilsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')

    def test_encode_token(self):
        token = encode_token(self.user)
        self.assertTrue(isinstance(token, str))

    def test_get_token_valid(self):
        auth_header = 'Bearer your_valid_token_here'
        response = get_token(auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_get_token_invalid(self):
        auth_header = 'InvalidHeaderFormat'
        response = get_token(auth_header)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_decode_token_valid(self):
        token = encode_token(self.user)
        decoded_data = decode_token(token)
        self.assertIn('username', decoded_data)

    def test_check_access_valid_token(self):
        # Mock the get_token and decode_token functions
        with unittest.mock.patch('api.utils.get_token') as mock_get_token, \
             unittest.mock.patch('api.utils.decode_token') as mock_decode_token:

            # Set up the mock behavior
            mock_get_token.return_value = MagicMock(data={'token': 'valid_token'})
            mock_decode_token.return_value = {'username': 'test_user'}

            # Call the function
            result = check_access({'Authorization': 'Bearer valid_token'})

            # Assertions
            self.assertEqual(result, 'test_user')

    def test_check_access_invalid_token(self):
        # Mock the get_token function
        with unittest.mock.patch('api.utils.get_token') as mock_get_token:
            
            # Set up the mock behavior
            mock_get_token.return_value = MagicMock(data={'error': 'Invalid Authorization header'})

            # Call the function and expect an AuthenticationFailed exception
            with self.assertRaises(AuthenticationFailed):
                check_access({'Authorization': 'Bearer invalid_token'})

if __name__ == '__main__':
    unittest.main()
