from django.urls import path

from account.views import AddUser
from library.views import AddBook, StudentApiListView, RequestBookView, ReviewBookRequestView, ReviewStudentStatusView, \
    ReviewBookStatusView, BookApiListView, BookSearchListView

urlpatterns = [
    path('add/book', AddBook.as_view(), name='add_book'),
    path('request/book', RequestBookView.as_view(), name='request_book'),
    path('review/book', ReviewBookStatusView.as_view(), name='request_book'),
    path('review/book/request', ReviewBookRequestView.as_view(), name='review_request'),
    path('review/student', ReviewStudentStatusView.as_view(), name='review_student'),
    path('student/list', StudentApiListView.as_view(), name='students'),
    path('book/list', BookApiListView.as_view(), name='books'),
    path('book/search/list', BookSearchListView.as_view(), name='book_list'),
    ]