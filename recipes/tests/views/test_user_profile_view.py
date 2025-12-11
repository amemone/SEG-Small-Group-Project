from django.test import TestCase
from recipes.models import User, Recipe, Favourite, Follow
from django.urls import reverse

class ProfileDisplayViewTest(TestCase):

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        """Tests for the user profile view (viewing another user's profile)"""
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username='@janedoe')
        self.third_user = User.objects.get(username='@petrapickles')
        self.url = reverse('user_profile', kwargs={'username': self.second_user.username})
        self.client.login(username='@johndoe', password="Password123")

    def test_user_profile_url(self):
        expected_url = f'/profile/{self.second_user.username}/'
        self.assertEqual(self.url, expected_url)

    def user_is_following(viewer, profile_user):
        return Follow.objects.filter(
            follower=viewer,
            followee=profile_user
        ).exists()

    def test_user_profile_404_for_nonexistent_user(self):
        bad_url = reverse('user_profile', kwargs={'username': '@nouser'})
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)

    def test_user_profile_loads_successfully(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile.html')
        self.assertEqual(response.context['profile_user'], self.second_user)

    def test_following_count_starts_at_zero(self):
        following_count = Follow.objects.filter(follower=self.second_user).count()
        self.assertEqual(following_count, 0)

    def test_follower_count_starts_at_zero(self):
        follower_count = Follow.objects.filter(followee=self.second_user).count()
        self.assertEqual(follower_count, 0)

    def test_user_profile_shows_no_followers_or_following_initially(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["following"], 0)
        self.assertEqual(response.context["followers"], 0)

        self.assertEqual(list(response.context["user_followings"]), [])
        self.assertEqual(list(response.context["user_followers"]), [])

        self.assertContains(response, "<b>No Users</b>", html=True)

    def test_is_following_false_initially(self):
        response = self.client.get(self.url)
        self.assertFalse(response.context["is_following"])

    def test_is_following_true_when_user_follows_profile_user(self):
        Follow.objects.create(follower=self.user, followee=self.second_user)
        response = self.client.get(self.url)
        self.assertTrue(response.context["is_following"])

    def test_following_count_increases_when_following_someone(self):
        initial_count = Follow.objects.filter(follower=self.second_user).count()
        Follow.objects.create(follower=self.second_user, followee=self.third_user)
        new_count = Follow.objects.filter(follower=self.second_user).count()
        self.assertEqual(new_count, initial_count + 1)

    def test_follower_count_increases_when_getting_followed(self):
        initial_count = Follow.objects.filter(followee=self.second_user).count()
        Follow.objects.create(follower=self.user, followee=self.second_user)
        new_count = Follow.objects.filter(followee=self.second_user).count()
        self.assertEqual(new_count, initial_count + 1)

    def test_following_users_contains_expected_users(self):
        Follow.objects.get_or_create(follower=self.second_user, followee=self.third_user)
        following_users = [
            f.followee.username
            for f in Follow.objects.filter(follower=self.second_user).select_related('followee')
        ]
        self.assertIn(self.third_user.username, following_users)

    def test_followers_users_contains_expected_users(self):
        Follow.objects.get_or_create(follower=self.user, followee=self.second_user)
        followers = [
            f.follower.username
            for f in Follow.objects.filter(followee=self.second_user).select_related('follower')
        ]
        self.assertIn(self.user.username, followers)

    def test_unfollow_decreases_following_count_and_removes_user(self):
        follow_relationship = Follow.objects.create(
            follower=self.second_user,
            followee=self.third_user
        )
        initial_count = Follow.objects.filter(follower=self.second_user).count()
        follow_relationship.delete()
        new_count = Follow.objects.filter(follower=self.second_user).count()
        self.assertEqual(new_count, initial_count - 1)
        self.assertFalse(Follow.objects.filter(follower=self.second_user, followee=self.third_user).exists())

    def test_following_pagination_page_size(self):
        for i in range(7):
            following = User.objects.create_user(
                username=f'@u{i}',
                email=f'u{i}@example.com',
                password='Password123',
                first_name='User',
                last_name=str(i)
            )
            Follow.objects.create(follower=self.second_user, followee=following)

        response = self.client.get(self.url)
        page_object = response.context["user_followings"]
        self.assertEqual(len(page_object.object_list), 5)
        self.assertTrue(page_object.has_next)

    def test_follower_pagination_page_size(self):
        for i in range(7):
            follower = User.objects.create(
                username=f'@f{i}',
                email=f'f{i}@example.com',
                password='Password123',
                first_name='Follower',
                last_name=str(i)
            )
            Follow.objects.create(follower=follower, followee=self.second_user)

        response = self.client.get(self.url)
        page_obj = response.context["user_followers"]
        self.assertEqual(len(page_obj.object_list), 5)
        self.assertTrue(page_obj.has_next)

    def test_following_empty_page_shows_no_users_message(self):
        response = self.client.get(self.url + "?following_page=99")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<b>No Users</b>", html=True)

    def test_user_recipes_displayed(self):
        first_recipe = Recipe.objects.create(
            title='Vanilla Cake',
            description='eggs, milk, flour, sugar, vanilla, icing',
            user=self.second_user
        )
        second_recipe = Recipe.objects.create(
            title='Chocolate Cake',
            description='eggs, milk, flour, sugar, chocolate, icing',
            user=self.second_user
        )
        response = self.client.get(self.url)
        recipes_page = response.context['recipes']
        recipe_list = list(recipes_page)
        self.assertIn(first_recipe, recipe_list)
        self.assertIn(second_recipe, recipe_list)

    def test_user_recipe_pagination(self):
        recipes = []
        for i in range(13):
            recipe = Recipe.objects.create(
                title=f"Recipe {i}",
                description="test",
                user=self.second_user
            )
            recipes.append(recipe)

        response = self.client.get(self.url + "?page=1")
        first_page = response.context["recipes"]
        self.assertEqual(len(first_page), 9)
        self.assertTrue(first_page.has_next())
        response = self.client.get(self.url + "?page=2")
        second_page = response.context["recipes"]
        self.assertEqual(len(second_page), 4)
        self.assertFalse(second_page.has_next())