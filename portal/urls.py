from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Web Patterns
    path('', auth_views.LoginView.as_view(template_name='portal/login.html', redirect_authenticated_user=True), name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='portal/login.html'), name='login'),
    path('initialize-demo/', views.initialize_demo, name='initialize_demo'),
    
    # Subject Registration
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/enroll/<int:subject_id>/', views.enroll_subject, name='enroll_subject'),
    path('subjects/enroll/approve/<int:enrollment_id>/', views.approve_enrollment, name='approve_enrollment'),
    path('subjects/enroll/reject/<int:enrollment_id>/', views.reject_enrollment, name='reject_enrollment'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    
    # Core Student Navigation Routes
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('progress/', views.academic_progress, name='academic_progress'),
    path('grades/', views.grades_view, name='grades'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('registration/', views.registration_flow, name='registration'),
    path('registration/success/', views.registration_success, name='registration_success'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('help/', views.help_view, name='help'),
    
    # Auth & Admin Routes
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/redirect/', views.dashboard_redirect, name='dashboard_redirect'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
