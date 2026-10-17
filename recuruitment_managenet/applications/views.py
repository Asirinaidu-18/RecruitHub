from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from users.models import JobSeeker
from jobs.models import Job
from .models import Application


@login_required
def my_applications(request):
    job_seeker = get_object_or_404(
        JobSeeker,
        user=request.user
    )

    applications = Application.objects.filter(
        job_seeker=job_seeker
    ).select_related('job').order_by('-applied_date')

    context = {
        'applications': applications,
        'total_applications': applications.count(),
        'shortlisted_applications': applications.filter(
            status='Shortlisted'
        ).count(),
        'interview_applications': applications.filter(
            status='Interview'
        ).count(),
        'selected_applications': applications.filter(
            status='Selected'
        ).count(),
    }

    return render(
        request,
        'applications/my_applications.html',
        context
    )


@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    job_seeker = get_object_or_404(
        JobSeeker,
        user=request.user
    )

    if request.method == "POST":
        application, created = Application.objects.get_or_create(
            job_seeker=job_seeker,
            job=job,
            defaults={'status': 'Applied'}
        )

        if created:
            messages.success(
                request,
                "Your application was submitted successfully!"
            )
        else:
            messages.info(
                request,
                "You have already applied for this job."
            )

        return redirect('my_applications')

    return render(
        request,
        'applications/apply_job.html',
        {'job': job}
    )