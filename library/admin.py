from django.contrib import admin

from library.models import Student, Book, BookRequest


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'matric_num', 'first_name', 'last_name', 'status']
    search_fields = ['first_name', 'last_name', 'matric_num']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'isbn', 'summary', 'language', 'category', 'status', 'due_date', ]
    search_fields = ['title', 'author', 'category']


@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'book', 'requested_by', 'status', 'approved_by', 'rejected_by']
    search_fields = ['status', 'book__title', 'book__category']
