from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_applications, name='my_applications'),
    path('<int:job_id>/apply/', views.apply_job, name='apply_job'),
]