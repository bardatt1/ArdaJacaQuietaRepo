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

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} ({self.specialization})"

class Patient(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patients')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    sex = models.CharField(max_length=10, default="Unknown")
    contact_information = models.CharField(max_length=50, default="Not Provided")
    medical_history = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    details = models.TextField()

    def __str__(self):
        return f"Appointment with {self.patient} on {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"
