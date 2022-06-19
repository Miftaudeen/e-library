import uuid

from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True, null=True)
    summary = models.TextField(null=True, blank=True)
    isbn = models.CharField(max_length=200)
    genre = models.CharField(max_length=200, null=True, blank=True)
    language = models.CharField(max_length=200, null=True, blank=True)

    @property
    def copies(self):
        return BookInstance.objects.filter(book=self).count()

    @property
    def available_books(self):
        return BookInstance.objects.filter(book=self, )


class BookInstance(models.Model):
    UNAVAILABLE = 'Unavailable'
    ON_LOAN = 'On loan'
    AVAILABLE = 'Available'
    RESERVED = 'Reserved'
    BOOK_STATE = (
        (UNAVAILABLE, 'Unavailable'),
        (ON_LOAN, 'On loan'),
        (AVAILABLE, 'Available'),
        (RESERVED, 'Reserved'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Unique ID for this particular book across whole library')
    due_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey('library.Book', on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=50,
        choices=BOOK_STATE,
        blank=True,
        default=RESERVED,
        help_text='Book availability',
    )


class Student(models.Model):
    ACTIVE = 'Active'
    GRADUATED = 'Graduated'
    SUSPENDED = 'Suspended'
    EXPELLED = 'Expelled'

    STUDENT_STATE = (
        (ACTIVE, ACTIVE),
        (GRADUATED, GRADUATED),
        (SUSPENDED, SUSPENDED),
        (EXPELLED, EXPELLED),
    )

    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    matric_num = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=50, choices=STUDENT_STATE, default=ACTIVE)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class BookRequest(models.Model):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'
    RETURNED = 'Returned'
    REQUEST_STATUS = (
        (PENDING, PENDING),
        (APPROVED, APPROVED),
        (RETURNED, RETURNED),
        (REJECTED, REJECTED),
    )
    requested_by = models.ForeignKey('library.Student', on_delete=models.CASCADE),
    status = models.CharField(max_length=200, choices=REQUEST_STATUS)
    approved_by = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_requests')
    rejected_by = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='rejected_requests')
    book = models.ForeignKey('library.Book', on_delete=models.CASCADE)
    given_book = models.ForeignKey('library.BookInstance', on_delete=models.SET_NULL, null=True, blank=True)
