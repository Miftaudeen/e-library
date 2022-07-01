import os
from datetime import timedelta

from celery import shared_task
from celery.schedules import crontab
from celery.task import periodic_task
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core import management
from django.db.models import Q
from django.utils import timezone

from library.models import BookRequest, Book, Student


@periodic_task(run_every=(crontab(minute=0)), name="request_check_task")
def request_check_task(tenant_name, tenant_id):
    pending_requests = BookRequest.objects.filter(status=BookRequest.PENDING)
    for p_request in pending_requests:
        if (p_request.created + relativedelta(hours=24)) <= timezone.now():
            p_request.status = BookRequest.REJECTED
            p_request.save()
            book = p_request.book
            book.status = Book.AVAILABLE
            book.save()
    approved_requests = BookRequest.objects.filter(status=BookRequest.APPROVED)
    for approved_request in approved_requests:
        if approved_request.due_date <= timezone.now():
            student = approved_request.requested_by
            student.status = Student.SUSPENDED
            student.save()
