from django.contrib import admin

from library.models import Student, Book, BookInstance, BookRequest


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'matric_num', 'first_name', 'last_name', 'status']
    search_fields = ['first_name', 'last_name', 'matric_num']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'isbn', 'summary', 'language', 'genre', 'copies']
    search_fields = ['title', 'author', 'genre']


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'due_date', 'book']
    search_fields = ['status', 'book__title', 'book__genre']


@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'book', 'requested_by', 'status', 'approved_by', 'rejected_by', 'given_book']
    search_fields = ['status', 'book__title', 'book__genre']
