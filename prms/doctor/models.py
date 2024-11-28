from django.db import models
from django.utils import timezone

class Doctor(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    specialization = models.CharField(max_length=100)
    hospital_assigned = models.CharField(max_length=255, blank=True, default="")
    profile_picture = models.ImageField(
        upload_to='doctor_profile_pics/', 
        blank=True, 
        null=True, 
        help_text="Upload a profile picture for the doctor."
    )

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} ({self.specialization})"


class Document(models.Model):
    doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    file = models.FileField(
        upload_to='doctor_documents/', 
        help_text="Upload a document (e.g., certificates)."
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.doctor.first_name} {self.doctor.last_name}"

class Patient(models.Model):
    SEX_CHOICES = [
        ('', 'Select Sex'),  # This will show as the default option
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patients')
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    sex = models.CharField(max_length=6, choices=SEX_CHOICES, blank=False)
    phone_number = models.CharField(max_length=255, blank=True, default="Not provided")
    medical_history = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    appointment_type = models.CharField(max_length=50, default='consultation')
    location = models.CharField(max_length=100, default="Unknown Location")
    details = models.TextField()

    def __str__(self):
        return f"Appointment with {self.patient} on {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"
    
class Activity(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='activities')
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Activity by {self.doctor.first_name} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

