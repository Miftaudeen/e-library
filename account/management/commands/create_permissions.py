from django.core.management.base import BaseCommand

from account.permission import create_default_permissions


class Command(BaseCommand):

    def handle(self, *args, **options):
        create_default_permissions()
        print("Permissions created successfully")
