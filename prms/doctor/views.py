from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Doctor, Patient
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse

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

        # Redirect to Step 2
        return redirect(reverse('registration_step2'))

    return render(request, 'registration_step1.html')

def registration_step2(request):
    # Retrieve and print session data
    print(f"Session Data - Username: {request.session.get('username')}, First Name: {request.session.get('first_name')}, Last Name: {request.session.get('last_name')}")

    if request.method == 'POST':
        # Retrieve step 1 data from the session
        first_name = request.session.get('first_name')
        middle_name = request.session.get('middle_name')
        last_name = request.session.get('last_name')
        birthday = request.session.get('birthday')
        gender = request.session.get('gender')
        email = request.session.get('email')
        username = request.session.get('username')
        password = make_password(request.session.get('password'))

        # Confirm that username is not None
        if not username:
            print("Error: Username is missing from the session.")
            return render(request, 'registration_step1.html', {"error": "Username is required."})

        # Retrieve step 2 form data
        specialization = request.POST.get('specialization')
        chart_number = request.POST.get('chart_number')
        health_care_number = request.POST.get('health_care_number')
        current_address = request.POST.get('current_address')
        social_security_number = request.POST.get('social_security_number')
        phone_number_home = request.POST.get('phone_number_home')
        phone_number_work = request.POST.get('phone_number_work')

        # Try creating the doctor instance
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
            # Fill in other required fields as per model
        )
        return redirect('registration_complete')
    
    return render(request, 'registration_step2.html')

def registration_complete(request):
    return render(request, 'registration_complete.html')

def doctor_login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the doctor exists in the database
        try:
            doctor = Doctor.objects.get(username=username)
            # Check password
            if check_password(password, doctor.password):
                request.session['doctor_id'] = doctor.id
                return redirect("home")  # Redirect to a home or dashboard page
            else:
                messages.error(request, "Invalid username or password")  # This line adds the message
        except Doctor.DoesNotExist:
            messages.error(request, "Doctor not found. Please register first.")

    return render(request, "login.html") # Ensure this matches your login template filename

def doctor_home_view(request):
    doctor_id = request.session.get('doctor_id')
    if doctor_id is None:
        return redirect('login')

    doctor = get_object_or_404(Doctor, id=doctor_id)
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