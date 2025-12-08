"""Tests of the follow view."""
from django.test import TestCase
from recipes.models import User
from django.urls import reverse

class UserBrowseView(TestCase):
    """Tests of the user browse view"""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username='@janedoe')
        self.third_user = User.objects.get(username='@petrapickles')
        self.url = reverse('user_browse')

    def _search_and_get_results(self, search):
        response = self.client.get(self.url, {'q': search})
        return list(response.context['users'])

    def test_user_browse_url(self):
        self.assertEqual(self.url, '/user_browse/')

    def test_search_returns_correct_user(self):
        self.assertEqual(self._search_and_get_results('@johndoe'), [self.user])

    def test_search_with_spaces_returns_no_users(self):
        self.assertEqual(self._search_and_get_results(' '), [])

    def test_search_not_case_sensitive(self):
        self.assertEqual(self._search_and_get_results('@JAnEdOe'), [self.second_user])

    def test_search_works_with_spaces(self):
        self.assertEqual(self._search_and_get_results(' @petrapickles '), [self.third_user])

    def test_search_works_with_partial_name(self):
        self.assertEqual(self._search_and_get_results('john'), [self.user])

    def test_search_nonexistant_user(self):
        self.assertEqual(self._search_and_get_results('@doesntexist'), [])

    def test_search_multiple_users(self):
        self.assertEqual(self._search_and_get_results('doe'),[self.second_user, self.user])

