from django.shortcuts import render,redirect
from jobs.models import Job
from applications.models import Application
# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import JobSeeker
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login,logout
def home(request):
    return HttpResponse("Welcome to Recruitment Management System")

from django.shortcuts import render


from django.shortcuts import render

def home(request):
    name = "Naidu"

    return render(
        request,
        'users/home.html',
        {'name': name}
    )
def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        phone = request.POST['phone']
        qualification = request.POST['qualification']
        skills = request.POST['skills']
        resume = request.FILES.get('resume')

        if User.objects.filter(username=email).exists():
            return render(
                request,
                'users/register.html',
                {'error': 'An account with this email already exists.'}
            )

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        JobSeeker.objects.create(
            user=user,
            name=name,
            email=email,
            phone=phone,
            qualification=qualification,
            skills=skills,
            resume=resume
        )

        return render(
            request,
            'users/register.html',
            {'success': 'Registration successful! You can now login.'}
        )

    return render(request, 'users/register.html')
def login_view(request):

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(
                request,
                'users/login.html',
                {'error': 'Invalid email or password'}
            )

    return render(request, 'users/login.html')
@login_required
def dashboard(request):
    job_seeker = JobSeeker.objects.get(user=request.user)

    # Calculate Profile Strength
    total_fields = 6

    completed_fields = sum([
        bool(job_seeker.name.strip()),
        bool(job_seeker.email.strip()),
        bool(job_seeker.phone.strip()),
        bool(job_seeker.qualification.strip()),
        bool(job_seeker.skills.strip()),
        bool(job_seeker.resume),
    ])

    profile_strength = round(
        (completed_fields / total_fields) * 100
    )

    # Dashboard statistics
    total_jobs = Job.objects.count()

    my_applications = Application.objects.filter(
        job_seeker=job_seeker
    )

    total_applications = my_applications.count()

    shortlisted_applications = my_applications.filter(
        status='Shortlisted'
    ).count()

    recent_applications = my_applications.select_related(
        'job'
    ).order_by('-applied_date')[:5]

    # Data sent to the HTML template
    context = {
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'shortlisted_applications': shortlisted_applications,
        'recent_applications': recent_applications,
        'profile_strength': profile_strength,
    }

    return render(
        request,
        'users/dashboard.html',
        context
    )
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):

    job_seeker = JobSeeker.objects.get(user=request.user)

    return render(
        request,
        'users/profile.html',
        {'job_seeker': job_seeker}
    )
@login_required
def edit_profile(request):

    job_seeker = JobSeeker.objects.get(user=request.user)

    if request.method == 'POST':

        job_seeker.name = request.POST['name']
        job_seeker.phone = request.POST['phone']
        job_seeker.qualification = request.POST['qualification']
        job_seeker.skills = request.POST['skills']
        if request.FILES.get('resume'):
         job_seeker.resume = request.FILES['resume']

        job_seeker.save()

        return redirect('profile')

    return render(
        request,
        'users/edit_profile.html',
        {'job_seeker': job_seeker}
    )