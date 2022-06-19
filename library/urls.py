from django.urls import path

from account.views import AddUser
from library.views import AddBook

urlpatterns = [
    path('add/book', AddBook.as_view(), name='add_book'),
    ]