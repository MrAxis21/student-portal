from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Subject, Enrollment, Section, StudentCourseGrade, Notification

class PortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user('student', 's@e.com', 'pass')
        self.admin = User.objects.create_superuser('admin', 'a@e.com', 'pass')
        
        # Create test subjects
        self.math101 = Subject.objects.create(
            name='Calculus I', 
            code='MATH101', 
            description='Algebra', 
            credits=4,
            category='Math/Science',
            plan_year=1,
            plan_semester=1
        )
        self.cpe101 = Subject.objects.create(
            name='Intro to Computing', 
            code='CPE101', 
            description='Intro', 
            credits=3,
            category='CPE Core',
            plan_year=1,
            plan_semester=1
        )
        
        # Create sections
        self.math_section = Section.objects.create(
            subject=self.math101,
            section_number='01',
            days_and_time='Mon/Wed 09:00 - 10:30',
            days_pattern='MW',
            seats_total=30,
            seats_available=10
        )
        self.cpe_section = Section.objects.create(
            subject=self.cpe101,
            section_number='01',
            days_and_time='Mon/Wed 09:00 - 10:30', # Overlapping time pattern for testing conflict
            days_pattern='MW',
            seats_total=30,
            seats_available=10
        )

    def test_subject_enrollment_flow_approved(self):
        self.client.force_login(self.student)
        
        # 1. View subject list
        response = self.client.get('/subjects/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Calculus I')
        
        # 2. Enroll (seat is available)
        response = self.client.post(f'/subjects/enroll/{self.math101.id}/')
        self.assertRedirects(response, '/subjects/')
        
        # 3. Verify DB - Should be approved automatically
        enrollment = Enrollment.objects.get(student=self.student, subject=self.math101)
        self.assertEqual(enrollment.status, 'approved')
        
        # 4. Verify seat count decremented
        self.math_section.refresh_from_db()
        self.assertEqual(self.math_section.seats_available, 9)

    def test_subject_enrollment_flow_pending_no_seats(self):
        # Set seats to 0
        self.math_section.seats_available = 0
        self.math_section.save()
        
        self.client.force_login(self.student)
        
        # Enroll
        response = self.client.post(f'/subjects/enroll/{self.math101.id}/')
        self.assertRedirects(response, '/subjects/')
        
        # Verify DB - Should be pending
        enrollment = Enrollment.objects.get(student=self.student, subject=self.math101)
        self.assertEqual(enrollment.status, 'pending')

    def test_admin_approval_flow(self):
        # Create pending enrollment
        enrollment = Enrollment.objects.create(student=self.student, subject=self.math101, status='pending')
        self.client.force_login(self.admin)
        
        # Approve
        response = self.client.get(f'/subjects/enroll/approve/{enrollment.id}/')
        self.assertRedirects(response, '/admin-dashboard/')
        
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, 'approved')

    def test_add_subject_view(self):
        self.client.force_login(self.admin)
        response = self.client.get('/subjects/add/')
        self.assertEqual(response.status_code, 200)
        
        # Add new subject
        data = {
            'name': 'New Subject',
            'code': 'NEW101',
            'description': 'Description',
            'credits': 3
        }
        response = self.client.post('/subjects/add/', data)
        self.assertRedirects(response, '/admin-dashboard/')
        self.assertTrue(Subject.objects.filter(code='NEW101').exists())

    def test_student_cannot_add_subject(self):
        self.client.force_login(self.student)
        response = self.client.get('/subjects/add/')
        self.assertNotEqual(response.status_code, 200)

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Back')

    def test_registration_flow(self):
        # 1. GET register page
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        
        # 2. POST registration
        data = {
            'username': 'newuser',
            'password1': 'SafePassword123',
            'password2': 'SafePassword123',
        }
        response = self.client.post('/register/', data)
        self.assertRedirects(response, '/login/')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    # --- New Tests for Student Portal Upgrades ---

    def test_student_dashboard_metrics(self):
        # Seed user grades
        StudentCourseGrade.objects.create(
            student=self.student,
            subject=self.math101,
            grade='A',
            points=4.0,
            term='Fall 2025'
        )
        self.client.force_login(self.student)
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '4.0') # Cumulative GPA
        self.assertContains(response, 'student') # Student username displayed (No Sara Al-Rashid)

    def test_academic_progress_audit(self):
        # Create grade
        StudentCourseGrade.objects.create(
            student=self.student,
            subject=self.math101,
            grade='A',
            points=4.0,
            term='Fall 2025'
        )
        self.client.force_login(self.student)
        response = self.client.get('/progress/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Completed')

    def test_grades_and_what_if_calc(self):
        self.client.force_login(self.student)
        response = self.client.get('/grades/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'What-If GPA Calculator')

    def test_notification_page_loads_and_clears_read(self):
        self.client.force_login(self.student)
        # Create a notification
        Notification.objects.create(
            student=self.student,
            title='Seat Available',
            message='Test message',
            category='seats',
            is_read=False
        )
        # Verify notification page loads
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)
        
        # Verify post action mark_all_read works
        data = {'action': 'mark_all_read'}
        response = self.client.post('/notifications/', data)
        self.assertRedirects(response, '/notifications/')
        self.assertEqual(Notification.objects.filter(student=self.student, is_read=False).count(), 0)

    def test_session_registration_draft_flow(self):
        self.client.force_login(self.student)
        
        # 1. Add course section to draft plan
        data = {'action': 'add_draft', 'section_id': self.math_section.id}
        response = self.client.post('/registration/', data)
        self.assertRedirects(response, '/registration/')
        
        # Verify section added to session draft
        session = self.client.session
        self.assertIn(self.math_section.id, session['registration_draft'])

        # 2. Add conflicting section (same slot) - should fail conflict checks
        data = {'action': 'add_draft', 'section_id': self.cpe_section.id}
        response = self.client.post('/registration/', data)
        self.assertRedirects(response, '/registration/')
        # Conflicting item should not be in the draft list
        session = self.client.session
        self.assertNotIn(self.cpe_section.id, session['registration_draft'])

        # 3. Submit registration plan
        data = {'action': 'submit_registration'}
        response = self.client.post('/registration/', data)
        self.assertRedirects(response, '/registration/success/')

        # Verify draft was cleared and Enrollment created with approved status
        session = self.client.session
        self.assertEqual(len(session['registration_draft']), 0)
        enrollment = Enrollment.objects.get(student=self.student, subject=self.math101)
        self.assertEqual(enrollment.status, 'approved')
        
        # Verify seat count decremented
        self.math_section.refresh_from_db()
        self.assertEqual(self.math_section.seats_available, 9)
