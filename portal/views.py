from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db import models
from django.db.models import Sum
from .models import Subject, Enrollment, Section, StudentCourseGrade, Notification
from .forms import SubjectForm

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
            # Check if there is any section with available seats
            available_sections = subject.sections.filter(seats_available__gt=0)
            if available_sections.exists():
                sec = available_sections.first()
                Enrollment.objects.create(
                    student=request.user, 
                    subject=subject, 
                    section=sec, 
                    status='approved'
                )
                sec.seats_available -= 1
                sec.save()
                messages.success(request, f'Successfully registered for {subject.name}!')
            else:
                Enrollment.objects.create(student=request.user, subject=subject, status='pending')
                messages.success(request, f'Enrollment requested for {subject.name}. Waiting for approval.')
            
    return redirect('subject_list')

@staff_member_required
def admin_dashboard(request):
    # Fetch pending enrollments
    pending_enrollments = Enrollment.objects.filter(status='pending').select_related('student', 'subject')
    total_subjects_count = Subject.objects.count()
        
    return render(request, 'portal/admin_dashboard.html', {
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
    # Fetch unread notifications count
    unread_notifs = Notification.objects.filter(student=request.user, is_read=False).count()
    
    # Calculate GPA
    grades = StudentCourseGrade.objects.filter(student=request.user).select_related('subject')
    total_completed_credits = sum(g.subject.credits for g in grades)
    weighted_points = sum(g.points * g.subject.credits for g in grades)
    gpa = round(weighted_points / total_completed_credits, 2) if total_completed_credits > 0 else 0.0
    
    # Calculate major GPA (using CPE core subjects)
    major_grades = [g for g in grades if g.subject.category == 'CPE Core']
    major_completed_credits = sum(g.subject.credits for g in major_grades)
    major_weighted_points = sum(g.points * g.subject.credits for g in major_grades)
    major_gpa = round(major_weighted_points / major_completed_credits, 2) if major_completed_credits > 0 else 0.0
    
    # Calculate degree completion progress
    total_curriculum_credits = Subject.objects.aggregate(Sum('credits'))['credits__sum'] or 1
    completion_percentage = int((total_completed_credits / total_curriculum_credits) * 100)
    
    # Active enrollments
    enrollments = Enrollment.objects.filter(student=request.user).select_related('subject', 'section')
    approved_enrollments = enrollments.filter(status='approved')
    enrolled_count = approved_enrollments.count()
    active_credits = approved_enrollments.aggregate(Sum('subject__credits'))['subject__credits__sum'] or 0
    
    # Hold status warning (simulating a hold if username is student_hold)
    holds = ['Library Fee Hold ($15.00)'] if request.user.username == 'student_hold' else []
    
    # Recommended courses (prerequisites met, not yet completed or registered)
    completed_codes = {g.subject.code for g in grades}
    registered_codes = {e.subject.code for e in enrollments}
    recommended = []
    
    for s in Subject.objects.all():
        if s.code not in completed_codes and s.code not in registered_codes:
            # Check prerequisites
            prereq = s.prerequisites
            if prereq == 'None' or all(p.strip() in completed_codes for p in prereq.split(',')):
                recommended.append(s)
                if len(recommended) >= 3:
                    break
                    
    # Notifications feed (up to 3 recent notifications)
    recent_notifications = Notification.objects.filter(student=request.user).order_by('-created_at')[:3]
                    
    return render(request, 'portal/student_dashboard.html', {
        'enrollments': enrollments,
        'enrolled_count': enrolled_count,
        'total_credits': active_credits,
        'cumulative_gpa': gpa,
        'major_gpa': major_gpa,
        'completion_percentage': completion_percentage,
        'completed_credits': total_completed_credits,
        'total_curriculum_credits': total_curriculum_credits,
        'holds': holds,
        'recommended': recommended,
        'unread_notifs': unread_notifs,
        'recent_notifications': recent_notifications,
    })

@login_required
def academic_progress(request):
    grades = StudentCourseGrade.objects.filter(student=request.user)
    completed_subject_ids = {g.subject_id for g in grades}
    enrollments = Enrollment.objects.filter(student=request.user)
    enrollment_status = {e.subject_id: e.status for e in enrollments}
    
    categories = ['University Core', 'College Core', 'Math/Science', 'CPE Core', 'Technical Elective', 'General Elective']
    grouped_subjects = {}
    
    total_credits = 0
    completed_credits = 0
    
    for cat in categories:
        subjects = Subject.objects.filter(category=cat)
        cat_subjects = []
        for s in subjects:
            total_credits += s.credits
            status = 'remaining'
            if s.id in completed_subject_ids:
                status = 'completed'
                completed_credits += s.credits
            elif s.id in enrollment_status:
                status = enrollment_status[s.id] # 'pending' or 'approved'
            
            cat_subjects.append({
                'subject': s,
                'status': status
            })
        grouped_subjects[cat] = cat_subjects
        
    completion_percentage = int((completed_credits / total_credits) * 100) if total_credits > 0 else 0

    return render(request, 'portal/progress.html', {
        'grouped_subjects': grouped_subjects,
        'completed_credits': completed_credits,
        'total_credits': total_credits,
        'completion_percentage': completion_percentage,
    })

@login_required
def grades_view(request):
    grades = StudentCourseGrade.objects.filter(student=request.user).select_related('subject')
    
    # Group grades by term
    grades_by_term = {}
    for g in grades:
        grades_by_term.setdefault(g.term, []).append(g)
        
    # Calculate current GPA stats
    total_completed_credits = sum(g.subject.credits for g in grades)
    weighted_points = sum(g.points * g.subject.credits for g in grades)
    gpa = round(weighted_points / total_completed_credits, 2) if total_completed_credits > 0 else 0.0
    
    # Fetch active enrollments (courses currently registered or pending) for the calculator
    current_enrollments = Enrollment.objects.filter(student=request.user).exclude(status='rejected').select_related('subject')
    
    return render(request, 'portal/grades.html', {
        'grades_by_term': grades_by_term,
        'cumulative_gpa': gpa,
        'total_credits': total_completed_credits,
        'current_enrollments': current_enrollments,
    })

@login_required
def notifications_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_all_read':
            Notification.objects.filter(student=request.user).update(is_read=True)
            messages.success(request, 'All notifications marked as read.')
        elif action == 'delete':
            notif_id = request.POST.get('notif_id')
            Notification.objects.filter(student=request.user, id=notif_id).delete()
            messages.success(request, 'Notification dismissed.')
        return redirect('notifications')
        
    notifications = Notification.objects.filter(student=request.user).order_by('-created_at')
    
    # Categorized unread counts
    unread_counts = {
        'all': notifications.filter(is_read=False).count(),
        'seats': notifications.filter(category='seats', is_read=False).count(),
        'deadlines': notifications.filter(category='deadlines', is_read=False).count(),
        'rooms': notifications.filter(category='rooms', is_read=False).count(),
    }
    
    # Mark read when viewing notifications list
    notifications.filter(student=request.user).update(is_read=True)
    
    return render(request, 'portal/notifications.html', {
        'notifications': notifications,
        'unread_counts': unread_counts,
    })

@login_required
def registration_flow(request):
    draft_ids = request.session.get('registration_draft', [])
    
    # Actions
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_draft':
            section_id = int(request.POST.get('section_id'))
            section = get_object_or_404(Section, id=section_id)
            
            # Double check already enrolled
            if Enrollment.objects.filter(student=request.user, subject=section.subject, status='approved').exists():
                messages.warning(request, f'You are already registered for {section.subject.code}.')
            elif section_id not in draft_ids:
                # Check for duplicates or time conflicts
                draft_sections = Section.objects.filter(id__in=draft_ids).select_related('subject')
                has_conflict = False
                for ds in draft_sections:
                    # Duplicate subject check
                    if ds.subject_id == section.subject_id:
                        messages.warning(request, f'You have already chosen a section of {section.subject.code}.')
                        has_conflict = True
                        break
                    # Simple time conflict check
                    if ds.days_pattern == section.days_pattern and ds.time_start == section.time_start:
                        messages.warning(request, f'Time conflict: Section overlaps with {ds.subject.code} Sec {ds.section_number}.')
                        has_conflict = True
                        break
                        
                if not has_conflict:
                    draft_ids.append(section_id)
                    request.session['registration_draft'] = draft_ids
                    messages.success(request, f'Added {section.subject.code} Section {section.section_number} to draft registration plan.')
        elif action == 'remove_draft':
            section_id = int(request.POST.get('section_id'))
            if section_id in draft_ids:
                draft_ids.remove(section_id)
                request.session['registration_draft'] = draft_ids
                messages.success(request, 'Removed course from plan.')
        elif action == 'submit_registration':
            # Create enrollments
            draft_sections = Section.objects.filter(id__in=draft_ids).select_related('subject')
            for sec in draft_sections:
                # Avoid duplicate enrollments
                if not Enrollment.objects.filter(student=request.user, subject=sec.subject).exists():
                    if sec.seats_available > 0:
                        Enrollment.objects.create(
                            student=request.user,
                            subject=sec.subject,
                            section=sec,
                            status='approved'
                        )
                        sec.seats_available -= 1
                        sec.save()
                    else:
                        Enrollment.objects.create(
                            student=request.user,
                            subject=sec.subject,
                            section=sec,
                            status='pending'
                        )
            # Clear draft
            request.session['registration_draft'] = []
            return redirect('registration_success')
            
        return redirect('registration')
        
    # Get subjects for Major Sheet
    subjects = Subject.objects.all().order_by('plan_year', 'plan_semester')
    
    # Check student grades and existing enrollments
    grades = StudentCourseGrade.objects.filter(student=request.user)
    completed_codes = {g.subject.code for g in grades}
    
    enrollments = Enrollment.objects.filter(student=request.user).select_related('subject')
    enrollment_status = {e.subject.code: e.status for e in enrollments} # subject.code -> status
    
    # Draft details
    draft_sections = Section.objects.filter(id__in=draft_ids).select_related('subject')
    
    # Prep subjects list with custom status
    subjects_status = []
    for s in subjects:
        status = 'eligible'
        if s.code in completed_codes:
            status = 'completed'
        elif s.code in enrollment_status:
            status = enrollment_status[s.code] # 'pending' or 'approved'
        else:
            # Check prerequisites
            prereqs = s.prerequisites
            if prereqs != 'None':
                prereq_list = [p.strip() for p in prereqs.split(',')]
                # If any prereq is not met
                if not all(p in completed_codes for p in prereq_list):
                    status = 'locked'
        
        subjects_status.append({
            'subject': s,
            'status': status
        })
        
    # Search Query
    search_query = request.GET.get('q', '')
    search_dept = request.GET.get('dept', '')
    
    search_results = []
    if search_query or search_dept:
        search_results = Subject.objects.all()
        if search_query:
            search_results = search_results.filter(models.Q(name__icontains=search_query) | models.Q(code__icontains=search_query))
        if search_dept:
            search_results = search_results.filter(category=search_dept)
            
    # Load all sections
    sections = Section.objects.all().select_related('subject')
    
    # Identify which sections are in draft or registered
    draft_section_ids = set(draft_ids)
    registered_subject_ids = {e.subject_id for e in enrollments if e.status == 'approved'}

    return render(request, 'portal/registration.html', {
        'subjects_status': subjects_status,
        'draft_sections': draft_sections,
        'sections': sections,
        'draft_section_ids': draft_section_ids,
        'registered_subject_ids': registered_subject_ids,
        'search_query': search_query,
        'search_dept': search_dept,
        'search_results': search_results,
    })

@login_required
def registration_success(request):
    return render(request, 'portal/registration_success.html')

@login_required
def schedule_view(request):
    enrollments = Enrollment.objects.filter(student=request.user, status='approved').select_related('subject', 'section')
    
    # Format schedule events for rendering
    events = []
    for e in enrollments:
        if e.section:
            events.append({
                'subject': e.subject,
                'section': e.section,
                'days_pattern': e.section.days_pattern,
                'time_start': e.section.time_start.strftime("%H:%M") if e.section.time_start else "",
                'time_end': e.section.time_end.strftime("%H:%M") if e.section.time_end else "",
                'room': e.section.room,
                'instructor': e.section.instructor
            })
            
    return render(request, 'portal/schedule.html', {
        'events': events,
    })

@login_required
def help_view(request):
    return render(request, 'portal/help.html')

def initialize_demo(request):
    if request.method == 'POST':
        from django.contrib.auth.models import User
        from portal.models import Subject, Section, StudentCourseGrade, Notification
        import datetime

        try:
            # 1. Create default users
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
            if not User.objects.filter(username='student').exists():
                User.objects.create_user('student', 'student@example.com', 'studentpass')
                
            student = User.objects.get(username='student')

            # 2. Clear subjects and grades
            Section.objects.all().delete()
            Subject.objects.all().delete()
            StudentCourseGrade.objects.filter(student=student).delete()
            Notification.objects.filter(student=student).delete()

            # 3. Create subjects data
            subjects_data = [
                # Year 1 Semester 1
                {
                    'name': 'Calculus I',
                    'code': 'MATH101',
                    'description': 'Limits, derivatives, integrals, and their applications in science and engineering.',
                    'credits': 4,
                    'category': 'Math/Science',
                    'plan_year': 1,
                    'plan_semester': 1,
                    'prerequisites': 'None',
                    'sections': [
                        {'section_number': '01', 'days_and_time': 'Mon/Wed 09:00 - 10:30', 'days_pattern': 'MW', 'time_start': datetime.time(9, 0), 'time_end': datetime.time(10, 30), 'instructor': 'Dr. Alan Turing', 'room': 'Science Hall 101', 'seats_total': 40, 'seats_available': 12, 'final_exam_date': 'Dec 15, 2026'},
                        {'section_number': '02', 'days_and_time': 'Tue/Thu 11:00 - 12:30', 'days_pattern': 'TR', 'time_start': datetime.time(11, 0), 'time_end': datetime.time(12, 30), 'instructor': 'Dr. Grace Hopper', 'room': 'Science Hall 102', 'seats_total': 40, 'seats_available': 28, 'final_exam_date': 'Dec 16, 2026'},
                    ]
                },
                {
                    'name': 'Intro to Computing',
                    'code': 'CPE101',
                    'description': 'Introduction to computer architecture, software development concepts, and binary math.',
                    'credits': 3,
                    'category': 'CPE Core',
                    'plan_year': 1,
                    'plan_semester': 1,
                    'prerequisites': 'None',
                    'sections': [
                        {'section_number': '01', 'days_and_time': 'Mon/Wed 11:00 - 12:30', 'days_pattern': 'MW', 'time_start': datetime.time(11, 0), 'time_end': datetime.time(12, 30), 'instructor': 'Dr. Ada Lovelace', 'room': 'Engineering Bldg 204', 'seats_total': 35, 'seats_available': 0, 'final_exam_date': 'Dec 14, 2026'},
                        {'section_number': '02', 'days_and_time': 'Tue/Thu 09:00 - 10:30', 'days_pattern': 'TR', 'time_start': datetime.time(9, 0), 'time_end': datetime.time(10, 30), 'instructor': 'Dr. Charles Babbage', 'room': 'Engineering Bldg 204', 'seats_total': 35, 'seats_available': 15, 'final_exam_date': 'Dec 14, 2026'},
                    ]
                },
                # Year 1 Semester 2
                {
                    'name': 'Calculus II',
                    'code': 'MATH102',
                    'description': 'Techniques of integration, sequences, series, and power series.',
                    'credits': 4,
                    'category': 'Math/Science',
                    'plan_year': 1,
                    'plan_semester': 2,
                    'prerequisites': 'MATH101',
                    'sections': [
                        {'section_number': '01', 'days_and_time': 'Mon/Wed 09:00 - 10:30', 'days_pattern': 'MW', 'time_start': datetime.time(9, 0), 'time_end': datetime.time(10, 30), 'instructor': 'Dr. Alan Turing', 'room': 'Science Hall 101', 'seats_total': 40, 'seats_available': 12, 'final_exam_date': 'Dec 15, 2026'},
                    ]
                },
                {
                    'name': 'Computer Programming',
                    'code': 'CPE102',
                    'description': 'Core programming constructs, functions, arrays, objects, and console I/O using Python.',
                    'credits': 3,
                    'category': 'CPE Core',
                    'plan_year': 1,
                    'plan_semester': 2,
                    'prerequisites': 'CPE101',
                    'sections': [
                        {'section_number': '01', 'days_and_time': 'Tue/Thu 14:00 - 15:30', 'days_pattern': 'TR', 'time_start': datetime.time(14, 0), 'time_end': datetime.time(15, 30), 'instructor': 'Dr. Charles Babbage', 'room': 'Engineering Bldg 204', 'seats_total': 35, 'seats_available': 15, 'final_exam_date': 'Dec 14, 2026'},
                    ]
                },
                # Year 2 Semester 1
                {
                    'name': 'Digital Logic Design',
                    'code': 'CPE201',
                    'description': 'Number systems, boolean algebra, logic gates, combinational and sequential circuit design.',
                    'credits': 4,
                    'category': 'CPE Core',
                    'plan_year': 2,
                    'plan_semester': 1,
                    'prerequisites': 'CPE101',
                    'sections': [
                        {'section_number': '01', 'days_and_time': 'Mon/Wed 14:00 - 15:30', 'days_pattern': 'MW', 'time_start': datetime.time(14, 0), 'time_end': datetime.time(15, 30), 'instructor': 'Dr. Grace Hopper', 'room': 'Engineering Bldg 103', 'seats_total': 30, 'seats_available': 20, 'final_exam_date': 'Dec 16, 2026'},
                    ]
                },
                # Year 2 Semester 2
                {
                    'name': 'Data Structures & Algorithms',
                    'code': 'CPE202',
                    'description': 'Stacks, queues, linked lists, trees, graphs, sorting, and big-O time complexity analysis.',
                    'credits': 4,
                    'category': 'CPE Core',
                    'plan_year': 2,
                    'plan_semester': 2,
                    'prerequisites': 'CPE102',
                    'sections': [
                        {'section_number': '01', 'days_and_time': 'Tue/Thu 09:00 - 10:30', 'days_pattern': 'TR', 'time_start': datetime.time(9, 0), 'time_end': datetime.time(10, 30), 'instructor': 'Dr. Donald Knuth', 'room': 'Engineering Bldg 202', 'seats_total': 30, 'seats_available': 14, 'final_exam_date': 'Dec 15, 2026'},
                        {'section_number': '02', 'days_and_time': 'Mon/Wed 11:00 - 12:30', 'days_pattern': 'MW', 'time_start': datetime.time(11, 0), 'time_end': datetime.time(12, 30), 'instructor': 'Dr. Donald Knuth', 'room': 'Engineering Bldg 202', 'seats_total': 30, 'seats_available': 2, 'final_exam_date': 'Dec 15, 2026'},
                    ]
                },
                # Year 3 Semester 1
                {
                    'name': 'Embedded Systems',
                    'code': 'CPE502',
                    'description': 'Bridge the gap between hardware and software using microcontrollers and RTOS.',
                    'credits': 4,
                    'category': 'CPE Core',
                    'plan_year': 3,
                    'plan_semester': 1,
                    'prerequisites': 'CPE201',
                    'sections': [
                        {'section_number': '01', 'days_and_time': 'Tue/Thu 11:00 - 12:30', 'days_pattern': 'TR', 'time_start': datetime.time(11, 0), 'time_end': datetime.time(12, 30), 'instructor': 'Dr. Ken Thompson', 'room': 'Hardware Lab 105', 'seats_total': 25, 'seats_available': 11, 'final_exam_date': 'Dec 17, 2026'},
                    ]
                },
                {
                    'name': 'Database Systems',
                    'code': 'DB301',
                    'description': 'Master SQL, NoSQL, and database design principles.',
                    'credits': 3,
                    'category': 'CPE Core',
                    'plan_year': 3,
                    'plan_semester': 1,
                    'prerequisites': 'CPE202',
                    'sections': [
                        {'section_number': '01', 'days_and_time': 'Tue/Thu 11:00 - 12:30', 'days_pattern': 'TR', 'time_start': datetime.time(11, 0), 'time_end': datetime.time(12, 30), 'instructor': 'Dr. Edgar F. Codd', 'room': 'Engineering Bldg 103', 'seats_total': 40, 'seats_available': 4, 'final_exam_date': 'Dec 13, 2026'},
                    ]
                },
                # Year 3 Semester 2
                {
                    'name': 'Operating Systems',
                    'code': 'CPE302',
                    'description': 'Processes, threads, memory management, file systems, and scheduling.',
                    'credits': 4,
                    'category': 'CPE Core',
                    'plan_year': 3,
                    'plan_semester': 2,
                    'prerequisites': 'CPE202',
                    'sections': [
                        {'section_number': '01', 'days_and_time': 'Mon/Wed 14:00 - 15:30', 'days_pattern': 'MW', 'time_start': datetime.time(14, 0), 'time_end': datetime.time(15, 30), 'instructor': 'Dr. Linus Torvalds', 'room': 'Engineering Bldg 202', 'seats_total': 30, 'seats_available': 18, 'final_exam_date': 'Dec 16, 2026'},
                    ]
                },
                # Year 4 Semester 1
                {
                    'name': 'Software Engineering',
                    'code': 'SE401',
                    'description': 'Understand the software lifecycle, agile methodologies, and testing.',
                    'credits': 3,
                    'category': 'CPE Core',
                    'plan_year': 4,
                    'plan_semester': 1,
                    'prerequisites': 'CPE202',
                    'sections': [
                        {'section_number': '01', 'days_and_time': 'Tue/Thu 09:00 - 10:30', 'days_pattern': 'TR', 'time_start': datetime.time(9, 0), 'time_end': datetime.time(10, 30), 'instructor': 'Dr. Margaret Hamilton', 'room': 'Software Lab 112', 'seats_total': 35, 'seats_available': 20, 'final_exam_date': 'Dec 14, 2026'},
                    ]
                },
                # Technical Electives
                {
                    'name': 'Machine Learning',
                    'code': 'CPE501',
                    'description': 'Supervised and unsupervised learning, regression, neural networks, and decision trees.',
                    'credits': 3,
                    'category': 'Technical Elective',
                    'plan_year': 5,
                    'plan_semester': 1,
                    'prerequisites': 'MATH102',
                    'sections': [
                        {'section_number': '01', 'days_and_time': 'Mon/Wed 16:00 - 17:30', 'days_pattern': 'MW', 'time_start': datetime.time(16, 0), 'time_end': datetime.time(17, 30), 'instructor': 'Dr. Yann LeCun', 'room': 'Engineering Bldg 312', 'seats_total': 25, 'seats_available': 2, 'final_exam_date': 'Dec 18, 2026'},
                    ]
                },
                # Humanities
                {
                    'name': 'Academic English',
                    'code': 'HUM101',
                    'description': 'Critical reading, essay writing, and research skills for academic purposes.',
                    'credits': 3,
                    'category': 'Humanities',
                    'plan_year': 1,
                    'plan_semester': 1,
                    'prerequisites': 'None',
                    'sections': [
                        {'section_number': '01', 'days_and_time': 'Mon/Wed 12:30 - 14:00', 'days_pattern': 'MW', 'time_start': datetime.time(12, 30), 'time_end': datetime.time(14, 0), 'instructor': 'Prof. William Shakespeare', 'room': 'Liberal Arts 101', 'seats_total': 30, 'seats_available': 10, 'final_exam_date': 'Dec 13, 2026'},
                    ]
                },
                # General Electives
                {
                    'name': 'Intro to Sociology',
                    'code': 'SOC101',
                    'description': 'Analysis of human social behavior, culture, and institutions.',
                    'credits': 3,
                    'category': 'General Elective',
                    'plan_year': 2,
                    'plan_semester': 1,
                    'prerequisites': 'None',
                    'sections': [
                        {'section_number': '01', 'days_and_time': 'Tue/Thu 12:30 - 14:00', 'days_pattern': 'TR', 'time_start': datetime.time(12, 30), 'time_end': datetime.time(14, 0), 'instructor': 'Prof. Max Weber', 'room': 'Liberal Arts 203', 'seats_total': 45, 'seats_available': 34, 'final_exam_date': 'Dec 14, 2026'},
                    ]
                },
                {
                    'name': 'Web Development',
                    'code': 'WEB101',
                    'description': 'Learn HTML, CSS, JavaScript, and Django to build modern web applications.',
                    'credits': 4,
                    'category': 'Technical Elective',
                    'plan_year': 5,
                    'plan_semester': 2,
                    'prerequisites': 'CPE202',
                    'sections': [
                        {'section_number': '01', 'days_and_time': 'Mon/Wed 09:00 - 10:30', 'days_pattern': 'MW', 'time_start': datetime.time(9, 0), 'time_end': datetime.time(10, 30), 'instructor': 'Dr. Tim Berners-Lee', 'room': 'Engineering Bldg 110', 'seats_total': 35, 'seats_available': 10, 'final_exam_date': 'Dec 12, 2026'},
                        {'section_number': '02', 'days_and_time': 'Tue/Thu 14:00 - 15:30', 'days_pattern': 'TR', 'time_start': datetime.time(14, 0), 'time_end': datetime.time(15, 30), 'instructor': 'Dr. Tim Berners-Lee', 'room': 'Engineering Bldg 110', 'seats_total': 35, 'seats_available': 35, 'final_exam_date': 'Dec 12, 2026'},
                    ]
                }
            ]

            for item in subjects_data:
                subject = Subject.objects.create(
                    name=item['name'],
                    code=item['code'],
                    description=item['description'],
                    credits=item['credits'],
                    category=item['category'],
                    plan_year=item['plan_year'],
                    plan_semester=item['plan_semester'],
                    prerequisites=item['prerequisites']
                )
                for sec in item['sections']:
                    Section.objects.create(
                        subject=subject,
                        section_number=sec['section_number'],
                        days_and_time=sec['days_and_time'],
                        days_pattern=sec['days_pattern'],
                        time_start=sec['time_start'],
                        time_end=sec['time_end'],
                        instructor=sec['instructor'],
                        room=sec['room'],
                        seats_total=sec['seats_total'],
                        seats_available=sec['seats_available'],
                        final_exam_date=sec['final_exam_date']
                    )

            # 4. Create grades & notifications
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
                try:
                    subject = Subject.objects.get(code=g['code'])
                    StudentCourseGrade.objects.create(
                        student=student,
                        subject=subject,
                        grade=g['grade'],
                        points=g['points'],
                        term=g['term']
                    )
                except Subject.DoesNotExist:
                    pass

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
                Notification.objects.create(
                    student=student,
                    title=n['title'],
                    message=n['message'],
                    category=n['category'],
                    is_read=False,
                    link=n['link']
                )
            
            messages.success(request, 'Database successfully initialized! Log in with username: student and password: studentpass')
        except Exception as e:
            messages.error(request, f'Failed to initialize database: {e}')
            
    return redirect('login')
