from datetime import datetime

from rest_framework import serializers

from account.models import User
from account.permission import get_as_perm
from account.perms_constants import PERM_CHOICES
from library.models import Book, BookInstance, Student, BookRequest


class BookSerializer(serializers.ModelSerializer):
    copies = serializers.IntegerField(min_value=1)

    class Meta:
        model = Book
        fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'copies']

    def save(self, **kwargs):
        book, _ = Book.objects.update_or_create(
                                   isbn=self.validated_data.get('isbn'),
                                   defaults={
                                       'title': self.validated_data.get('title'),
                                       'author': self.validated_data.get('author'),
                                       'summary': self.validated_data.get('summary'),
                                       'genre': self.validated_data.get('genre'),
                                       'language': self.validated_data.get('language'),
                                   })
        for i in range(self.validated_data.get('copies')):
            if i > 0:
                BookInstance.objects.create(book=book, status=BookInstance.AVAILABLE)
                continue
            BookInstance.objects.create(book=book)
        return book


class BookRequestSerializer(serializers.ModelSerializer):
    requested_by = serializers.SlugRelatedField(queryset=Student.objects.filter(status=Student.ACTIVE),
                                                slug_field='matric_num')
    book = serializers.SlugRelatedField(queryset=Book.objects.all(), slug_field='isbn')

    class Meta:
        model = BookRequest
        fields = ['requested_by', 'book']

    def validate_book(self, value):
        if value.available_books.count() >= 1:
            return value
        raise serializers.ValidationError("Requested book is not available")

    def save(self, **kwargs):
        book_request, _ = BookRequest.objects.update_or_create(
            book=self.validated_data.get('book'),
            requested_by=self.validated_data.get('requested_by'),
            status=BookRequest.PENDING)
        return book_request


class BookRequestReviewSerializer(serializers.Serializer):
    due_date = serializers.DateField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=BookRequest.REQUEST_STATUS)
    book_request = serializers.PrimaryKeyRelatedField(queryset=BookRequest.objects.filter(
        status__in=[BookRequest.PENDING, BookRequest.APPROVED]),
                                                     many=False)

    def validate(self, data):
        if data.get('status') == BookRequest.APPROVED and not data.get('due_date'):
            raise serializers.ValidationError({"due_date": "This Field is required for approving book request"})
        if data.get('due_date') and data.get('due_date') <= datetime.now().date():
            raise serializers.ValidationError({"due_date": "Only future date can be chosen for due date"})
        return data


class StudentReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Student.STUDENT_STATE)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.exclude(
        status__in=[Student.EXPELLED, Student.GRADUATED]), many=False)


class BookReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=((BookInstance.AVAILABLE, BookInstance.AVAILABLE), (BookInstance.UNAVAILABLE, BookInstance.UNAVAILABLE),))
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), many=False)


class BookInstanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookInstance
        fields = ['id', 'status', 'due_date', 'book']


class BookListSerializer(serializers.ModelSerializer):
    copies = BookInstanceSerializer(many=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'summary', 'language', 'genre', 'copies']


class BookRequestListSerializer(serializers.ModelSerializer):
    given_book = BookInstanceSerializer()

    class Meta:
        model = BookRequest
        fields = ['id', 'book', 'requested_by', 'status', 'approved_by', 'rejected_by', 'given_book']


class StudentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ['id', 'matric_num', 'first_name', 'last_name', 'status']
