from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import ServiceRequest, Subject, Enrollment
from django.contrib import messages
from django.db.models import Sum
from .forms import ServiceRequestForm, SubjectForm

@login_required
def dashboard_redirect(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect('student_dashboard')

@login_required
def subject_list(request):
    subjects = Subject.objects.all()
    # Get dict of subject_id -> status
    enrollments = Enrollment.objects.filter(student=request.user)
    enrollment_status = {e.subject_id: e.status for e in enrollments}
    
    return render(request, 'portal/subject_list.html', {
        'subjects': subjects,
        'enrollment_status': enrollment_status
    })

@login_required
def enroll_subject(request, subject_id):
    if request.method == 'POST':
        subject = get_object_or_404(Subject, id=subject_id)
        # Check if already enrolled (any status)
        if Enrollment.objects.filter(student=request.user, subject=subject).exists():
             messages.warning(request, f'You have already requested/enrolled in {subject.name}')
        else:
            Enrollment.objects.create(student=request.user, subject=subject, status='pending')
            messages.success(request, f'Enrollment requested for {subject.name}. Waiting for approval.')
            
    return redirect('subject_list')

@staff_member_required
def admin_dashboard(request):
    status_filter = request.GET.get('status')
    if status_filter:
        requests = ServiceRequest.objects.filter(status=status_filter).order_by('-created_at')
    else:
        requests = ServiceRequest.objects.all().order_by('-created_at')
    
    # Fetch pending enrollments
    pending_enrollments = Enrollment.objects.filter(status='pending').select_related('student', 'subject')
    
    total_subjects_count = Subject.objects.count()
        
    return render(request, 'portal/admin_dashboard.html', {
        'requests': requests,
        'pending_enrollments': pending_enrollments,
        'total_subjects_count': total_subjects_count,
    })

@staff_member_required
def approve_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    enrollment.status = 'approved'
    enrollment.save()
    messages.success(request, f'Approved enrollment for {enrollment.student.username} in {enrollment.subject.code}')
    return redirect('admin_dashboard')

@staff_member_required
def reject_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    enrollment.status = 'rejected'
    enrollment.save()
    messages.success(request, f'Rejected enrollment for {enrollment.student.username} in {enrollment.subject.code}')
    return redirect('admin_dashboard')

@staff_member_required
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully!')
            return redirect('admin_dashboard')
    else:
        form = SubjectForm()
    return render(request, 'portal/add_subject.html', {'form': form})

def home(request):
    return render(request, 'portal/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You can now login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'portal/register.html', {'form': form})

@login_required
def student_dashboard(request):
    requests = ServiceRequest.objects.filter(student=request.user).order_by('-created_at')
    # Get all enrollments for list
    enrollments = Enrollment.objects.filter(student=request.user).select_related('subject')
    
    # Calculate stats for approved enrollments only
    approved_enrollments = enrollments.filter(status='approved')
    enrolled_count = approved_enrollments.count()
    total_credits = approved_enrollments.aggregate(Sum('subject__credits'))['subject__credits__sum'] or 0
    approved_requests_count = requests.filter(status='approved').count()
    
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.student = request.user
            service_request.save()
            messages.success(request, 'Request submitted successfully!')
            return redirect('student_dashboard')
    else:
        form = ServiceRequestForm()
    
    return render(request, 'portal/student_dashboard.html', {
        'requests': requests,
        'enrollments': enrollments,
        'enrolled_count': enrolled_count,
        'total_credits': total_credits,
        'approved_requests_count': approved_requests_count,
        'form': form,
    })



@staff_member_required
def update_request_status(request, request_id, new_status):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    if new_status in dict(ServiceRequest.STATUS_CHOICES):
        service_request.status = new_status
        service_request.save()
    return redirect('admin_dashboard')
