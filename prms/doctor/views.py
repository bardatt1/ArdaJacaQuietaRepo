from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Doctor, Patient
from django.contrib.auth.hashers import make_password, check_password

def doctor_register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        specialization = request.POST['specialization']

        # Check if the username already exists
        if Doctor.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose a different one.')
        else:
            # Create the new doctor
            Doctor.objects.create(
                username=username,
                password=make_password(password),  # Hash the password
                email=email,
                first_name=first_name,
                last_name=last_name,
                specialization=specialization,
            )
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    return render(request, 'registration.html')

def doctor_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Check if the doctor exists in the database
        try:
            doctor = Doctor.objects.get(username=username)
            if check_password(password, doctor.password):
                request.session['doctor_id'] = doctor.id
                return redirect('home')
            else:
                messages.error(request, 'Invalid password.')
        except Doctor.DoesNotExist:
            messages.error(request, 'Doctor not found. Please register first.')
    return render(request, 'login.html')

def doctor_home_view(request):
    if 'doctor_id' not in request.session:
        return redirect('login')
    
    doctor = Doctor.objects.get(id=request.session['doctor_id'])
    patients = doctor.patients.all()
    return render(request, 'home.html', {'doctor': doctor, 'patients': patients})

def add_patient_view(request):
    if 'doctor_id' not in request.session:
        return redirect('login')
    
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        age = request.POST['age']
        medical_history = request.POST['medical_history']
        doctor = Doctor.objects.get(id=request.session['doctor_id'])

        # Create the patient
        Patient.objects.create(
            doctor=doctor,
            first_name=first_name,
            last_name=last_name,
            age=age,
            medical_history=medical_history,
        )
        messages.success(request, 'Patient added successfully.')
        return redirect('home')
    return render(request, 'add_patient.html')


def doctor_logout_view(request):
    if 'doctor_id' in request.session:
        del request.session['doctor_id']  # Clear the doctor_id from the session
        messages.success(request, 'You have been logged out successfully.')
    return redirect('login')
