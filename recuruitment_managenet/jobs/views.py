
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.admin.views.decorators import staff_member_required
from users.models import JobSeeker
from applications.models import Application
from .models import Job
from datetime import date
from django.db.models import Q, Count
from django.utils.dateparse import parse_date

from applications.models import Application
from .models import Job

from django.db.models import Q
from django.shortcuts import render
from .models import Job


def job_list(request):
    # Get the job title, company, or location entered in the search bar.
    search_query = request.GET.get('q', '').strip()

    # Start with all available jobs.
    jobs = Job.objects.all().order_by('-id')

    # Show only jobs matching the search text.
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query)
            | Q(company__icontains=search_query)
            | Q(location__icontains=search_query)
        )

    return render(
        request,
        'jobs/job_list.html',
        {
            'jobs': jobs,
            'search_query': search_query,
        }
    )
def job_detail(request, id):
    """Display details of a selected job."""
    job = get_object_or_404(Job, id=id)

    return render(
        request,
        'jobs/job_detail.html',
        {'job': job}
    )


@staff_member_required
def manage_jobs(request):
    """Allow staff to view all jobs."""
    jobs = Job.objects.all().order_by('-id')

    return render(
        request,
        'jobs/manage_jobs.html',
        {'jobs': jobs}
    )
from django.contrib.admin.views.decorators import staff_member_required
from applications.models import Application


@staff_member_required
def all_applications(request):
    # Start with all applications and load related records efficiently.
    all_applications_qs = Application.objects.select_related(
        "job_seeker",
        "job",
    ).order_by("-id")

    # Read the search and filter values from the URL.
    search_query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "").strip()
    selected_job = request.GET.get("job", "").strip()
    selected_date = request.GET.get("date", "").strip()

    # Calculate pipeline counts from ALL applications,
    # independently of the current search and filters.
    status_counts = Application.objects.aggregate(
        pending_count=Count(
            "id",
            filter=Q(status="Applied"),
        ),
        shortlisted_count=Count(
            "id",
            filter=Q(status="Shortlisted"),
        ),
        rejected_count=Count(
            "id",
            filter=Q(status="Rejected"),
        ),
    )

    total_applications = Application.objects.count()

    # Apply the text search.
    if search_query:
        search_filter = (
            Q(job_seeker__name__icontains=search_query)
            | Q(job_seeker__email__icontains=search_query)
            | Q(job__title__icontains=search_query)
            | Q(job__company__icontains=search_query)
        )

        # Also allow searching by application ID:
        # searching for "APP-12" or "12" can find application 12.
        application_id = search_query.upper().removeprefix("APP-").strip()

        if application_id.isdigit():
            search_filter |= Q(id=int(application_id))

        all_applications_qs = all_applications_qs.filter(search_filter)

    # Filter by status.
    valid_statuses = {
        "Applied",
        "Shortlisted",
        "Interview",
        "Selected",
        "Rejected",
    }

    if selected_status in valid_statuses:
        all_applications_qs = all_applications_qs.filter(
            status=selected_status
        )

    # Filter by selected job.
    if selected_job.isdigit():
        all_applications_qs = all_applications_qs.filter(
            job_id=int(selected_job)
        )

    # Filter by application date.
    if selected_date:
        parsed_date = parse_date(selected_date)

        if parsed_date:
            all_applications_qs = all_applications_qs.filter(
                applied_date__date=parsed_date
            )

    context = {
        "applications": all_applications_qs,
        "search_query": search_query,
        "selected_status": selected_status,
        "selected_job": selected_job,
        "selected_date": selected_date,
        "filter_jobs": Job.objects.all().order_by("title"),
        "total_applications": total_applications,
        "pending_count": status_counts["pending_count"],
        "shortlisted_count": status_counts["shortlisted_count"],
        "rejected_count": status_counts["rejected_count"],
    }

    return render(
        request,
        "jobs/all_applications.html",
        context,
    )
from django.contrib.admin.views.decorators import staff_member_required
from applications.models import Application


@staff_member_required
def admin_dashboard(request):
    total_jobs = Job.objects.count()
    total_candidates = JobSeeker.objects.count()
    total_applications = Application.objects.count()

    context = {
        "total_jobs": total_jobs,
        "total_candidates": total_candidates,
        "total_applications": total_applications,
    }

    return render(request, "jobs/admin_dashboard.html", context)
from django.contrib.admin.views.decorators import staff_member_required
from users.models import JobSeeker
@staff_member_required
def candidates(request):
    candidates_list = JobSeeker.objects.all()

    return render(
        request,
        'jobs/candidates.html',
        {'candidates': candidates_list}
    )
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from applications.models import Application


@staff_member_required
def application_detail(request, id):
    application = get_object_or_404(Application, id=id)

    if request.method == "POST":
        status = request.POST.get("status")

        # Validate the submitted status
        valid_statuses = [
            choice[0]
            for choice in Application.STATUS_CHOICES
        ]

        if status in valid_statuses:
            application.status = status
            application.save(update_fields=["status"])

            messages.success(
                request,
                "Application status updated successfully."
            )
        else:
            messages.error(
                request,
                "Invalid application status selected."
            )

        return redirect("application_detail", id=application.id)

    return render(
        request,
        "jobs/application_detail.html",
        {"application": application,  "status_choices": Application.STATUS_CHOICES,}
    )
from django.shortcuts import redirect
from django.contrib import messages


@staff_member_required
def add_job(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        company = request.POST.get("company", "").strip()
        location = request.POST.get("location", "").strip()
        description = request.POST.get("description", "").strip()
        salary = request.POST.get("salary", "").strip()
        skills = request.POST.get("skills", "").strip()

        if not all([title, company, location, description, salary, skills]):
            messages.error(request, "Please fill in all fields.")
            return render(request, "jobs/add_job.html")

        Job.objects.create(
            title=title,
            company=company,
            location=location,
            description=description,
            salary=salary,
            skills=skills,
        )

        messages.success(request, "Job added successfully!")
        return redirect("manage_jobs")

    return render(request, "jobs/add_job.html")


@staff_member_required
def edit_job(request, id):
    job = get_object_or_404(Job, id=id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        company = request.POST.get("company", "").strip()
        location = request.POST.get("location", "").strip()
        description = request.POST.get("description", "").strip()
        salary = request.POST.get("salary", "").strip()
        skills = request.POST.get("skills", "").strip()

        if not all([title, company, location, description, salary, skills]):
            messages.error(request, "Please fill in all fields.")
            return render(request, "jobs/edit_job.html", {"job": job})

        job.title = title
        job.company = company
        job.location = location
        job.description = description
        job.salary = salary
        job.skills = skills
        job.save()

        messages.success(request, "Job updated successfully!")
        return redirect("manage_jobs")

    return render(request, "jobs/edit_job.html", {"job": job})

@staff_member_required
def delete_job(request, id):
    job = get_object_or_404(Job, id=id)

    if request.method == "POST":
        try:
            job_title = job.title
            job.delete()

            messages.success(
                request,
                f'"{job_title}" was deleted successfully.'
            )

            return redirect("manage_jobs")

        except Exception as e:
            messages.error(
                request,
                f"Unable to delete this job: {e}"
            )

            return redirect("manage_jobs")

    return render(
        request,
        "jobs/delete_job.html",
        {"job": job}
    )
def apply_job_redirect(request, id):
    return redirect('apply_job', job_id=id)

