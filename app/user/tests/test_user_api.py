from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

#
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """"Tests for User API (Public)"""

    def setUp(self):
        """Instantiate a simulated REST API Test client"""
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Create a a valid user
        1. Check if the user exists
        2. Check if given password is the one that is stored in hashed form
        3. Ensure password is not leaking
        """
        valid_user_payload = {
            'email': 'test@tessel.tech',
            'name': 'tester guy',
            'password': 'ssshhh123'
        }
        res = self.client.post(CREATE_USER_URL, valid_user_payload)
        created_user_data = get_user_model().objects.get(**res.data)
        print("\n\n------->>>>>>", res)
        self.assertEquals(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            created_user_data.check_password(valid_user_payload['password'])
        )
        self.assertNotIn('password', res.data)

    def test_user_exists_fails(self):
        """Create a user and then to create another use with same email
        1. This operation should fail
        2. There should be appropriate error message
        """
        valid_user_payload = {
            'email': 'test@tessel.tech',
            'name': 'tester guy',
            'password': 'ssshhh123'
        }
        valid_user_payload_duplicate = {
            'email': 'test@tessel.tech',
            'name': 'tester boy',
            'password': 'ssssshhh123'
        }
        create_user(**valid_user_payload)
        res2 = self.client.post(CREATE_USER_URL, valid_user_payload_duplicate)

        self.assertEquals(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_generated_valid_user(self):
        """"Test if token generated for user login"""
        payload = {
            'email': 'test@tessel.tech',
            'password': 'ssshhh123'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_token_not_generated_invalid_user(self):
        """"Test if token generated for user login"""
        valid_user = {
            'email': 'test@tessel.tech',
            'password': 'ssshhh123'
        }
        incorrect_payload = {
            'email': 'test@tessel.tech',
            'password': 'wrongpassword'
        }
        create_user(**valid_user)
        res = self.client.post(TOKEN_URL, incorrect_payload)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_token_not_generated_if_no_user(self):
        """ Ensure no token is generated if the user
        does not exist in the database"""
        incorrect_payload = {
            'email': 'nonexistantusername@tessel.tech',
            'password': 'ssshhh123'
        }
        res = self.client.post(TOKEN_URL, incorrect_payload)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_token_not_generated_if_empty_password(self):
        """ Ensure no token is generated if the password field is empty"""
        valid_user = {
            'email': 'test@tessel.tech',
            'password': 'ssshhh123'
        }
        incorrect_payload = {
            'email': 'nonexistantusername@tessel.tech',
            'password': ''
        }
        create_user(**valid_user)
        res = self.client.post(TOKEN_URL, incorrect_payload)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_retrive_user_unauthorized(self):
        """Ensure people who are not logged in don't have access to the API"""
        res = self.client.get(ME_URL)
        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test cases for logged in users"""

    def setUp(self):
        valid_user_info = {
            'email': 'test@tessel.tech',
            'name': 'tester guy',
            'password': 'ssshhh123'
        }
        self.user = create_user(**valid_user_info)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_profile_not_allowed(self):
        """Ensure user does not post on the /me endpoint"""
        random_user_payload = {
            'email': 'tester@tessel.tech',
            'name': 'tester gal',
            'password': 'quiet123'
        }
        res = self.client.post(ME_URL, random_user_payload)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        update_payload = {
            'name': 'my name changed',
            'password': 'newpasswordaswell'
        }
        res = self.client.patch(ME_URL, update_payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, update_payload["name"])
        self.assertTrue(self.user.check_password(update_payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
