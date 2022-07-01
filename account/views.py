from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, get_object_or_404, ListAPIView
# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token, RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from account.models import User
from account.permission import get_as_perm, get_permission, AdminPermission, get_user_permissions
from account.perms_constants import ADMIN_NAME, USER_PERMS_NAMES, MANAGER_NAME, STUDENT_NAME
from account.serializers import UserSerializer, UserListSerializer, UserPasswordResetSerializer, StudentUserSerializer
from library.models import Student
from library.serializers import StudentListSerializer
from utils.utility import generate_username, generate_digits, generate_matric_num


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

            temp_password = f'{user.first_name}{generate_digits(5)}'
            user.set_password(temp_password)
            user.temp_password = temp_password
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


class ChangePasswordAPIView(CreateAPIView):

    """
    Change  Password of a user
    Method `GET`<br>
    Format `Json` <br>
    Authorization: Token based auth is required

    Response:
        <pre>


        </pre>
    """
    serializer_class = UserPasswordResetSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)

        if serializer.is_valid():
            username = serializer.validated_data.get('username').lower()
            temp_password = serializer.validated_data.get('old_password')
            password = serializer.validated_data.get('new_password')

            try:
                validate_password(password)
            except ValidationError as validate_error:
                return Response(
                    {"message": "Change Password Error", "responseCode": "108", "errors": str(validate_error),
                     "data": serializer.data},
                    status=status.HTTP_201_CREATED)

            user = authenticate(request=request, username=username, password=temp_password)
            if user is not None:
                user.set_password(password)
                user.temp_password = ''
                user.initial_password_changed = True
                user.save()
                return Response({"message": "Change Password", "responseCode": "100", "data": serializer.data},
                                status=status.HTTP_201_CREATED)

        return Response({"message": "Change Password Error", "responseCode": "108", "errors": serializer.errors,
                         "data": serializer.data},
                        status=status.HTTP_201_CREATED)


def custom_jwt_response_payload_handler(refresh, user=None, request=None):
    user_perms = get_user_permissions(user)

    return {"username": user.username, "user_id": user.id, 'permissions': user_perms,
            "refresh": refresh.get('refresh'),
            "access": refresh.get('access'),
            'initial_password_changed': user.initial_password_changed,
            'responseCode': '100', 'message': 'Authentication successfully'}


class CustomAuthToken(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        data = request.data

        # changes the username to lower because username is case insensitive, and are stored in lower case
        serializer = self.get_serializer(data={'username': data.get('username'),
                                               'password': data.get('password')})

        if serializer.validate(attrs={'username': data.get('username'),
                                               'password': data.get('password')}):

            user = User.objects.filter(username=data.get('username')).first()
            refresh = serializer.get_token(user)
            res = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            response_data = custom_jwt_response_payload_handler(res, user)

            if STUDENT_NAME in get_user_permissions(user):
                student = user.student
                if student and student.status == Student.SUSPENDED:
                    return Response({"message": "Authentication Error", "responseCode": "103",
                                     "errors": "You have been suspended"}, status=status.HTTP_200_OK)

            return Response(response_data, status=status.HTTP_200_OK)
        return Response({"message": "Authentication Error", "responseCode": "101",
                         "errors": serializer.errors}, status=status.HTTP_200_OK)


class StudentSignUpApiView(CreateAPIView):
    model = User
    serializer_class = StudentUserSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.user_permissions.add(get_permission(STUDENT_NAME))
            temp_password = f'{user.first_name}{generate_digits(5)}'
            user.set_password(temp_password)
            user.temp_password = temp_password
            user.save()
            student = Student.objects.create(matric_num=generate_matric_num(), user=user)
            serializer = StudentListSerializer(instance=student)
            return Response({"message": "Sign Up Successful", "responseCode": "100", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"message": "Sign Up Error", "responseCode": "101",
                         "errors": serializer.errors}, status=status.HTTP_200_OK)
