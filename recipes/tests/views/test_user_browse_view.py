"""Tests of the follow view."""
from django.test import TestCase
from recipes.models import User, Follow
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
        self.fourth_user = User.objects.create_user(
            username='@sophieharris',
            email='sophieharris@email.org',
            password='Password123',
            first_name='Sophie',
            last_name='Harris',
            )
        self.fifth_user = User.objects.create_user(
            username='@frankbegum',
            email='frankbegum@email.org',
            password='Password123',
            first_name='Frank',
            last_name='Begum'
            )
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

    def test_get_top_five_most_followed_users(self):
        Follow.objects.create(follower=self.second_user, followee=self.user)
        Follow.objects.create(follower=self.third_user, followee=self.user)
        Follow.objects.create(follower=self.fourth_user, followee=self.user)
        Follow.objects.create(follower=self.fifth_user, followee=self.user)

        Follow.objects.create(follower=self.user, followee=self.second_user)
        Follow.objects.create(follower=self.third_user, followee=self.second_user)
        Follow.objects.create(follower=self.fourth_user, followee=self.second_user)
        Follow.objects.create(follower=self.fifth_user, followee=self.second_user)


        Follow.objects.create(follower=self.user, followee=self.third_user)
        Follow.objects.create(follower=self.second_user, followee=self.third_user)
        Follow.objects.create(follower=self.fourth_user, followee=self.third_user)

        Follow.objects.create(follower=self.user, followee=self.fourth_user)
        Follow.objects.create(follower=self.second_user, followee=self.fourth_user)

        Follow.objects.create(follower=self.user, followee=self.fifth_user)

        response = self.client.get(reverse('user_browse'), {'q': ''})
        top_users = list(response.context['top_users'])
        self.assertEqual(len(top_users), 5)

        expected_order = [self.second_user, self.user, self.third_user, self.fourth_user, self.fifth_user]
        self.assertEqual(top_users, expected_order)

