import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from portal.models import Subject, Section

# Clear existing subjects and sections to avoid duplication
Section.objects.all().delete()
Subject.objects.all().delete()

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
        'description': 'Techniques of integration, infinite series, polar coordinates, and parametric equations.',
        'credits': 4,
        'category': 'Math/Science',
        'plan_year': 1,
        'plan_semester': 2,
        'prerequisites': 'MATH101',
        'sections': [
            {'section_number': '01', 'days_and_time': 'Mon/Wed 09:00 - 10:30', 'days_pattern': 'MW', 'time_start': datetime.time(9, 0), 'time_end': datetime.time(10, 30), 'instructor': 'Dr. Katherine Johnson', 'room': 'Science Hall 101', 'seats_total': 35, 'seats_available': 22, 'final_exam_date': 'Dec 15, 2026'},
        ]
    },
    {
        'name': 'Computer Programming',
        'code': 'CPE102',
        'description': 'Procedural programming, object-oriented concepts, recursion, and file manipulation.',
        'credits': 3,
        'category': 'CPE Core',
        'plan_year': 1,
        'plan_semester': 2,
        'prerequisites': 'CPE101',
        'sections': [
            {'section_number': '01', 'days_and_time': 'Tue/Thu 14:00 - 15:30', 'days_pattern': 'TR', 'time_start': datetime.time(14, 0), 'time_end': datetime.time(15, 30), 'instructor': 'Dr. Dennis Ritchie', 'room': 'Engineering Bldg 305', 'seats_total': 35, 'seats_available': 5, 'final_exam_date': 'Dec 18, 2026'},
        ]
    },
    # Year 2 Semester 1
    {
        'name': 'Digital Logic Design',
        'code': 'CPE201',
        'description': 'Boolean algebra, logic gates, combinational and sequential circuit design, and VHDL.',
        'credits': 4,
        'category': 'CPE Core',
        'plan_year': 2,
        'plan_semester': 1,
        'prerequisites': 'CPE102',
        'sections': [
            {'section_number': '01', 'days_and_time': 'Mon/Wed 14:00 - 15:30', 'days_pattern': 'MW', 'time_start': datetime.time(14, 0), 'time_end': datetime.time(15, 30), 'instructor': 'Dr. Claude Shannon', 'room': 'Logic Lab 102', 'seats_total': 30, 'seats_available': 8, 'final_exam_date': 'Dec 17, 2026'},
        ]
    },
    # Year 2 Semester 2
    {
        'name': 'Data Structures & Algorithms',
        'code': 'CPE202',
        'description': 'Stacks, queues, trees, graphs, sorting, searching, and algorithmic analysis.',
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
    # University Core
    {
        'name': 'Academic English',
        'code': 'HUM101',
        'description': 'Development of academic reading, writing, and analytical skills.',
        'credits': 3,
        'category': 'University Core',
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
    print(f"Created Subject: {subject.code} - {subject.name}")
    
    # Create sections
    for sec in item['sections']:
        section = Section.objects.create(
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
        print(f"  Created Section {section.section_number} at {section.days_and_time}")

print("Population of subjects and sections completed successfully!")
