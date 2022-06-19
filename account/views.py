from django.contrib.auth.models import Permission
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView, get_object_or_404, ListAPIView
# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import User
from account.permission import get_as_perm, get_permission, AdminPermission, get_user_permissions
from account.perms_constants import ADMIN_NAME, USER_PERMS_NAMES, MANAGER_NAME
from account.serializers import UserSerializer, UserListSerializer
from utils.utility import generate_username


class AddUser(CreateAPIView):
    model = User
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, AdminPermission]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = generate_username(serializer.validated_data['first_name'], serializer.validated_data['last_name'])
            while User.objects.filter(username=username).exists():
                username = generate_username(serializer.validated_data['first_name'], serializer.validated_data['last_name'],
                                             more=True)
            user = serializer.save(username=username)
            user_role = serializer.validated_data.get('role')
            if user_role == ADMIN_NAME:
                for perm in USER_PERMS_NAMES:
                    user.user_permissions.add(get_permission(perm))
                user.is_staff = True
            else:
                user.user_permissions.add(get_permission(user_role))
            user.set_password("TempP@552022")
            user.save()
            serializer = UserListSerializer(instance=user)
            return Response({"message": "Registration Successful", "responseCode": "100", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"message": "Registration Error", "responseCode": "101",
                         "errors": serializer.errors}, status=status.HTTP_200_OK)


class ManagerApiListView(ListAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def list(self, request, *args, **kwargs):
        managers = User.objects.filter(user_permissions__codename__endswith=MANAGER_NAME).exclude(
            user_permissions__codename__endswith=ADMIN_NAME)
        serializer = UserListSerializer(managers, many=True)
        return Response({"message": "Manager List", "responseCode": "100", "data": serializer.data},
                        status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_manager(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_perms = get_user_permissions(user)
    if MANAGER_NAME in user_perms and ADMIN_NAME not in user_perms:
        user.delete()
    else:
        return Response({"message": "Only a Manager can be deleted", "responseCode": "101"}, status=status.HTTP_200_OK)
    return Response({"message": "Manager Deleted Successfully", "responseCode": "100"}, status=status.HTTP_202_ACCEPTED)
