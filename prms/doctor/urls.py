from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.doctor_register_view, name='registration'),
    path('login/', views.doctor_login_view, name='login'),
    path('home/', views.doctor_home_view, name='home'),
    path('add-patient/', views.add_patient_view, name='add_patient'),
    path('logout/', views.doctor_logout_view, name='logout'),
]
