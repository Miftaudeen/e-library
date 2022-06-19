from rest_framework import serializers

from account.models import User
from account.permission import get_as_perm
from account.perms_constants import PERM_CHOICES


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(required=True, choices=PERM_CHOICES)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'role']

    def save(self, username):
        user, _ = User.objects.update_or_create(
                                   email=self.validated_data.get('email'),
                                   defaults={
                                       'first_name': self.validated_data.get('first_name'),
                                       'last_name': self.validated_data.get('last_name'),
                                       'phone_number': self.validated_data.get('phone_number'),
                                       'username': username
                                   })
        return user


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'roles']
