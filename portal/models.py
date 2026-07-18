from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    CATEGORY_CHOICES = [
        ('University Core', 'University Core'),
        ('College Core', 'College Core'),
        ('Math/Science', 'Math/Science'),
        ('CPE Core', 'CPE Core'),
        ('Technical Elective', 'Technical Elective'),
        ('General Elective', 'General Elective'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    credits = models.PositiveIntegerField()
    image = models.ImageField(upload_to='subjects/', blank=True, null=True)
    
    # Curriculum mapping fields
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='CPE Core')
    plan_year = models.PositiveIntegerField(default=1) # 1 to 5
    plan_semester = models.PositiveIntegerField(default=1) # 1 or 2
    prerequisites = models.CharField(max_length=200, blank=True, null=True, default='None')

    def __str__(self):
        return f"{self.code} - {self.name}"

class Section(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='sections')
    section_number = models.CharField(max_length=10)
    days_and_time = models.CharField(max_length=100) # e.g. "Mon/Wed 09:00 - 10:30"
    days_pattern = models.CharField(max_length=10, default='MW') # 'MW', 'TR', 'F', 'S'
    time_start = models.TimeField(null=True, blank=True)
    time_end = models.TimeField(null=True, blank=True)
    instructor = models.CharField(max_length=100, default='TBD')
    room = models.CharField(max_length=50, default='TBD')
    seats_total = models.PositiveIntegerField(default=35)
    seats_available = models.PositiveIntegerField(default=35)
    final_exam_date = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.subject.code} - Sec {self.section_number} ({self.days_and_time})"

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='enrollments')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='enrollments', null=True, blank=True)
    date_enrolled = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.subject.code} ({self.status})"

class StudentCourseGrade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.CharField(max_length=5) # e.g. 'A', 'A-', 'B+', 'C'
    points = models.FloatField() # e.g. 4.0, 3.7, 3.3, 2.0
    term = models.CharField(max_length=50) # e.g. 'Spring 2025'

    def __str__(self):
        return f"{self.student.username} - {self.subject.code}: {self.grade} ({self.term})"

class Notification(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=50, default='general') # e.g., 'seats', 'deadlines', 'rooms'
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.student.username} - {self.title} (Read: {self.is_read})"
