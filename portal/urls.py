from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views, api_views

router = DefaultRouter()
router.register(r'api/v1/requests', api_views.ServiceRequestViewSet, basename='servicerequest')

urlpatterns = [
    # Web Patterns
    path('', auth_views.LoginView.as_view(template_name='portal/login.html', redirect_authenticated_user=True), name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='portal/login.html'), name='login'),
    
    # Subject Registration
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/enroll/<int:subject_id>/', views.enroll_subject, name='enroll_subject'),
    path('subjects/enroll/approve/<int:enrollment_id>/', views.approve_enrollment, name='approve_enrollment'),
    path('subjects/enroll/reject/<int:enrollment_id>/', views.reject_enrollment, name='reject_enrollment'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    
    # API Patterns
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/redirect/', views.dashboard_redirect, name='dashboard_redirect'),
    path('request/<int:request_id>/status/<str:new_status>/', views.update_request_status, name='update_request_status'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
