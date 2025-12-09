from django.test import TestCase
from recipes.models import User, Recipe, Favourite, Follow
from django.urls import reverse

class ProfileDisplayViewTest(TestCase):

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        """Test of the profile display view """
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username='@janedoe')
        self.third_user = User.objects.get(username='@petrapickles')
        self.url = reverse('view_profile')
        self.client.login(username='@johndoe', password="Password123")

    def test_view_profile_url(self):
        self.assertEqual(self.url, '/view_profile/')

    def test_profile_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue("/log_in" in response.url)

    def test_following_count_starts_at_zero(self):
        following_count = Follow.objects.filter(follower = self.user).count()
        self.assertEqual(following_count, 0)

    def test_follower_count_starts_at_zero(self):
        follower_count = Follow.objects.filter(followee = self.user).count()
        self.assertEqual(follower_count, 0)

    def test_profile_view_shows_no_followers_or_following_initially(self):
        response = self.client.get(reverse('view_profile'))
        self.assertEqual(response.status_code,200)

        self.assertEqual(response.context["following"], 0)
        self.assertEqual(response.context["followers"], 0)

        self.assertEqual(list(response.context["user_followings"]), [])
        self.assertEqual(list(response.context["user_followers"]), [])
        
        self.assertContains(response, "<h5>No Users</h5>", html=True)

    def test_following_count_increases_when_following_someone(self):
        initial_count = Follow.objects.filter(follower = self.user).count()
        Follow.objects.create(follower = self.user, followee = self.second_user)
        new_count = Follow.objects.filter(follower = self.user).count()
        self.assertEqual(new_count, initial_count + 1)

    def test_follower_count_increases_when_getting_followed(self):
        initial_count = Follow.objects.filter(followee = self.second_user).count()
        Follow.objects.create(follower = self.user, followee = self.second_user)
        new_count = Follow.objects.filter(followee = self.second_user).count()
        self.assertEqual(new_count, initial_count + 1)

    def test_following_users_contains_and_excludes_expected_users(self):
        Follow.objects.get_or_create(follower = self.user, followee = self.second_user)
        Follow.objects.get_or_create(follower = self.user, followee = self.third_user)
        following_users = [
            user.followee.username
            for user in
            Follow.objects.filter(follower = self.user).select_related('followee')
        ]
        self.assertIn(self.second_user.username, following_users)
        self.assertIn(self.third_user.username, following_users)

    def test_unfollow_decreases_following_count_and_removes_user(self):
        follow_relationship = Follow.objects.filter(follower=self.user, followee=self.second_user).first()
        if follow_relationship is None:
            follow_relationship = Follow.objects.create(follower = self.user, followee = self.second_user)
        
        initial_count = Follow.objects.filter(follower = self.user).count()

        #unfollow
        follow_relationship.delete()
        new_count = Follow.objects.filter(follower = self.user).count()
        self.assertEqual(new_count, initial_count - 1)
        self.assertFalse(Follow.objects.filter(follower = self.user, followee= self.second_user).exists())

    def test_following_pagination_page_size(self):
        for i in range(7):
            following = User.objects.create_user(
                username=f'@user{i}',
                email=f'user{i}@example.com',
                password='Password123',
                first_name='User',
                last_name=str(i),
            )
            Follow.objects.create(follower = self.user, followee = following)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        page_object = response.context["user_followings"]
        self.assertEqual(len(page_object.object_list), 5)
        self.assertTrue(page_object.has_next)

    def test_follower_pagination_page_size(self):
        for i in range(7):
            follower = User.objects.create(
                username=f'@follower{i}',
                email=f'follower{i}@example.com',
                password='Password123',
                first_name='Follower',
                last_name=str(i),
            )
            Follow.objects.create(follower = follower, followee = self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        page_object = response.context["user_followers"]
        self.assertEqual(len(page_object.object_list), 5)
        self.assertTrue(page_object.has_next)

    def test_following_empty_page_shows_no_users_message(self):
        response = self.client.get(self.url + "?following_page=99")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h5>No Users</h5>", html=True)

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