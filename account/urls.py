from django.urls import path

from account.views import AddUser, delete_manager, ManagerApiListView

urlpatterns = [
    path('register/user', AddUser.as_view(), name='register'),
    path('manager/list', ManagerApiListView.as_view(), name='managers'),
    path('user/<int:pk>/delete/', delete_manager, name='delete_user'),
    ]