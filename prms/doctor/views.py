from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Doctor, Patient, Appointment, Activity, Document
from .forms import DoctorProfileEditForm
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.db.models import Q
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import random
import string

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

        # Retrieve email and username for validation
        email = request.session['email']
        username = request.session['username']

        # Check for existing email or username
        errors = {}
        if Doctor.objects.filter(email=email).exists():
            errors['email_error'] = "Email is already used."
        if Doctor.objects.filter(username=username).exists():
            errors['username_error'] = "Username is already taken."

        if errors:
            return render(request, 'registration_step1.html', {'errors': errors, 'form_data': request.POST})
        
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

    # Fetch patients and activities
    patients = doctor.patients.all()
    activities = doctor.activities.order_by('-timestamp')[:3]  # Fetch the latest 3 activities

    # Filter appointments
    today_start = now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    today_appointments = Appointment.objects.filter(
        patient__doctor=doctor,
        appointment_date__gte=today_start,
        appointment_date__lt=today_end
    ).order_by('appointment_date')[:3]

    upcoming_appointments = Appointment.objects.filter(
        patient__doctor=doctor,
        appointment_date__gte=today_end
    ).order_by('appointment_date')[:3]

    return render(
        request,
        'home.html',
        {
            'doctor': doctor,
            'patients': patients,
            'activities': activities,
            'greeting': greeting,
            'today_appointments': today_appointments,
            'upcoming_appointments': upcoming_appointments,
        }
    )

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

@login_required
def appointments_view(request):
    doctor = get_object_or_404(Doctor, user=request.user)  # Assuming logged-in user is a doctor
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient')  # Fetch appointments for this doctor

    # Extract appointment dates and corresponding patients
    appointment_data = [
        {
            'date': appointment.appointment_date,
            'patient': appointment.patient,
            'patient_name': f"{appointment.patient.first_name} {appointment.patient.last_name}"
        }
        for appointment in appointments
    ]
    
    return render(request, 'appointments.html', {
        'appointments': appointment_data,
    })

