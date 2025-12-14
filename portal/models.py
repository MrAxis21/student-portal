from django.db import models
from django.contrib.auth.models import User

class ServiceRequest(models.Model):
    REQUEST_TYPES = [
        ('transcript', 'Transcript'),
        ('letter', 'Recommendation Letter'),
        ('certificate', 'Enrollment Certificate'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPES)
    details = models.TextField(help_text="Provide additional details for your request.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_comment = models.TextField(blank=True, null=True, help_text="Reason for approval/rejection.")

    def __str__(self):
        return f"{self.student.username} - {self.get_request_type_display()} ({self.status})"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    credits = models.PositiveIntegerField()
    image = models.ImageField(upload_to='subjects/', blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='enrollments')
    date_enrolled = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.subject.code} ({self.status})"
