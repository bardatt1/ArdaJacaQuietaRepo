from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Doctor, Patient, Appointment
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

def registration_step1(request):
    if request.method == 'POST':
        request.session['first_name'] = request.POST.get('first_name')
        request.session['middle_name'] = request.POST.get('middle_name')
        request.session['last_name'] = request.POST.get('last_name')
        request.session['birthday'] = request.POST.get('birthday')
        request.session['gender'] = request.POST.get('gender')
        request.session['email'] = request.POST.get('email')
        request.session['username'] = request.POST.get('username')
        request.session['password'] = request.POST.get('password')
        return redirect(reverse('registration_step2'))
    return render(request, 'registration_step1.html')

def registration_step2(request):
    print(f"Session Data - Username: {request.session.get('username')}, First Name: {request.session.get('first_name')}, Last Name: {request.session.get('last_name')}")
    if request.method == 'POST':
        first_name = request.session.get('first_name')
        middle_name = request.session.get('middle_name')
        last_name = request.session.get('last_name')
        birthday = request.session.get('birthday')
        gender = request.session.get('gender')
        email = request.session.get('email')
        username = request.session.get('username')
        password = make_password(request.session.get('password'))
        if not username:
            print("Error: Username is missing from the session.")
            return render(request, 'registration_step1.html', {"error": "Username is required."})
        specialization = request.POST.get('specialization')
        doctor = Doctor.objects.create(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            birthday=birthday,
            gender=gender,
            specialization=specialization,
        )
        return redirect('registration_complete')
    return render(request, 'registration_step2.html')

def registration_complete(request):
    return render(request, 'registration_complete.html')

def doctor_login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            doctor = Doctor.objects.get(username=username)
            if check_password(password, doctor.password):
                request.session['doctor_id'] = doctor.id
                return redirect("home")  
            else:
                messages.error(request, "Invalid username or password")  
        except Doctor.DoesNotExist:
            messages.error(request, "Doctor not found. Please register first.")
    return render(request, "login.html") 

def doctor_home_view(request):
    doctor_id = request.session.get('doctor_id')
    if doctor_id is None:
        return redirect('login')
    doctor = get_object_or_404(Doctor, id=doctor_id)
    patients = doctor.patients.all().order_by('-created_at')
    return render(request, 'home.html', {'doctor': doctor, 'patients': patients})

def add_patient_view(request):
    if 'doctor_id' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        first_name = request.POST['first_name']
        middle_name = request.POST['middle_name']
        last_name = request.POST['last_name']
        age = request.POST['age']
        sex = request.POST['sex']
        contact_information = request.POST['contact_information']
        medical_history = request.POST['medical_history']
        doctor = Doctor.objects.get(id=request.session['doctor_id'])
        Patient.objects.create(
            doctor=doctor,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            age=age,
            sex=sex,
            contact_information=contact_information,
            medical_history=medical_history,
        )
        return redirect('home')
    return render(request, 'add_patient.html')

def doctor_logout_view(request):
    if 'doctor_id' in request.session:
        del request.session['doctor_id']  
        messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

def appointments_view(request):
    doctor_id = request.session.get('doctor_id')
    if doctor_id is None:
        return redirect('login')
    doctor = get_object_or_404(Doctor, id=doctor_id)
    appointments = doctor.appointments.all()  
    return render(request, 'appointments.html', {'doctor': doctor, 'appointments': appointments})

def patient_list_view(request):
    """View to list all patients associated with the logged-in doctor."""
    doctor_id = request.session.get('doctor_id')
    if doctor_id is None:
        return redirect('login')
    doctor = get_object_or_404(Doctor, id=doctor_id)
    patients = doctor.patients.all().order_by('-created_at')
    return render(request, 'patient_list.html', {'doctor': doctor, 'patients': patients})

def activities_view(request):
    """View to display recent activities for the doctor."""
    doctor_id = request.session.get('doctor_id')
    if doctor_id is None:
        return redirect('login')
    doctor = get_object_or_404(Doctor, id=doctor_id)
    activities = doctor.activities.all()  
    return render(request, 'activities.html', {'doctor': doctor, 'activities': activities})

def edit_patient_view(request, patient_id):
    if 'doctor_id' not in request.session:
        return redirect('login')
    
    patient = get_object_or_404(Patient, id=patient_id, doctor_id=request.session['doctor_id'])
    
    if request.method == 'POST':
        patient.first_name = request.POST['first_name']
        patient.middle_name = request.POST['middle_name']
        patient.last_name = request.POST['last_name']
        patient.age = request.POST['age']
        patient.sex = request.POST['sex']
        patient.contact_information = request.POST['contact_information']
        patient.medical_history = request.POST['medical_history']
        patient.save()
        return redirect('patients')
    
    return render(request, 'edit_patient.html', {'patient': patient})


def delete_patient_view(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id, doctor_id=request.session.get('doctor_id'))
    
    if request.method == 'POST':
        patient.delete()
        return redirect('patients')
    
    return render(request, 'confirm_delete_patient.html', {'patient': patient})