def patient_list_view(request):
    doctor_id = doctor_logged_in(request)  # Ensure doctor is logged in
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    sex_filter = request.GET.get('sex', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    sort_order = request.GET.get('sort_order', 'asc')  # Get sort order, default to ascending

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
        
        # Apply sort order
    if sort_order == 'desc':
        patients = patients.order_by('-created_at')
    else:
        patients = patients.order_by('created_at')

    return render(request, 'patient_list.html', {'doctor': doctor, 'patients': patients, 'sort_order': sort_order})

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

def delete_all_activities_view(request):
    doctor_id = doctor_logged_in(request)
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == "POST":
        # Delete all activities for the logged-in doctor
        doctor.activities.all().delete()
        return redirect('activities')

    return JsonResponse({"error": "Invalid request method."}, status=400)


def delete_all_patients_view(request):
    doctor_id = doctor_logged_in(request)  # Ensure doctor is logged in
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        # Delete all patients for the logged-in doctor
        doctor.patients.all().delete()  # This deletes all associated patients
        # Log the deletion activity
        Activity.objects.create(
            doctor=doctor,
            description="Deleted all patients."
        )
        return redirect('patients')  # Redirect to the patient list page

    return JsonResponse({"error": "Invalid request method."}, status=400)


def edit_doctor_profile_view(request):
    doctor_id = doctor_logged_in(request)
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        form = DoctorProfileEditForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            doctor = form.save()
            # Save profile picture
            if 'profile_picture' in request.FILES:
                doctor.profile_picture = request.FILES['profile_picture']
                doctor.save()

            # Save documents
            for file in request.FILES.getlist('documents'):
                Document.objects.create(doctor=doctor, file=file)

            Activity.objects.create(
                doctor=doctor,
                description="Updated profile information and uploaded documents."
            )
            return redirect('edit_doctor_profile')
    else:
        form = DoctorProfileEditForm(instance=doctor)
    return render(request, 'edit_doctor_profile.html', {'form': form, 'doctor': doctor})



def delete_appointment(request, appointment_id):
    if request.method == "POST":
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.delete()
            return JsonResponse({'status': 'success'}, status=200)
        except Appointment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Appointment not found.'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)

def delete_document(request, document_id):
    if request.method == 'POST':
        document = get_object_or_404(Document, id=document_id)
        document.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


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


def appointments_view(request):
    doctor_id = doctor_logged_in(request)  # Get logged-in doctor's ID
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # Fetch all appointments for the doctor
    appointments = Appointment.objects.filter(patient__doctor=doctor).select_related('patient')

    # Prepare appointments data for rendering
    appointment_data = [
        {
            'date': appointment.appointment_date.strftime('%Y-%m-%d %H:%M'),
            'type': appointment.appointment_type,
            'location': appointment.location,
            'details': appointment.details,
            'patient_name': f"{appointment.patient.first_name} {appointment.patient.last_name}"
        }
        for appointment in appointments
    ]

    return render(request, 'appointments.html', {'appointments': appointment_data})

def edit_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        # Update appointment details
        appointment.appointment_date = request.POST.get('appointment_date', appointment.appointment_date)
        appointment.appointment_type = request.POST.get('appointment_type', appointment.appointment_type)
        appointment.location = request.POST.get('location', appointment.location)
        appointment.details = request.POST.get('details', appointment.details)
        appointment.save()

        # Optionally log activity for this change
        Activity.objects.create(
            doctor=appointment.doctor,
            description=f"Updated appointment details for {appointment.patient} on {appointment.appointment_date}."
        )

        return redirect('appointments')  # Redirect to the appointments list or another page

    return render(request, 'edit_appointment.html', {'appointment': appointment})

def create_appointment_view(request, patient_id):
    # Get the logged-in doctor
    doctor_id = doctor_logged_in(request)  # Assuming you have a method to get the logged-in doctor
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # Get the patient assigned to this doctor
    patient = get_object_or_404(Patient, id=patient_id, doctor=doctor)

    if request.method == 'POST':
        # Extract form data
        appointment_date = request.POST.get('appointment_date')
        appointment_type = request.POST.get('appointment_type')
        location = request.POST.get('location')
        details = request.POST.get('details')

        # Validation
        if not appointment_date or not appointment_type or not location:
            messages.error(request, "All fields are required.")
        else:
            try:
                appointment_date = datetime.strptime(appointment_date, '%Y-%m-%dT%H:%M')
            except ValueError:
                messages.error(request, "Invalid date and time format.")
                return render(request, 'create_appointment.html', {'patient': patient, 'doctor': doctor})

            # Create appointment
            Appointment.objects.create(
                patient=patient,
                appointment_date=appointment_date,
                appointment_type=appointment_type,
                location=location,
                details=details,
            )

            # Log activity
            Activity.objects.create(
                doctor=doctor,
                description=f"Scheduled an appointment for {patient.first_name} {patient.last_name} on {appointment_date}."
            )
            return redirect('appointments')  # Redirect to appointments view

    return render(request, 'create_appointment.html', {'patient': patient, 'doctor': doctor})

def appointment_details(request):
    return render(request, 'appointment_details.html')


def forgot_username_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            doctor = Doctor.objects.get(email=email)
            # Send an email with the username
            send_mail(
                subject="Your Username",
                message=f"Dear {doctor.first_name},\n\nYour username is: {doctor.username}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            messages.success(request, "An email with your username has been sent.")
        except Doctor.DoesNotExist:
            messages.error(request, "Email not found.")
    return render(request, 'forgot_username.html')


def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            doctor = Doctor.objects.get(email=email)
            # Generate a temporary password
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            doctor.password = make_password(temp_password)
            doctor.save()
            # Send an email with the temporary password
            send_mail(
                subject="Password Reset",
                message=f"Dear {doctor.first_name},\n\nYour temporary password is: {temp_password}\nPlease log in and change your password immediately.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            messages.success(request, "A temporary password has been sent to your email.")
        except Doctor.DoesNotExist:
            messages.error(request, "Email not found.")
    return render(request, 'forgot_password.html')