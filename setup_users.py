import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Create Admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
    print("Superuser 'admin' created.")
else:
    print("Superuser 'admin' already exists.")

# Create Student
if not User.objects.filter(username='student').exists():
    user = User.objects.create_user('student', 'student@example.com', 'studentpass')
    print("User 'student' created.")
else:
    print("User 'student' already exists.")
