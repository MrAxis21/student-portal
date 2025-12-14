from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import ServiceRequest, Subject, Enrollment

class PortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user('student', 's@e.com', 'pass')
        self.admin = User.objects.create_superuser('admin', 'a@e.com', 'pass')
        self.subject = Subject.objects.create(name='Mathematics', code='MATH101', description='Algebra', credits=3)

    def test_subject_enrollment_flow(self):
        self.client.force_login(self.student)
        
        # 1. View subject list
        response = self.client.get('/subjects/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mathematics')
        
        # 2. Enroll
        response = self.client.post(f'/subjects/enroll/{self.subject.id}/')
        self.assertRedirects(response, '/subjects/')
        
        # 3. Verify DB - Should be pending
        enrollment = Enrollment.objects.get(student=self.student, subject=self.subject)
        self.assertEqual(enrollment.status, 'pending')
        
        # 4. Pending badge visible
        response = self.client.get('/subjects/')
        self.assertContains(response, 'Request Pending')

    def test_admin_approval_flow(self):
        # Create pending enrollment
        enrollment = Enrollment.objects.create(student=self.student, subject=self.subject, status='pending')
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
        # Should redirect to login (staff_member_required usually redirects to login if not staff)
        self.assertNotEqual(response.status_code, 200)

    def test_student_request_flow(self):
        print("\n--- Starting Test ---")
        # Login as student
        logged_in = self.client.login(username='student', password='pass')
        print(f"Student login: {logged_in}")
        
        # Submit request
        response = self.client.post('/dashboard/', {
            'request_type': 'transcript',
            'details': 'Need it ASAP'
        })
        print(f"Post response: {response.status_code}, Location: {response.get('Location', 'None')}")
        self.assertRedirects(response, '/dashboard/')
        
        count = ServiceRequest.objects.count()
        print(f"Request count: {count}")
        self.assertEqual(count, 1)
        
        req = ServiceRequest.objects.first()
        print(f"Request status: {req.status}")
        self.assertEqual(req.student, self.student)
        self.assertEqual(req.status, 'pending')

        # Admin login
        self.client.logout()
        logged_in_admin = self.client.login(username='admin', password='pass')
        print(f"Admin login: {logged_in_admin}")

        # View dashboard
        response = self.client.get('/admin-dashboard/')
        print(f"Admin dashboard status: {response.status_code}")
        self.assertEqual(response.status_code, 200)

        # Approve
        approve_url = f'/request/{req.id}/status/approved/'
        print(f"Approving at: {approve_url}")
        response = self.client.get(approve_url)
        print(f"Approve response: {response.status_code}, Location: {response.get('Location', 'None')}")
        self.assertRedirects(response, '/admin-dashboard/')
        
        req.refresh_from_db()
        print(f"New Status: {req.status}")
        self.assertEqual(req.status, 'approved')

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome to Student Services')

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
        # In Django's test client, creating a user might require different handling if we want to bypass full form validation quirks 
        # or we just rely on the view using UserCreationForm which does the job.
        # UserCreationForm saves the user.
        
        response = self.client.post('/register/', data)
        if response.status_code != 302:
            print(f"Registration failed: {response.context['form'].errors}")
            
        self.assertRedirects(response, '/login/')
        
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_api_access(self):
        # Obtain JWT token
        response = self.client.post('/auth/jwt/create/', {'username': 'student', 'password': 'pass'})
        self.assertEqual(response.status_code, 200, f"Token fetch failed: {response.content}")
        token = response.json()['access']
        auth_headers = {'HTTP_AUTHORIZATION': f'JWT {token}'}
        
        # Create request via API
        response = self.client.post('/api/v1/requests/', {'request_type': 'letter', 'details': 'API Request'}, **auth_headers)
        self.assertEqual(response.status_code, 201, f"API Create failed: {response.content}")
        self.assertEqual(ServiceRequest.objects.filter(details='API Request').count(), 1)
        
        # List requests
        response = self.client.get('/api/v1/requests/', **auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) >= 1)
