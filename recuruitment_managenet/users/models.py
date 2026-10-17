from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class JobSeeker(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    qualification = models.CharField(max_length=100)
    skills = models.TextField()
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    def __str__(self):
        return self.name

