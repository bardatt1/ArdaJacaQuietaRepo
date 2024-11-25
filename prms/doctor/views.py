from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
from .models import Doctor, Patient, Appointment, Activity
from .forms import DoctorProfileEditForm
from datetime import datetime
from django.db.models import Q

# Helper function to ensure a doctor is logged in
def doctor_logged_in(request):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('login')
    return doctor_id

def registration_step1(request):
    if request.method == 'POST':
        # Store form data in session
        request.session['first_name'] = request.POST.get('first_name')
        request.session['middle_name'] = request.POST.get('middle_name')
        request.session['last_name'] = request.POST.get('last_name')
        request.session['birthday'] = request.POST.get('birthday')
        request.session['gender'] = request.POST.get('gender')
        request.session['email'] = request.POST.get('email')
        request.session['username'] = request.POST.get('username')
        request.session['password'] = request.POST.get('password')
        request.session['hospital_assigned'] = request.POST.get('hospital_assigned')
        return redirect(reverse('registration_step2'))
    return render(request, 'registration_step1.html')

def registration_step2(request):
    # Check if session data exists and process it
    print(f"Session Data - Username: {request.session.get('username')}, First Name: {request.session.get('first_name')}, Last Name: {request.session.get('last_name')}")
    if request.method == 'POST':
        # Get session data for doctor registration
        first_name = request.session.get('first_name')
        middle_name = request.session.get('middle_name')
        last_name = request.session.get('last_name')
        birthday = request.session.get('birthday')
        gender = request.session.get('gender')
        email = request.session.get('email')
        username = request.session.get('username')
        password = make_password(request.session.get('password'))
        hospital_assigned = request.session.get('hospital_assigned')
        
        if not username:
            return render(request, 'registration_step1.html', {"error": "Username is required."})

        # Register doctor
        specialization = request.POST.get('specialization')
        Doctor.objects.create(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            birthday=birthday,
            gender=gender,
            specialization=specialization,
            hospital_assigned=hospital_assigned,
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
    doctor_id = doctor_logged_in(request)
    doctor = get_object_or_404(Doctor, id=doctor_id)
        # Determine the greeting message based on the current hour
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
        
    patients = doctor.patients.all()
    activities = doctor.activities.order_by('-timestamp')[:3]  # Fetch the latest 3 activities
    return render(request, 'home.html', {'doctor': doctor, 'patients': patients, 'activities': activities, 'greeting':greeting})

def add_patient_view(request):
    doctor_id = doctor_logged_in(request)
    if request.method == 'POST':
        # Add patient
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        middle_name = request.POST['middle_name']
        age = request.POST['age']
        sex = request.POST['sex']
        phone_number = request.POST['phone_number']
        medical_history = request.POST['medical_history']
        doctor = Doctor.objects.get(id=doctor_id)
        
        # Create patient and log activity
        patient = Patient.objects.create(
            doctor=doctor,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            age=age,
            sex=sex,
            phone_number=phone_number,
            medical_history=medical_history,
        )
        Activity.objects.create(
            doctor=doctor,
            description=f"Added a new patient: {patient.first_name} {patient.last_name}",
        )
        return redirect('home')
    return render(request, 'add_patient.html')

def doctor_logout_view(request):
    if 'doctor_id' in request.session:
        del request.session['doctor_id']
        messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

def appointments_view(request):
    doctor_id = doctor_logged_in(request)  # Ensure doctor is logged in
    doctor = get_object_or_404(Doctor, id=doctor_id)
    appointments = doctor.appointments.all()
    return render(request, 'appointments.html', {'doctor': doctor, 'appointments': appointments})

def patient_list_view(request):
    doctor_id = doctor_logged_in(request)  # Ensure doctor is logged in
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    sex_filter = request.GET.get('sex', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Base query
    patients = doctor.patients.all()

    # Apply search filter
    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    # Apply sex filter
    if sex_filter:
        patients = patients.filter(sex=sex_filter)

    # Apply date range filter
    if start_date and end_date:
        patients = patients.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

    return render(request, 'patient_list.html', {'doctor': doctor, 'patients': patients})

def activities_view(request):
    doctor_id = doctor_logged_in(request)
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Base query
    activities = doctor.activities.all()

    # Apply search filter
    if search_query:
        activities = activities.filter(description__icontains=search_query)

    # Apply date range filter
    if start_date and end_date:
        activities = activities.filter(
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        )

    activities = activities.order_by('-timestamp')  # Sort activities by latest first
    return render(request, 'activities.html', {'activities': activities})

def edit_doctor_profile_view(request):
    doctor_id = doctor_logged_in(request)
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        form = DoctorProfileEditForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            Activity.objects.create(
                doctor=doctor,
                description="Updated profile information."
            )
            return redirect('doctor_profile')
    else:
        form = DoctorProfileEditForm(instance=doctor)
    return render(request, 'edit_doctor_profile.html', {'form': form, 'doctor': doctor})

def delete_patient_view(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        doctor = patient.doctor  # Assuming `Patient` has a ForeignKey to `Doctor`
        
        # Log the deletion in the Activity model
        Activity.objects.create(
            doctor=doctor,
            description=f"Deleted patient: {patient.first_name} {patient.last_name}."
        )
        
        patient.delete()  # Delete the patient record from the database
        return redirect('patients')
    
    return render(request, 'confirm_delete_patient.html', {'patient': patient})

def doctor_profile_view(request):
    doctor_id = doctor_logged_in(request)  # Ensure doctor is logged in
    doctor = get_object_or_404(Doctor, id=doctor_id)
    return render(request, 'doctor_profile.html', {'doctor': doctor})


def edit_patient_view(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        # Update patient details
        patient.first_name = request.POST.get('first_name', patient.first_name)
        patient.middle_name = request.POST.get('middle_name', patient.middle_name)
        patient.last_name = request.POST.get('last_name', patient.last_name)
        patient.age = request.POST.get('age', patient.age)
        patient.sex = request.POST.get('sex', patient.sex)
        patient.phone_number = request.POST.get('phone_number', patient.phone_number)
        patient.medical_history = request.POST.get('medical_history', patient.medical_history)
        patient.save()
        
        # Optionally log activity for this change
        Activity.objects.create(
            doctor=patient.doctor,
            description=f"Updated patient details for {patient.first_name} {patient.last_name}."
        )
        return redirect('patients')  # Redirect to patient list or other page
    
    return render(request, 'edit_patient.html', {'patient': patient})

