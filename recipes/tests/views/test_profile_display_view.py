from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe, Favourite, Follow

class ProfileDisplayViewTest(TestCase):
    """Tests of the profile display view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('view_profile')

    def test_profile_display_url(self):
        self.assertEqual(self.url, '/view_profile/')

    def test_profile_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue("/log_in" in response.url)

    def test_profile_display_shows_follow_counts(self):
        other = User.objects.get(username='@janedoe')
        Follow.objects.create(follower=self.user, followee=other)
        third = User.objects.create(username='@third', email='third@test.com')
        third.set_password('Password123')
        third.save()
        Follow.objects.create(follower=third, followee=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.context["following"], 1)
        self.assertEqual(response.context["followers"], 1)
        self.assertIn(other, response.context["user_followings"])
        self.assertIn(third, response.context["user_followers"])

    def test_profile_display_loads_successfully(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_profile.html')
        self.assertIn('favourites', response.context)

    def test_profile_displays_favourites_in_order(self):
        first_recipe = Recipe.objects.create(
            title='Vanilla Cake',
            description='eggs, milk, flour, sugar, vanilla, icing',
            user=self.user
        )
        second_recipe = Recipe.objects.create(
            title='Chocolate Cake',
            description='eggs, milk, flour, sugar, chocolate icing',
            user=self.user
        )
        third_recipe = Recipe.objects.create(
            title='Caramel Brownies',
            description='eggs, milk, flour, sugar, cocoa powder, caramel',
            user=self.user
        )
        Favourite.objects.create(user=self.user, recipe=second_recipe)
        Favourite.objects.create(user=self.user, recipe=third_recipe)
        Favourite.objects.create(user=self.user, recipe=first_recipe)
        response = self.client.get(self.url)
        favourites_page = response.context['favourites']
        favourites = list(favourites_page)
        self.assertEqual(favourites, [first_recipe, third_recipe, second_recipe])

    def test_profile_shows_no_favourites_when_user_has_none(self):
        response = self.client.get(self.url)
        favourites_page = response.context['favourites']
        favourites = list(favourites_page)
        self.assertEqual(favourites, [])

    def test_profile_favourites_pagination(self):
        recipes = []
        for i in range(13):
            recipe = Recipe.objects.create(
                title=f"Recipe {i}",
                description="test",
                user=self.user
            )
            recipes.append(recipe)

        for recipe in recipes:
            Favourite.objects.create(user=self.user, recipe=recipe)
        response = self.client.get(self.url + "?page=1")
        first_page = response.context["favourites"]
        self.assertEqual(len(first_page), 12)
        self.assertTrue(first_page.has_next())
        response = self.client.get(self.url + "?page=2")
        second_page = response.context["favourites"]
        self.assertEqual(len(second_page), 1)
        self.assertFalse(second_page.has_next())