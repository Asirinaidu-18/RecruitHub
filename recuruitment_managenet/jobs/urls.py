from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('<int:id>/', views.job_detail, name='job_detail'),
    path('manage/', views.manage_jobs, name='manage_jobs'),
    path('all-applications/', views.all_applications, name='all_applications'),
     path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
     path('candidates/', views.candidates, name='candidates'),
    path('application/<int:id>/', views.application_detail, name='application_detail'),
    path('manage/add/', views.add_job, name='add_job'),
    path('manage/<int:id>/edit/', views.edit_job, name='edit_job'),
    path('manage/<int:id>/delete/', views.delete_job, name='delete_job'),
    path('<int:id>/apply/',views.apply_job_redirect,name='apply_job_redirect')
]