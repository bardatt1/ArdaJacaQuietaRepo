from django import forms
from django.core.exceptions import ValidationError
from .models import Doctor
from django.contrib.auth.hashers import make_password
from .models import Appointment

class DoctorProfileEditForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            'first_name', 'middle_name', 'last_name', 'birthday',
            'gender', 'specialization', 'email', 'hospital_assigned', 'profile_picture'
        ]
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=[('Male', 'Male'), ('Female', 'Female')]),
        }



class DoctorRegistrationForm(forms.ModelForm):
    password_confirmation = forms.CharField(max_length=100, widget=forms.PasswordInput)

    class Meta:
        model = Doctor
        fields = ['username', 'password']
    
    # Clean the username to ensure it is unique
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Doctor.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError("Password cannot be empty.")
        return make_password(password)  # Hash the password before saving

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password != password_confirmation:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    # Override the save method to ensure unique username and hash password
    def save(self, commit=True):
        doctor = super().save(commit=False)
        doctor.password = make_password(doctor.password)  # Hash the password
        if commit:
            doctor.save()
        return doctor
    

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'appointment_type', 'location', 'details']
