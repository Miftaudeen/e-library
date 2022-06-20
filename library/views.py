from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.permission import ManagerPermission, AdminPermission
from library.models import Book, Student, BookRequest, BookInstance
from library.serializers import BookSerializer, BookListSerializer, StudentListSerializer, BookRequestSerializer, \
    BookRequestListSerializer, BookRequestReviewSerializer, StudentReviewSerializer, BookReviewSerializer


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


class RequestBookView(CreateAPIView):
    model = BookRequest
    serializer_class = BookRequestSerializer
    permission_classes = [IsAuthenticated, ManagerPermission]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            book = serializer.save()
            serializer = BookRequestListSerializer(instance=book)
            return Response({"message": "Book Requested Successfully", "responseCode": "100", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"message": "Error Requesting Book", "responseCode": "101",
                         "errors": serializer.errors}, status=status.HTTP_200_OK)


class ReviewBookRequestView(UpdateAPIView):
    model = BookRequest
    serializer_class = BookRequestReviewSerializer
    permission_classes = [IsAuthenticated, ManagerPermission]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user = request.user
        if serializer.is_valid():
            book_request = serializer.validated_data.get('book_request')
            request_status = serializer.validated_data.get('status')
            if request_status == BookRequest.APPROVED:
                if book_request.status != BookRequest.PENDING:
                    return Response({"message": f"You cannot approve {book_request.status} book request", "responseCode": "103",
                                     "errors": "You can only approve a pending book request"},
                                    status=status.HTTP_200_OK)
                book = book_request.book
                if book.available_books.exists():
                    available_book = book.available_books.first()
                    available_book.status = BookInstance.ON_LOAN
                    available_book.due_date = serializer.validated_data.get('due_date')
                    available_book.save()
                    book_request.given_book = available_book
                    book_request.approved_by = user
                    book_request.status = request_status
                else:
                    return Response({"message": f"Book is no longer Available", "responseCode": "103",
                                     "errors": f"{book_request.book} is no longer available"},
                                    status=status.HTTP_200_OK)

            elif request_status == BookRequest.REJECTED:
                if book_request.status != BookRequest.PENDING:
                    return Response({"message": f"You cannot reject {book_request.status} book request", "responseCode": "103",
                                     "errors": "You can only reject pending book request"},
                                    status=status.HTTP_200_OK)
                book_request.rejected_by = user
                book_request.status = request_status
            elif request_status == BookRequest.RETURNED:
                if book_request.status != BookRequest.APPROVED:
                    return Response({"message": f"You cannot return {book_request.status} book request", "responseCode": "103",
                                     "errors": "You can only return an approved book request"},
                                    status=status.HTTP_200_OK)
                given_book = book_request.given_book
                given_book.status = BookInstance.AVAILABLE
                given_book.save()
                book_request.status = request_status
            else:
                return Response({"message": "Invalid Status Selected", "responseCode": "103",
                                 "errors": "You can only approve, reject or return a book"}, status=status.HTTP_200_OK)
            book_request.save()
            serializer = BookRequestListSerializer(instance=book_request)
            return Response({"message": f"Book {request_status} Successfully", "responseCode": "100", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"message": "Error Reviewing Book Request", "responseCode": "101",
                         "errors": serializer.errors}, status=status.HTTP_200_OK)


class ReviewStudentStatusView(UpdateAPIView):
    model = Student
    serializer_class = StudentReviewSerializer
    permission_classes = [IsAuthenticated, ManagerPermission]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            student = serializer.validated_data.get('student')
            student_status = serializer.validated_data.get('status')
            if student_status == Student.ACTIVE:
                if student.status != Student.SUSPENDED:
                    return Response({"message": f"You cannot unsuspend {student.status} student", "responseCode": "103",
                                     "errors": "You can only unsuspend a suspended student"},
                                    status=status.HTTP_200_OK)
            elif student_status == Student.SUSPENDED:
                if student.status != Student.ACTIVE:
                    return Response({"message": f"You cannot suspend {student.status} student", "responseCode": "103",
                                     "errors": "You can only suspend an active student"},
                                    status=status.HTTP_200_OK)
            elif student_status == [Student.GRADUATED, Student.EXPELLED]:
                if student.status != Student.ACTIVE:
                    return Response({"message": f"You cannot graduate or expel {student.status} student", "responseCode": "103",
                                     "errors": "You can only graduate or expel an active student"},
                                    status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid Status Selected", "responseCode": "103",
                                 "errors": "You can only suspend, unsuspended, graduate or expel student"}, status=status.HTTP_200_OK)
            student.status = student_status
            student.save()
            serializer = StudentListSerializer(instance=student)
            return Response({"message": f"Student {student_status.replace(Student.ACTIVE, 'Unsuspend')} Successfully", "responseCode": "100", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"message": "Error Requesting Book", "responseCode": "101",
                         "errors": serializer.errors}, status=status.HTTP_200_OK)



class ReviewBookStatusView(UpdateAPIView):
    model = Book
    serializer_class = BookReviewSerializer
    permission_classes = [IsAuthenticated, ManagerPermission]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user = request.user
        if serializer.is_valid():
            book = serializer.validated_data.get('book')
            book_status = serializer.validated_data.get('status')
            if book_status == BookInstance.AVAILABLE:
                if book.unavailable_books.count() <= 0:
                    return Response({"message": f"You don't have any unavailable book", "responseCode": "103",
                                     "errors": "You can only make available unavailable books"},
                                    status=status.HTTP_200_OK)
                for book_copy in book.unavailable_books:
                    book_copy.status = BookInstance.AVAILABLE
                    book_copy.save()
            elif book_status == BookInstance.UNAVAILABLE:
                if book.available_books.count() <= 0:
                    return Response({"message": f"You don't have any available book", "responseCode": "103",
                                     "errors": "You can only make unavailable available books"},
                                    status=status.HTTP_200_OK)
                for book_copy in book.available_books:
                    book_copy.status = BookInstance.UNAVAILABLE
                    book_copy.save()
            else:
                return Response({"message": "Invalid Status Selected", "responseCode": "103",
                                 "errors": "You can only make a book available or unavailable"}, status=status.HTTP_200_OK)
            serializer = BookListSerializer(instance=book)
            return Response({"message": f"Book Made {book_status} ", "responseCode": "100", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"message": "Error Changing Book Status", "responseCode": "101",
                         "errors": serializer.errors}, status=status.HTTP_200_OK)


class StudentApiListView(ListAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def list(self, request, *args, **kwargs):
        students = Student.objects.all()
        serializer = StudentListSerializer(students, many=True)
        return Response({"message": "Student List", "responseCode": "100", "data": serializer.data},
                        status=status.HTTP_200_OK)
