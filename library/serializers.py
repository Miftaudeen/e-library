from datetime import datetime

from rest_framework import serializers

from account.serializers import UserListSerializer
from library.models import Book, Student, BookRequest


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ['title', 'author', 'summary', 'isbn', 'category', 'language']

    def save(self, **kwargs):
        book, _ = Book.objects.update_or_create(
                                   isbn=self.validated_data.get('isbn'),
                                   defaults={
                                       'title': self.validated_data.get('title'),
                                       'author': self.validated_data.get('author'),
                                       'summary': self.validated_data.get('summary'),
                                       'category': self.validated_data.get('category'),
                                       'language': self.validated_data.get('language'),
                                   })
        return book


class BookRequestSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(queryset=Book.objects.all(), slug_field='isbn')

    class Meta:
        model = BookRequest
        fields = ['book']

    def validate_book(self, value):
        if value.available_books.count() >= 1:
            return value
        raise serializers.ValidationError("Requested book is not available")

    def save(self, student):
        book_request, _ = BookRequest.objects.update_or_create(
            book=self.validated_data.get('book'),
            requested_by=student,
            status=BookRequest.PENDING)
        return book_request


class BookRequestReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=BookRequest.REQUEST_STATUS)
    book_request = serializers.PrimaryKeyRelatedField(queryset=BookRequest.objects.filter(
        status__in=[BookRequest.PENDING, BookRequest.APPROVED]),
                                                     many=False)


class BookReturnSerializer(serializers.Serializer):
    book_request = serializers.PrimaryKeyRelatedField(queryset=BookRequest.objects.filter(
        status=BookRequest.APPROVED), many=False)


class StudentReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Student.STUDENT_STATE)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.exclude(
        status__in=[Student.EXPELLED, Student.GRADUATED]), many=False)


class BookReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=((Book.AVAILABLE, Book.AVAILABLE), (Book.UNAVAILABLE, Book.UNAVAILABLE),))
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), many=False)


class BookListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'category', 'status', 'due_date', 'summary', 'language']


class BookRequestListSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookRequest
        fields = ['id', 'book', 'requested_by', 'status', 'approved_by', 'rejected_by']


class StudentListSerializer(serializers.ModelSerializer):
    user = UserListSerializer()

    class Meta:
        model = Student
        fields = ['id', 'matric_num', 'first_name', 'last_name', 'status', 'user']
