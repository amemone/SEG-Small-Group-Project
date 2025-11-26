from django.template import Context, Template
from recipes.models.recipes import Recipe
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
{"id": "55326", "variant": "code/python", "title": "test_recipe_delete_fill_in"}

User = get_user_model()  # Use the custom user model


class RecipeDeleteViewTest(TestCase):
    def setUp(self):
        # Use the user you already fetched
        self.user = User.objects.create_user(
            username='@johndoe',
            password='pass123',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org'
        )
        self.other_user = User.objects.create_user(
            username='@janedoe',
            password='pass123',
            first_name='Jane',
            last_name='Doe',
            email='janedoe@example.org'
        )

        self.url = reverse('recipe_delete')
        self.form_input = {
            'first_name': 'John2',
            'last_name': 'Doe2',
            'username': '@johndoe2',
            'email': 'johndoe2@example.org',
        }

        # recipe example
        self.recipe = Recipe.objects.create(
            title="Test Recipe", user=self.user)

        self.client = Client()

    def render_delete_form(self, user):
        """Helper to simulate template rendering of delete button (I had to google this)"""
        template = Template("""
        {% if recipe.user == user %}
            <form method="post" action="{% url 'recipe_delete' %}">
                <input type="hidden" name="recipe_id" value="{{ recipe.id }}">
                <button type="submit">Delete</button>
            </form>
        {% endif %}
        """)
        context = Context({'recipe': self.recipe, 'user': user})
        return template.render(context)

    def test_delete_button_visible_to_owner(self):
        rendered = self.render_delete_form(self.user)
        self.assertIn('name="recipe_id"', rendered)
        self.assertIn('<button type="submit">Delete</button>', rendered)

    def test_delete_button_not_visible_to_other_user(self):
        rendered = self.render_delete_form(self.other_user)
        self.assertNotIn('name="recipe_id"', rendered)
        self.assertNotIn('<button type="submit">Delete</button>', rendered)

    def test_owner_can_delete_recipe(self):
        self.client.login(username='@johndoe', password='pass123')
        response = self.client.post(self.url, {'recipe_id': self.recipe.id})

        # The recipe should be deleted
        with self.assertRaises(Recipe.DoesNotExist):
            Recipe.objects.get(id=self.recipe.id)

        self.assertRedirects(response, reverse('dashboard'))
