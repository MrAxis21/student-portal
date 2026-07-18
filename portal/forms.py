from django import forms
from .models import Subject

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description', 'credits', 'image']
        widgets = {
            'details': forms.Textarea(attrs={'rows': 4}),
        }
