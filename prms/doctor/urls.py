from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('login/', views.doctor_login_view, name='login'),
    path('register/step1/', views.registration_step1, name='registration_step1'),
    path('register/step2/', views.registration_step2, name='registration_step2'),
    path('register/complete/', views.registration_complete, name='registration_complete'),
    path('home/', views.doctor_home_view, name='home'),
    path('add-patient/', views.add_patient_view, name='add_patient'),
    path('logout/', views.doctor_logout_view, name='logout'),
    path('appointments/', views.appointments_view, name='appointments'),
    path('patients/', views.patient_list_view, name='patients'),
    path('activities/', views.activities_view, name='activities'),
    path('patients/edit/<int:patient_id>/', views.edit_patient_view, name='edit_patient'),
    path('patients/delete/<int:patient_id>/', views.delete_patient_view, name='delete_patient'),
    path('profile/', views.doctor_profile_view, name='doctor_profile'),
    path('edit-profile/', views.edit_doctor_profile_view, name='edit_doctor_profile'),
    path('activities/delete-all/', views.delete_all_activities_view, name='delete_all_activities'),
    path('create-appointment/<int:patient_id>/', views.create_appointment_view, name='create_appointment'),
    path('delete_all_patients/', views.delete_all_patients_view, name='delete_all_patients'),
    path('appointment_details/', views.appointment_details, name='appointment_details'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
