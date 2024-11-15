from django.shortcuts import render

def specific_page(request):
    return render(request, 'login.html')