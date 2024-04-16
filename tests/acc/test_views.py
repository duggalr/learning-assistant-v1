from django.test import TestCase
from django.urls import reverse

from acc.models import CustomUser, AnonUser, UserOAuth


class LandingViewTest(TestCase):
    """
    Testing core functions when user visits landing page
    """

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_view_accessible_by_name(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'generic/landing.html')

    def test_view_creates_custom_user(self):
        response = self.client.get('')
 
        self.assertTrue(CustomUser.objects.exists())
        self.assertTrue(AnonUser.objects.exists())

        custom_user_obj = CustomUser.objects.first()
        self.assertIsNotNone(custom_user_obj.anon_user)
        self.assertIsNone(custom_user_obj.oauth_user)

    def test_view_populates_session(self):
        response = self.client.get('')

        custom_user_obj = CustomUser.objects.first()
        self.assertIn('custom_user_uuid', self.client.session)
        self.assertEqual(self.client.session['custom_user_uuid'], custom_user_obj.id)


class AboutViewTest(TestCase):
    """
    Testing core functions when user visits about page
    """

    pass



