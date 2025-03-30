from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.db.models import Q
from environs import Env

env = Env()
env.read_env()

# from users.models import email_superuser

SUPERUSER_USERNAME = env("SUPERUSER_USERNAME")
SUPERUSER_EMAIL = env("SUPERUSER_EMAIL")
SUPERUSER_PASSWORD = env("SUPERUSER_PASSWORD")

if not SUPERUSER_PASSWORD:
    raise ImproperlyConfigured("'SUPERUSER_PASSWORD' environment variable is unset")

User = get_user_model()

help_message = """
Sets up the DB, creating:
1) superuser with admin rights
"""


class Command(BaseCommand):
    """
    init: Command to set up database for the application
    """

    help = help_message

    def handle(self, *args, **kwargs):
        if not User.objects.filter(
            Q(email=SUPERUSER_EMAIL) | Q(username=SUPERUSER_USERNAME)
        ).exists():
            User.objects.create_superuser(
                username=SUPERUSER_USERNAME,
                email=SUPERUSER_EMAIL,
                password=SUPERUSER_PASSWORD,
                oauth_provider="email",
                role="admin",
            )
            print("Super-User Created!")
        print("Set-Up Complete!")
