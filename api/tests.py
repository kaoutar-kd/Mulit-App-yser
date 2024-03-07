import unittest
from unittest.mock import MagicMock, patch
from django.test import TestCase
from api.models import User, Role, SubscriptionPlan, Image as I
from .utils import check_access, encode_token, get_token, decode_token
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

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

User = get_user_model()


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.role = Role.objects.create(role='beta_player')
        self.user.role = self.role
        self.user.save()
        self.token = 'mocked_token'
        self.client.force_authenticate(user=self.user, token=self.token)
        self.fake_image_file = self.create_fake_image()
    
    def create_fake_image(self):
        # Create a fake image file in memory
        fake_image_data = BytesIO()
        fake_image = Image.new('RGB', (100, 100))
        fake_image.save(fake_image_data, format='PNG')
        fake_image_data.seek(0)

        # Django's SimpleUploadedFile to create a file-like object
        fake_uploaded_file = SimpleUploadedFile("fake_image.png", fake_image_data.read())

        return fake_uploaded_file


    @patch('api.views.check_access', return_value='test_user')
    def test_image_list_view(self, mock_check_access):
        # Mock data for the image
        image_data = {
            'uploaded_by': self.user.id,
            'image_file': self.fake_image_file,
            'description': 'Test Image'
        }

        # Test image creation
        response = self.client.post('/images/', data=image_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test getting the list of images
        response = self.client.get('/images/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    @patch('api.views.check_access', return_value='test_user')
    def test_image_details_view(self, mock_check_access):
        
        # Create an image
        image = I.objects.create(uploaded_by=self.user, image_file=self.fake_image_file, description='Test image')

        # Make a GET request to the image details view
        response = self.client.get(f'/images/{image.id}/')

        # Assert the response status and expectations
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('api.views.check_access', return_value='test_user')
    def test_image_update_view(self, mock_check_access):
        # Create an image
        image = I.objects.create(uploaded_by=self.user, image_file=self.fake_image_file, description='Test image')

        # Make a PUT request to update the image details
        response = self.client.put(f'/images/{image.id}/', {'description': 'Updated description'}, format='json')

        # Assert the response status and expectations
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    @patch('api.views.check_access', return_value='test_user')
    def test_image_delete_view(self, mock_check_access):
        # Create an image
        image = I.objects.create(uploaded_by=self.user, image_file=self.fake_image_file, description='Test image')

        # Make a DELETE request to delete the image
        response = self.client.delete(f'/images/{image.id}/')

        # Assert the response status and expectations
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_image_view_not_allowed(self):
        # Create a user with a role other than 'beta_player'
        user = User.objects.create_user(username='company_user', password='test_password')
        role = Role.objects.create(role='company_user')
        user.role = role
        user.save()

        # Authenticate the client
        client = APIClient()
        token = 'mocked_token'
        client.force_authenticate(user=self.user, token=self.token)

        # Attempt to make a POST request to the image upload view
        response = client.post('/images/', {'uploaded_by': user.id, 'image_file': self.fake_image_file, 'description': 'Test image upload'}, format='multipart')

        # Assert the response status and expectations
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        

    @patch('api.views.check_access', return_value='test_user')
    def test_subscription_plan_list_view(self, mock_check_access):
        # Mock data for the subscription plan
        subscription_plan_data = {
            'subscription_plan': 'Gold Plan',
            'features': 'Feature 1, Feature 2',
            'benefits': 'Benefit 1, Benefit 2'
        }

        # Test subscription plan creation
        response = self.client.post('/subscription-plans/', data=subscription_plan_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test getting the list of subscription plans
        response = self.client.get('/subscription-plans/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    @patch('api.views.check_access', return_value='test_user')
    def test_subscription_plan_get(self, mock_check_access):
        # Create a subscription plan for testing
        subscription_plan = SubscriptionPlan.objects.create(subscription_plan='Silver Plan', features='Feature X', benefits='Benefit X')

        # Make a POST request to create a subscription plan
        response = self.client.get(f'/subscription-plans/{subscription_plan.subscription_plan}/')

        # Assert the response status and expectations
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    @patch('api.views.check_access', return_value='test_user')
    def test_subscription_plan_update(self, mock_check_access):
        # Create a subscription plan for testing
        subscription_plan = SubscriptionPlan.objects.create(subscription_plan='Silver Plan', features='Feature X', benefits='Benefit X')

        # Make a PUT request to update the subscription plan
        response = self.client.put(f'/subscription-plans/{subscription_plan.subscription_plan}/', {'subscription_plan': 'Updated Plan', 'features': 'Updated Feature', 'benefits': 'Updated Benefit'})

        # Assert the response status and expectations
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    @patch('api.views.check_access', return_value='test_user')
    def test_subscription_plan_deletion(self, mock_check_access):
        # Create a subscription plan for testing
        subscription_plan = SubscriptionPlan.objects.create(subscription_plan='Bronze Plan', features='Feature Y', benefits='Benefit Y')

        # Make a DELETE request to delete the subscription plan
        response = self.client.delete(f'/subscription-plans/{subscription_plan.subscription_plan}/')

        # Assert the response status and expectations
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    @patch('api.views.check_access', return_value='test_user')
    def test_role_list_view(self, mock_check_access):
        # Test role creation
        response = self.client.post('/roles/', data={'role':'company_user'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test getting the list of roles
        response = self.client.get('/roles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('api.views.check_access', return_value='test_user')
    def test_role_get(self, mock_check_access):
        # Create a role for testing
        role = Role.objects.create(role='company_user')
        
        # Make a GET request to get details of a role
        response = self.client.get(f'/roles/{self.role.role}/')

        # Assert the response status and expectations
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('api.views.check_access', return_value='test_user')
    def test_role_update(self, mock_check_access):
        # Create a role for testing
        role = Role.objects.create(role='company_user')

        # Make a PUT request to update the role
        response = self.client.put(f'/roles/{role.role}/', {'role': 'growth_plan_subscriber'})

        # Assert the response status and expectations
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('api.views.check_access', return_value='test_user')
    def test_role_deletion(self, mock_check_access):

        # Make a DELETE request to delete the role
        response = self.client.delete(f'/roles/{self.role.role}/')

        # Assert the response status and expectations
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

if __name__ == '__main__':
    unittest.main()
