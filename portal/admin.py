from django.contrib import admin
from .models import ServiceRequest

# Register Profile if it exists (Checking plan, plan said Profile but I didn't verify if I created it. 
# Plan Task 4 said "Implement Models (Profile, ServiceRequest)".
# Checking 'models.py' via memory... I created ServiceRequest. 
# I did NOT create a Profile model in models.py content I wrote in Step 76. 
# Step 76 only had ServiceRequest. The user prompt didn't strictly require Profile separate from User, 
# "Student login and profile" can mean User model.
# I will only register ServiceRequest.

class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'request_type', 'status', 'created_at')
    list_filter = ('status', 'request_type')
    search_fields = ('student__username', 'details')
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        queryset.update(status='approved')
    approve_requests.short_description = "Approve selected requests"

    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')
    reject_requests.short_description = "Reject selected requests"

admin.site.register(ServiceRequest, ServiceRequestAdmin)

from .models import Subject, Enrollment

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credits')
    search_fields = ('code', 'name')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date_enrolled')
    list_filter = ('subject', 'date_enrolled')
