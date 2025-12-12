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
from recipes.models.comment import Comment, Notification
from recipes.models.favourite import Favourite


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
            "Shepherd's Pie", "Irish Stew", "Beef Wellington", "Yorkshire Pudding", "Black Forest Cake", 
            "Tiramisu", "Crème Brûlée", "Apple Pie", "Cheesecake", "Brownies", "Ice Cream Sundae"
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
        self.dish_descriptions = {
            "Spaghetti Carbonara": "Discover how to make traditional spaghetti carbonara. This classic Italian pasta dish combines a silky cheese sauce with crisp pancetta and black pepper.",
            "Chicken Tikka Masala": "Get this chicken tikka masala cooking in the morning and have dinner waiting for you when you get in – it's perfect for a cold winter evening.",
            "Beef Bourguignon": "The secret to this rich beef casserole is to use all wine and no stock. Our ultimate beef bourguignon recipe is an instant comforting classic, full of satisfying flavours.",
            "Sushi Rolls": "Try smoked salmon in these sushi-style brown rice bites. If you prefer the real thing, add thin slices of sushi-grade tuna or salmon instead",
            "Margherita Pizza": "Even a novice cook can master the art of perfect pizza with our step-by-step guide. This homemade pizza recipe features a simple pizza dough and toppings.",
            "Caesar Salad": "A classic chicken salad recipe, featuring crunchy croutons and a creamy, garlic dressing. Ideal for lunch with friends",
            "Beef Tacos": "Make these vibrant beef tacos with a pack of mince. Go to the extra effort of making your own spice mix for even more flavour, and use soft tortillas",
            "Pad Thai": "Toss chicken with rice noodles and stir-fried veg to create a deliciously healthy dinner. There's a vegan option, too, which uses peanut butter (see tip, below)",
            "Moussaka": "Make our easy moussaka for an instant crowd pleaser. This classic Greek dish of layered thinly sliced potato, aubergine and lamb is topped with a creamy béchamel sauce.",
            "Ratatouille": "Seasonal vegetables are all slow-cooked together in a dish that truly celebrates summer. Serve with bread, or for a more substantial meal, as a side with barbecued or roasted meat or fish",
            "Pho": "Try making this delicious Vietnamese broth as something different for dinner. It's full of classic Asian flavours along with sirloin steak and noodles",
            "Bibimbap": "A Korean rice bowl packed with goodies - sliced steak, fried egg, spinach, carrot and toasted sesame seeds, plus gochujang or sriracha for a chilli kick",
            "Fish and Chips": "Skip the takeaway, and spend a little effort perfecting fish & chips at home – you'll be rewarded with crisp, deeply golden fish and moreish chips",
            "Paella": "Whip up this easy version of the traditional Spanish seafood dish using storecupboard staples. Add extras to paella rice such as chorizo and peas if you like",
            "Goulash": "With fall-apart beef, tomatoes and peppers in a creamy, rich stew, our slow-cooker goulash recipe couldn't be easier or more comforting",
            "Butter Chicken": "Fancy a healthy version of your favourite Friday night curry? Try our easy butter chicken – the meat can be marinaded the day before so you can get ahead on your prep",
            "Lamb Kofta": "With only five ingredients, these lean meatballs couldn't be any easier to make.",
            "Falafel Wrap": "Make our 5-ingredient falafels to create these ultimate veggie wraps, packed with falafels, avocado and herbs and topped with a delicious tahini sauce",
            "Shakshuka": "Start the day on a lighter note with this satisfying shakshuka, a wonderful pan full of tomatoes, pepper, spinach and eggs. It packs in four of your 5-a-day",
            "Ramen": "Use chicken, ramen noodles, spinach, sweetcorn and eggs to make this warming soup, ideal for when you crave something comforting yet light and wholesome.",
            "Spring Rolls": "Make these spring rolls in the air fryer for an easy and fun vegetarian lunch for the family. Serve with the sweet chilli sauce for dipping",
            "Dumplings": "Take your stew or casserole to the next level with our easy dumplings. Add them to your dish for instant family-friendly comfort food in a flash",
            "Beef Stir Fry": "Our quick and easy beef stir-fry can be whipped up in one pan using just a handful of ingredients. This takeaway classic is perfect for a family midweek meal.",
            "Grilled Salmon": "Grill healthy fish with chipotle spice then serve with cabbage salad, coriander and chilli in soft tortillas",
            "Eggplant Parmesan": "Every Italian cook has their own version of this classic aubergine dish. It's even better made a day ahead",
            "Chicken Curry": "Cook our easy, healthy chicken curry in under an hour. Serve this replica of your favourite takeaway dish with fluffy rice for a wholesome family meal",
            "Burger": "Struggle to find dishes to cook that take very little time but the whole family will love? Look no further than these chicken and halloumi burgers",
            "Lasagna": "Layers of tender pasta, rich meat sauce and melted cheese come together in this classic, comforting baked lasagna.",
            "Tomato Soup": "Smooth and creamy tomato soup made with ripe tomatoes and a touch of cream. Perfect paired with warm crusty bread.",
            "Greek Salad": "A refreshing mix of cucumbers, tomatoes, olives and feta tossed in a bright lemon-oregano dressing. Ideal for a light lunch or side.",
            "Chicken Wings": "Crispy baked chicken wings tossed in your favourite sauce – from spicy buffalo to sweet honey garlic.",
            "Fried Rice": "A quick and versatile fried rice packed with vegetables and your choice of chicken, shrimp or tofu for an easy weeknight meal.",
            "Beef Bulgogi": "Thinly sliced beef marinated in a sweet and savoury Korean sauce, then grilled until caramelised and served with steamed rice.",
            "Chicken Shawarma": "Tender spiced chicken roasted until golden, wrapped in warm pita with crisp vegetables and creamy garlic sauce.",
            "Clam Chowder": "A creamy, comforting chowder made with tender clams, potatoes and herbs – perfect for chilly evenings.",
            "Guacamole": "A smooth and zesty avocado dip with lime, cilantro and onion. Ideal for dipping or spreading on warm tortillas.",
            "Nachos": "Crisp tortilla chips loaded with melted cheese, beans and jalapeños. Add salsa and sour cream for the perfect sharing platter.",
            "Hummus": "A velvety chickpea dip blended with tahini, garlic and lemon. Delicious with pita bread or raw vegetables.",
            "Tandoori Chicken": "Juicy chicken marinated in yoghurt and bold Indian spices, then roasted until smoky and deeply flavourful.",
            "Chili con Carne": "A hearty, warming chili made with beef, beans and aromatic spices. Serve with rice or crusty bread.",
            "Fajitas": "Sizzling strips of chicken or beef with peppers and onions, served with warm tortillas and your favourite toppings.",
            "Enchiladas": "Soft tortillas filled with seasoned meat or beans, smothered in rich sauce and cheese, then baked until bubbling.",
            "Ceviche": "Fresh fish marinated in citrus juice with onions, herbs and chilli for a bright, refreshing dish.",
            "Couscous": "Fluffy couscous tossed with roasted vegetables and herbs. Perfect as a light lunch or side dish.",
            "Gyoza": "Crispy-bottomed Japanese dumplings filled with savoury pork or vegetables, served with a tangy dipping sauce.",
            "Tempura": "Lightly battered vegetables or seafood fried until crisp and golden. Great as a starter or side.",
            "Sashimi": "Thin slices of premium raw fish served with soy sauce and wasabi for a clean, elegant dish.",
            "Teriyaki Chicken": "Juicy chicken glazed in a shiny, sweet and savoury teriyaki sauce. Lovely with steamed rice and greens.",
            "Peking Duck": "Crispy roasted duck carved and served with pancakes, scallions and rich hoisin sauce.",
            "Mapo Tofu": "A spicy Sichuan classic featuring silky tofu and ground meat simmered in a fiery, fragrant sauce.",
            "Kimchi": "Traditional Korean fermented cabbage with a bold, tangy and spicy flavour. A perfect side or topping.",
            "Jambalaya": "A hearty Cajun rice dish cooked with chicken, sausage and spices for a comforting and flavour-packed meal.",
            "Gumbo": "A rich Louisiana stew with sausage, seafood and okra served over warm rice. Deep, smoky and satisfying.",
            "Crawfish Etouffee": "A spicy, buttery Louisiana crawfish stew served with rice, full of Creole flavours.",
            "Shepherd's Pie": "A comforting dish of minced meat and tender vegetables topped with creamy mashed potatoes and baked until golden.",
            "Irish Stew": "A rustic stew of lamb, potatoes and carrots slow-cooked until tender and full of homely flavour.",
            "Beef Wellington": "Tender beef fillet wrapped in mushroom duxelles and golden puff pastry for an elegant dinner centrepiece.",
            "Yorkshire Pudding": "Light and airy baked batter perfect alongside roasted meats and rich gravy.",
            "Black Forest Cake": "Layers of chocolate sponge, cherries and whipped cream come together in this indulgent German classic.",
            "Tiramisu": "Creamy Italian dessert made with coffee-soaked ladyfingers, mascarpone and a dusting of cocoa.",
            "Crème Brûlée": "Silky vanilla custard topped with a crisp, caramelised sugar crust for a luxurious dessert.",
            "Apple Pie": "Classic spiced apple filling wrapped in a buttery, flaky crust. Best served warm with ice cream.",
            "Cheesecake": "A rich, creamy cheesecake baked on a crisp biscuit base. Perfect for any occasion.",
            "Brownies": "Fudgy chocolate brownies with a soft centre and crackly top – irresistible and easy to share.",
            "Ice Cream Sundae": "Scoops of ice cream topped with chocolate sauce, nuts and cherries for a nostalgic, crowd-pleasing treat."
        }
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
        self.sample_comments = [
            "Looks yummy!", "Can't wait to try this.", "Delicious!", 
            "My favorite!", "This recipe is amazing.", "Perfect for dinner.",
            "Easy and tasty!", "I love this!", "So good!", "Will make again.", 
            "It's satisfactory", "Too time consuming", "My kids did not like this",
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

    def create_comments(self, recipe, max_comments=5):
        num_comments = randint(0, max_comments)
        users = list(User.objects.all())
        
        for _ in range(num_comments):
            user = choice(users)
            Comment.objects.create(
                recipe=recipe,
                user=choice(users),  # random user
                text=choice(self.sample_comments)
            )

            if user != recipe.user:
                Notification.objects.create(
                    user=recipe.user,
                    text=f"{user.username} commented on your recipe '{recipe.title}'",
                    link=f"/recipe/{recipe.id}/"
                )

    def create_favourites(self, recipe, max_favourites=10):
        """
        Randomly favourite a recipe for a few users.

        Args:
            recipe (Recipe): Recipe instance.
            max_favourites (int): Max number of favourites to add.
        """
        users = list(User.objects.all())
        num_favourites = randint(0, min(max_favourites, len(users)))
        selected_users = sample(users, num_favourites)

        for user in selected_users:
            Favourite.objects.get_or_create(user=user, recipe=recipe)

            if user != recipe.user:
                Notification.objects.create(
                    user=recipe.user,
                    text=f"{user.username} favourited your recipe '{recipe.title}'",
                    link=f"/recipe/{recipe.id}/"
                )
            
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
            title = choice(self.dishes)
            description = self.dish_descriptions.get(title, "A delicious recipe!")

            recipe = Recipe.objects.create(
                title=title,
                description=description,
                ingredients=self.select_ingredients(ingredient_amount),
                user=user,
                visibility=choice(self.visibility),
                difficulty=choice(self.difficulty),
                time_required=choice(self.time)
            )

            tags = sample(self.default_tags, randint(tag_amount[0], min(tag_amount[1], len(self.default_tags))))
            recipe.tags.add(*tags)
            recipe.save()

            self.create_comments(recipe, max_comments=10)
            self.create_favourites(recipe, max_favourites=50)

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

