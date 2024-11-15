from django import forms
from .models import Doctor

class DoctorProfileEditForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            'first_name', 'middle_name', 'last_name', 'birthday', 
            'gender', 'specialization', 'email'
        ]
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=[('Male', 'Male'), ('Female', 'Female')]),
        }
