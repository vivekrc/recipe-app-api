from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from recipe.services import TagSerializer, Tag

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Tag API that is accessible to public without loggin in"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test if tag creation successful"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test for Tag API after authorization"""

    def setUp(self):
        valid_user = {
            'email': 'testy@tesla.com',
            'password': 'sssshhhh123'
        }
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(**valid_user)
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """See if retrieving tag names created
        by given user is successful"""
        valid_tag_1 = {
            'name': 'Vegan',
            'user': self.user
        }
        valid_tag_2 = {
            'name': 'Hot',
            'user': self.user
        }
        Tag.objects.create(**valid_tag_1)
        Tag.objects.create(**valid_tag_2)
        res = self.client.get(TAGS_URL)
        serialed_tags = TagSerializer(res.data, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialed_tags.data)

    def test_retrieve_tags_limited_to_user(self):
        """Ensure only the logged in user's tags are fetched"""
        valid_user_2_payload = {
            'email': 'other@tesla.com',
            'password': '123'
        }
        user_2 = get_user_model().objects.create_user(**valid_user_2_payload)
        tag_1_payload = {
            'name': 'Vegan',
            'user': self.user
        }
        tag_2_payload = {
            'name': 'Carni',
            'user': user_2
        }
        tag = Tag.objects.create(**tag_1_payload)
        Tag.objects.create(**tag_2_payload)
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)

    def test_create_tags_successful(self):
        """Test create new tag"""
        tag_payload = {
            'name': 'Vegan',
            'user': self.user
        }
        res = self.client.post(TAGS_URL, tag_payload)
        exists = Tag.objects.filter(
            user=self.user,
            name=tag_payload['name']
        ).exists()
        #
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
