import json
from django.test import TestCase
from django.urls import reverse

from acc.models import CustomUser, AnonUser, UserOAuth
from learning_assistant.models import PlaygroundCode


class PlaygroundViewTest(TestCase):
    """
    Testing core functions when user visits playground page
    """

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/playground/ide')
        self.assertEqual(response.status_code, 200)

    def test_view_accessible_by_name(self):
        response = self.client.get(reverse('playground'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('playground'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'assistant/playground.html')

    def test_view_save_code_error(self):
        response = self.client.post(reverse('save_user_playground_code'))
        response_dict = json.loads(response.content)
        self.assertEqual(response_dict['success'], False)
        self.assertEqual(response_dict['response'], 'User not found')

    def test_view_save_code_success(self):
        self.client.get('/playground/ide')

        response = self.client.post(reverse('save_user_playground_code'), data = {
            'cid': '',
            'user_code': 'print("hello world")',
        })
        
        response_dict = json.loads(response.content)
        self.assertEqual(response_dict['success'], True)
        self.assertIn('code_file_name',  response_dict)

        self.assertTrue(CustomUser.objects.exists())
        self.assertTrue(AnonUser.objects.exists())

        custom_user_obj = CustomUser.objects.first()
        pg_obj = PlaygroundCode.objects.first()

        self.assertEqual(pg_obj.user_obj, custom_user_obj)
    
    def test_view_save_existing_code_obj_success(self):
        self.client.get('/playground/ide')

        response = self.client.post(reverse('save_user_playground_code'), data = {
            'cid': '',
            'user_code': 'print("hello world")',
        })

        response_dict = json.loads(response.content)
        self.assertEqual(response_dict['success'], True)
        self.assertIn('code_file_name',  response_dict)

        custom_user_obj = CustomUser.objects.first()
        pg_obj = PlaygroundCode.objects.first()

        self.assertEqual(pg_obj.user_obj, custom_user_obj)

        response = self.client.post(reverse('save_user_playground_code'), data = {
            'cid': pg_obj.id,
            'user_code': 'print(4+4)',
        })
        self.assertEqual(response_dict['success'], True)

    # TODO: not testing since GPT's API will be called and unnecessary charges.. way to bypass?
    def test_view_playground_message(self):
        pass


class GeneralTutorViewTest(TestCase):
    """
    Testing core functions when user visits general tutor page
    """

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/chat/tutor')
        self.assertEqual(response.status_code, 200)

    def test_view_accessible_by_name(self):
        response = self.client.get(reverse('general_cs_tutor'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('general_cs_tutor'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'assistant/general_cs_tutor_chat.html')

    # TODO: not testing since GPT's API will be called and unnecessary charges.. way to bypass?
    def test_view_message(self):
        pass

