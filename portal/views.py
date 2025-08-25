from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from django.shortcuts import get_object_or_404
from .models import Job, Application

def home(request):
    return render(request, "portal/layout/home.html")

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please login.")
            return redirect("login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, "portal/layout/register.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back {user.username}!")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "portal/layout/login.html", {"form": form})

@login_required
def dashboard(request):
    jobs = Job.objects.all()
    applied_jobs = Application.objects.filter(user=request.user).values_list('job_id', flat=True)

    if request.method == "POST":
        job_id = request.POST.get("job_id")
        job = get_object_or_404(Job, id=job_id)
        if job.id not in applied_jobs:
            Application.objects.create(user=request.user, job=job)
            applied_jobs = list(applied_jobs) + [job.id]
            messages.success(request, f"You applied to {job.title} at {job.company}.")
        else:
            messages.info(request, f"You already applied to {job.title}.")

    return render(request, "portal/layout/dashboard.html", {
        "jobs": jobs,
        "applied_jobs": applied_jobs
    })

def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")
