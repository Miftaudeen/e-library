from datetime import datetime
from os import getenv

from dateutil.relativedelta import relativedelta
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.permission import ManagerPermission, AdminPermission, StudentPermission
from library.models import Book, Student, BookRequest
from library.serializers import BookSerializer, BookListSerializer, StudentListSerializer, BookRequestSerializer, \
    BookRequestListSerializer, BookRequestReviewSerializer, StudentReviewSerializer, BookReviewSerializer, \
    BookReturnSerializer


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
    permission_classes = [IsAuthenticated, StudentPermission]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            student = request.user.student
            given_book = BookRequest.objects.filter(requested_by=student, status=BookRequest.APPROVED)
            if given_book.exists():
                return Response({"message": "Cannot Request Book", "responseCode": "103",
                                 "errors": f"You cannot request book because you have not returned {given_book.first().book.title }"},
                                status=status.HTTP_200_OK)

            pending_request = BookRequest.objects.filter(requested_by=student, status=BookRequest.PENDING)
            if pending_request.exists():
                return Response({"message": "Cannot Request Book", "responseCode": "103",
                                 "errors": f"You cannot request book because you have requested {pending_request.first().book.title }"},
                                status=status.HTTP_200_OK)

            book = serializer.save(student)
            book.status = Book.RESERVED
            book.save()
            serializer = BookRequestListSerializer(instance=book)
            return Response({"message": "Book Requested Successfully", "responseCode": "100", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"message": "Error Requesting Book", "responseCode": "101",
                         "errors": serializer.errors}, status=status.HTTP_200_OK)


class ReturnBookView(CreateAPIView):
    model = BookRequest
    serializer_class = BookReturnSerializer
    permission_classes = [IsAuthenticated, StudentPermission]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            book_request = serializer.validated_data.get('book_request')
            book_request.status = BookRequest.RETURNED
            book_request.save()
            book = book_request.book
            book.status = Book.AVAILABLE
            book.save()
            serializer = BookRequestListSerializer(instance=book)
            return Response({"message": "Book Returned Successfully", "responseCode": "100", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"message": "Error Returning Book", "responseCode": "101",
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
                if book.status == Book.RESERVED:
                    book.status = Book.ON_LOAN
                    book.due_date = (datetime.now() + relativedelta(hours=getenv('due', 72))).date()
                    book.save()
                    book_request.approved_by = user
                    book_request.status = request_status
                    pending_requests = BookRequest.objects.filter(book=book, status=BookRequest.PENDING)
                    for pending_request in pending_requests:
                        pending_request.status = BookRequest.REJECTED
                        pending_request.rejected_by = user
                        pending_request.save()
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
            else:
                return Response({"message": "Invalid Status Selected", "responseCode": "103",
                                 "errors": "You can only approve or reject a book request"}, status=status.HTTP_200_OK)
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
        if serializer.is_valid():
            book = serializer.validated_data.get('book')
            book_status = serializer.validated_data.get('status')
            if book_status == Book.AVAILABLE:
                if book.status != Book.UNAVAILABLE:
                    return Response({"message": f"You don't have any unavailable book", "responseCode": "103",
                                     "errors": "You can only make available, an  unavailable book"},
                                    status=status.HTTP_200_OK)
                book.status = Book.AVAILABLE
                book.save()
            elif book.status == Book.UNAVAILABLE:
                if book.status != Book.AVAILABLE:
                    return Response({"message": f"You don't have any available book", "responseCode": "103",
                                     "errors": "You can only make unavailable, an available book"},
                                    status=status.HTTP_200_OK)
                book.status = Book.UNAVAILABLE
                book.save()
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
    filter_backends = [OrderingFilter]

    def list(self, request, *args, **kwargs):
        students = Student.objects.all()
        status = request.GET.get('status')
        if status:
            students = students.filter(status=status)
        serializer = StudentListSerializer(students, many=True)
        return Response({"message": "Student List", "responseCode": "100", "data": serializer.data},
                        status=status.HTTP_200_OK)


class BookApiListView(ListAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    filter_backends = [OrderingFilter]

    def list(self, request, *args, **kwargs):
        books = Book.objects.all()
        status = request.GET.get('status')
        if status:
            books = books.filter(status__iexact=status)
        serializer =BookListSerializer(books, many=True)
        return Response({"message": "Book List", "responseCode": "100", "data": serializer.data},
                        status=status.HTTP_200_OK)


class BookSearchListView(ListAPIView):
    permission_classes = [IsAuthenticated, StudentPermission]
    filter_backends = [OrderingFilter]

    def list(self, request, *args, **kwargs):
        books = Book.objects.filter(status=Book.AVAILABLE)
        name = request.GET.get('name')
        if name:
            books = books.filter(title__icontains=name)
        author = request.GET.get('author')
        if author:
            books = books.filter(author__icontains=author)
        category = request.GET.get('category')
        if category:
            books = books.filter(category__icontains=category)
        year_published = request.GET.get('year_published')
        if year_published:
            books = books.filter(year_published=year_published)
        serializer =BookListSerializer(books, many=True)
        return Response({"message": "Book List", "responseCode": "100", "data": serializer.data},
                        status=status.HTTP_200_OK)
