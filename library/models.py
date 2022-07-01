from django.db import models
from django.utils.functional import cached_property

from base.models import BaseModel


class Book(BaseModel):
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
    AVAILABILITY = (
        (UNAVAILABLE, 'Unavailable'),
        (AVAILABLE, 'Available'),
    )
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True, null=True)
    summary = models.TextField(null=True, blank=True)
    isbn = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    language = models.CharField(max_length=200, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    year_published = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=BOOK_STATE, blank=True,
                              default=AVAILABLE, help_text='Book availability',
                              )

    def __str__(self):
        return self.title


class Student(BaseModel):
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

    matric_num = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=50, choices=STUDENT_STATE, default=ACTIVE)
    user = models.OneToOneField('account.User', on_delete=models.CASCADE)

    @cached_property
    def first_name(self):
        return self.user.first_name

    @cached_property
    def last_name(self):
        return self.user.last_name

    @cached_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class BookRequest(BaseModel):
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
    requested_by = models.ForeignKey('library.Student', on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=200, choices=REQUEST_STATUS)
    approved_by = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_requests')
    rejected_by = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='rejected_requests')
    book = models.ForeignKey('library.Book', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.requested_by.full_name} - {self.book.title}"

    @property
    def due_date(self):
        return self.book.due_date
