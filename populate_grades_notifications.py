import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from portal.models import Subject, StudentCourseGrade, Notification

def populate_data():
    try:
        student = User.objects.get(username='student')
    except User.DoesNotExist:
        print("Error: Student user 'student' not found. Run setup_users.py first.")
        return

    # Clear existing grades and notifications
    StudentCourseGrade.objects.filter(student=student).delete()
    Notification.objects.filter(student=student).delete()

    print(f"Populating grades and notifications for user: {student.username}")

    # Helper function to get subject or return None
    def get_subj(code):
        try:
            return Subject.objects.get(code=code)
        except Subject.DoesNotExist:
            return None

    # Past Grades data
    grades_data = [
        {'code': 'MATH101', 'grade': 'B+', 'points': 3.3, 'term': 'Fall 2024'},
        {'code': 'CPE101', 'grade': 'B-', 'points': 2.7, 'term': 'Fall 2024'},
        {'code': 'HUM101', 'grade': 'B', 'points': 3.0, 'term': 'Fall 2024'},
        {'code': 'MATH102', 'grade': 'B+', 'points': 3.3, 'term': 'Spring 2025'},
        {'code': 'CPE102', 'grade': 'B+', 'points': 3.3, 'term': 'Spring 2025'},
        {'code': 'CPE201', 'grade': 'A', 'points': 4.0, 'term': 'Fall 2025'},
        {'code': 'SOC101', 'grade': 'B+', 'points': 3.3, 'term': 'Fall 2025'},
    ]

    for g in grades_data:
        subject = get_subj(g['code'])
        if subject:
            grade_obj = StudentCourseGrade.objects.create(
                student=student,
                subject=subject,
                grade=g['grade'],
                points=g['points'],
                term=g['term']
            )
            print(f"Created Grade: {grade_obj}")

    # Notifications data
    notifications = [
        {
            'title': 'Seat Available in Watched Course',
            'message': 'A seat has just opened up in Web Development (WEB101) Section 01. Click below to register.',
            'category': 'seats',
            'link': '/registration/'
        },
        {
            'title': 'Registration Window Countdown',
            'message': 'Your enrollment window is scheduled for Fall 2026/2027. Ensure all holds are cleared before your slot opens.',
            'category': 'deadlines',
            'link': '/dashboard/'
        },
        {
            'title': 'New Section Opened',
            'message': 'A new section (Section 02) has been added for Data Structures & Algorithms (CPE202) taught by Dr. Donald Knuth.',
            'category': 'rooms',
            'link': '/registration/'
        }
    ]

    for n in notifications:
        notif = Notification.objects.create(
            student=student,
            title=n['title'],
            message=n['message'],
            category=n['category'],
            is_read=False,
            link=n['link']
        )
        print(f"Created Notification: {notif.title}")

    print("Population of grades and notifications complete.")

if __name__ == '__main__':
    populate_data()
