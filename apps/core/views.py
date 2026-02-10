# apps/core/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def home(request):
    return render(request, "base/index.html")

@login_required
def login_view(request):
    return render(request, "registration/login.html")



