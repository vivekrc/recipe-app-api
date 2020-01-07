from django.test import TestCase
from django.contrib.auth import get_user_model
from .. import models
# from app.core import models


def sample_user_create(email="test@tesla.com", password="teslaaa!"):
    user = get_user_model().objects.create_user(email=email, password=password)
    return user


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """ Test creating an User with an Email is successful. """
        email = "vivek@tessel.tech"
        password = "Qwerty@123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEquals(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        email = "vivek@TeSSel.teCh"
        user = get_user_model().objects.create_user(
            email=email,
            password='test123'
        )
        self.assertEquals(user.email, email.lower())

    def test_new_user_with_invalid_email(self):
        """Check if a blank email or an invalid email
        cannot be used to create user"""
        with self.assertRaises(ValueError):
            email = ""
            get_user_model().objects.create_user(
                email=email,
                password='test123'
            )

    def test_create_super_user(self):
        """Test creating a new super user"""
        email = "vivek@tessel.tech"
        password = "Qwerty@123"
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Ensure the creation of tag happens through the model methods"""
        sample_user = sample_user_create()
        tag = models.Tag.objects.create(
            user=sample_user,
            name="Vegan",
        )
        self.assertEqual(str(tag), tag.name)
