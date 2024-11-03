from django.urls import path
from . import views

urlpatterns = [
    path('register/step1/', views.registration_step1, name='registration_step1'),
    path('register/step2/', views.registration_step2, name='registration_step2'),
    path('register/complete/', views.registration_complete, name='registration_complete'),
    path('login/', views.doctor_login_view, name='login'),
    path('home/', views.doctor_home_view, name='home'),
    path('add-patient/', views.add_patient_view, name='add_patient'),
    path('logout/', views.doctor_logout_view, name='logout'),
    path('appointments/', views.appointments_view, name='appointments'),
    path('patients/', views.patient_list_view, name='patients'),
    path('activities/', views.activities_view, name='activities'),
]
