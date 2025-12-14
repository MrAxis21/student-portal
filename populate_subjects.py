import os
import django
import shutil
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from portal.models import Subject

# Ensure media directory exists
MEDIA_ROOT = 'media/subjects/'
os.makedirs(MEDIA_ROOT, exist_ok=True)

subjects_data = [
    {
        'name': 'Web Development',
        'code': 'WEB101',
        'description': 'Learn HTML, CSS, JavaScript, and Django to build modern web applications.',
        'credits': 4,
        'image_src': r'C:/Users/yoda2/.gemini/antigravity/brain/76a44f89-743b-42f8-bd90-17e7bb6dc204/web_development_subject_1765029267208.png'
    },
    {
        'name': 'Embedded Systems',
        'code': 'EMB201',
        'description': 'Bridge the gap between hardware and software using microcontrollers.',
        'credits': 4,
        'image_src': r'C:/Users/yoda2/.gemini/antigravity/brain/76a44f89-743b-42f8-bd90-17e7bb6dc204/embedded_systems_subject_1765029284155.png'
    },
    {
        'name': 'Database Systems',
        'code': 'DB301',
        'description': 'Master SQL, NoSQL, and database design principles.',
        'credits': 3,
        'image_src': r'C:/Users/yoda2/.gemini/antigravity/brain/76a44f89-743b-42f8-bd90-17e7bb6dc204/database_subject_1765029304057.png'
    },
    {
        'name': 'Software Engineering',
        'code': 'SE401',
        'description': 'Understand the software lifecycle, agile methodologies, and testing.',
        'credits': 3,
        'image_src': r'C:/Users/yoda2/.gemini/antigravity/brain/76a44f89-743b-42f8-bd90-17e7bb6dc204/software_engineering_subject_1765029320420.png'
    }
]

for item in subjects_data:
    subject, created = Subject.objects.get_or_create(
        code=item['code'],
        defaults={
            'name': item['name'],
            'description': item['description'],
            'credits': item['credits']
        }
    )
    
    if created or not subject.image:
        print(f"Updating image for {subject.name}")
        src = item['image_src']
        if os.path.exists(src):
            with open(src, 'rb') as f:
                subject.image.save(os.path.basename(src), File(f), save=True)
        else:
            print(f"Image not found: {src}")
    
    # Update description/credits just in case
    subject.description = item['description']
    subject.credits = item['credits']
    subject.save()
    print(f"Processed {subject.name}")

print("Population complete.")
