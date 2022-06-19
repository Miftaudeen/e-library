from rest_framework import serializers

from account.models import User
from account.permission import get_as_perm
from account.perms_constants import PERM_CHOICES
from library.models import Book, BookInstance


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


class BookListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'summary', 'language', 'genre', 'copies']
