from django import forms
from .models import ServiceRequest, Subject

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['request_type', 'details']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description', 'credits', 'image']
        widgets = {
            'details': forms.Textarea(attrs={'rows': 4}),
        }
