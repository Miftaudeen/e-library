import os

from django.core.management import BaseCommand

from account.models import User
from account.permission import get_permission
from account.perms_constants import MANAGER_NAME, ADMIN_NAME


class Command(BaseCommand):

    def handle(self, *args, **options):
        if User.objects.count() == 0:
            username = os.environ.get('username')
            password = os.environ.get('password')
            if username and password:
                email = f"{username}@mailinator.com"
                print('Creating account for %s (%s)' % (username, email))
                admin = User.objects.create_superuser(email=email, username=username, password=password)
                admin.is_active = True
                admin.is_admin = True
                admin.user_permissions.add(get_permission(MANAGER_NAME))
                admin.user_permissions.add(get_permission(ADMIN_NAME))
                admin.save()
        else:
            print('Admin accounts can only be initialized if no Accounts exist')