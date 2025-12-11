"""
Management command to seed the database with demo data.

This command creates a small set of named fixture users and then fills up
to ``USER_COUNT`` total users using Faker-generated data. Existing records
are left untouched—if a create fails (e.g., due to duplicates), the error
is swallowed and generation continues.
"""



from faker import Faker
from random import randint, random, sample, choice
from django.core.management.base import BaseCommand, CommandError
from recipes.models import User, Follow, Recipe, Tag


user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]


class Command(BaseCommand):
    """
    Build automation command to seed the database with data.

    This command inserts a small set of known users (``user_fixtures``) and then
    repeatedly generates additional random users until ``USER_COUNT`` total users
    exist in the database. Each generated user receives the same default password.

    Attributes:
        USER_COUNT (int): Target total number of users in the database.
        DEFAULT_PASSWORD (str): Default password assigned to all created users.
        NUMBER_OF_FOLLOWS (int): Target number of users each user is following.
        NUMBER_OF_RECIPES (tuple): Range of number of recipes each user will create.
        NUMBER_OF_INGREDIENTS (tuple): Range of number of ingredients each recipe will have.
        NUMBER_OF_TAGS (tuple): Range of number of tags each recipe will have.
        help (str): Short description shown in ``manage.py help``.
        faker (Faker): Locale-specific Faker instance used for random data.
    """

    USER_COUNT = 200
    DEFAULT_PASSWORD = 'Password123'
    NUMBER_OF_FOLLOWS = 10
    NUMBER_OF_RECIPES = (0,5)
    NUMBER_OF_INGREDIENTS = (2,8)
    NUMBER_OF_TAGS = (0,4)
    help = 'Seeds the database with sample data'

    def __init__(self, *args, **kwargs):
        """Initialize the command with a locale-specific Faker instance."""
        super().__init__(*args, **kwargs)
        self.faker = Faker('en_GB')
        self.dishes = [
            "Spaghetti Carbonara", "Chicken Tikka Masala", "Beef Bourguignon", "Sushi Rolls",
            "Margherita Pizza", "Caesar Salad", "Beef Tacos", "Pad Thai", "Moussaka", "Ratatouille",
            "Pho", "Bibimbap", "Fish and Chips", "Paella", "Goulash", "Butter Chicken",
            "Lamb Kofta", "Falafel Wrap", "Shakshuka", "Ramen", "Spring Rolls", "Dumplings",
            "Beef Stir Fry", "Grilled Salmon", "Eggplant Parmesan", "Chicken Curry", "Burger",
            "Lasagna", "Tomato Soup", "Greek Salad", "Chicken Wings", "Fried Rice",
            "Beef Bulgogi", "Chicken Shawarma", "Clam Chowder", "Guacamole", "Nachos",
            "Hummus", "Tandoori Chicken", "Chili con Carne", "Fajitas", "Enchiladas",
            "Ceviche", "Couscous", "Gyoza", "Tempura", "Sashimi", "Teriyaki Chicken",
            "Peking Duck", "Mapo Tofu", "Kimchi", "Jambalaya", "Gumbo", "Crawfish Etouffee",
            "Poutine", "Shepherd's Pie", "Bangers and Mash", "Corned Beef", "Irish Stew",
            "Beef Wellington", "Yorkshire Pudding", "Black Forest Cake", "Tiramisu",
            "Crème Brûlée", "Apple Pie", "Cheesecake", "Brownies", "Ice Cream Sundae"
        ]
        self.ingredients = [
            "garlic", "olive oil", "onion", "tomatoes", "eggs",
            "flour", "butter", "sugar", "salt", "black pepper",
            "parmesan cheese", "basil", "chicken breast", "ground beef",
            "rice", "pasta", "milk", "heavy cream", "lemons",
            "bell peppers", "carrots", "celery", "potatoes", "spinach",
            "mushrooms", "ginger", "soy sauce", "cilantro", "cumin",
            "paprika", "cinnamon", "nutmeg", "thyme", "rosemary",
            "oregano", "chili powder", "cayenne pepper", "honey",
            "maple syrup", "vanilla extract", "baking powder",
            "baking soda", "chocolate chips", "walnuts", "almonds",
            "coconut milk", "quinoa", "lentils", "avocado", "feta cheese"
        ]
        self.visibility = [
            'public',
            'friends',
            'me'
        ]
        self.difficulty = [
            'Beginner',
            'Intermediate',
            'Advanced'
        ]
        self.time = [
            '5',
            '10',
            '15',
            '20',
            '30',
            '45',
            '60',
            '90'
        ]
        self.default_tags = [
            Tag.objects.get(name="Vegetarian"),
            Tag.objects.get(name="Vegan"),
            Tag.objects.get(name="Dairy-Free"),
            Tag.objects.get(name="Gluten-Free"),
            Tag.objects.get(name="High Protein"),
            Tag.objects.get(name="Halal"),
            Tag.objects.get(name="Nut-Free"),
        ]

    def handle(self, *args, **options):
        """
        Django entrypoint for the command.

        Runs the full seeding workflow and stores ``self.users`` for any
        post-processing or debugging (not required for operation).
        """
        self.create_users()
        self.users = User.objects.all()

    def create_users(self):
        """
        Create fixture users and then generate random users up to USER_COUNT, as well as
        creating follow relations for each user, as well as recipes for each user.

        The process is idempotent in spirit: attempts that fail (e.g., due to
        uniqueness constraints on username/email) are ignored and generation continues.
        """
        self.generate_user_fixtures()
        self.generate_random_users()
        self.create_all_follows(self.NUMBER_OF_FOLLOWS)
        self.create_all_recipes(self.NUMBER_OF_RECIPES, self.NUMBER_OF_INGREDIENTS, self.NUMBER_OF_TAGS)

    def generate_user_fixtures(self):
        """Attempt to create each predefined fixture user."""
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        """
        Generate random users until the database contains USER_COUNT users.

        Prints a simple progress indicator to stdout during generation.
        """
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        """
        Generate a single random user and attempt to insert it.

        Uses Faker for first/last names, then derives a simple username/email.
        """
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})
       
    def try_create_user(self, data):
        """
        Attempt to create a user and ignore any errors.

        Args:
            data (dict): Mapping with keys ``username``, ``email``,
                ``first_name``, and ``last_name``.
        """
        try:
            self.create_user(data)
        except:
            pass

    def create_user(self, data):
        """
        Create a user with the default password.

        Args:
            data (dict): Mapping with keys ``username``, ``email``,
                ``first_name``, and ``last_name``.
        """
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )

    def create_all_follows(self, follow_amount):
        """
        Create follow relationships for every user.

        Args:
            follow_amount (int): How many users each user will attempt to follow.
        """
        all_users = User.objects.all()
        for user in all_users:
            print(f"Creating followers for {user.username}", end='\r')
            self.create_follow(user, follow_amount)

    def create_follow(self, user, follow_amount):
        """
        Create follow relationships for one user.

        Args:
            user (User): the user that is doing the following.
            follow_amount (int): How many users the user will attempt to follow.
        """
        all_users = User.objects.all().exclude(pk=user.pk)
        users_to_follow = sample(
            list(all_users),
            follow_amount
        )
        for followee in users_to_follow:
            Follow.objects.create(follower=user, followee=followee)

    def create_all_recipes(self, recipe_amount, ingredient_amount, tag_amount):
        """
        Create recipes for all users.

        Args:
            recipe_amount (tuple): the minimum and maximum recipes a user will create.
            ingredient_amount (tuple): the mimimum and maximum ingredients a recipe will have.
            tag_amount (tuple): the minimum and maximum tags a recipe will have.
        """
        all_users = User.objects.all()
        for user in all_users:
            print(f"Creating recipes for {user.username}", end='\r')
            self.create_recipe(user, recipe_amount, ingredient_amount, tag_amount)

    def create_recipe(self, user, recipe_amount, ingredient_amount, tag_amount):
        """
        Create recipes for one user.

        Args:
            user (User): the user that recipes are being created for.
            recipe_amount (tuple): the minimum and maximum recipes a user will create.
            ingredient_amount (tuple): the mimimum and maximum ingredients a recipe will have.
            tag_amount (tuple): the minimum and maximum tags a recipe will have.
        """
        for i in range(randint(recipe_amount[0], recipe_amount[1])):
            recipe = Recipe.objects.create(
                title = choice(self.dishes),
                description = self.faker.sentence(nb_words=10),
                ingredients = self.select_ingredients(ingredient_amount),
                user = user,
                visibility = choice(self.visibility),
                difficulty = choice(self.difficulty),
                time_required = choice(self.time)
            )

            tags = sample(self.default_tags, randint(tag_amount[0], min(tag_amount[1], len(self.default_tags))))
            recipe.tags.add(*tags)
            recipe.save()

    def select_ingredients(self, ingredient_amount):
        """
        Construct a list of ingredients from the ingredients list.

        Args:
            ingredient_amount (tuple): the mimimum and maximum ingredients a recipe will have.

        Returns:
            str: A list of ingredients separated by \n.
        """
        ingredients = []
        for i in range(randint(ingredient_amount[0], ingredient_amount[1])):
            ingredients.append(choice(self.ingredients))
        return "\n".join(ingredients)



def create_username(first_name, last_name):
    """
    Construct a simple username from first and last names.

    Args:
        first_name (str): Given name.
        last_name (str): Family name.

    Returns:
        str: A username in the form ``@{firstname}{lastname}`` (lowercased).
    """
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    """
    Construct a simple example email address.

    Args:
        first_name (str): Given name.
        last_name (str): Family name.

    Returns:
        str: An email in the form ``{firstname}.{lastname}@example.org``.
    """
    return first_name + '.' + last_name + '@example.org'

