from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.permission import ManagerPermission
from library.models import Book
from library.serializers import BookSerializer, BookListSerializer


class AddBook(CreateAPIView):
    model = Book
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, ManagerPermission]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            book = serializer.save()
            serializer = BookListSerializer(instance=book)
            return Response({"message": "Book Successfully added to the library", "responseCode": "100", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"message": "Error Adding Book", "responseCode": "101",
                         "errors": serializer.errors}, status=status.HTTP_200_OK)
