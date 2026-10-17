from django.db import models

# Create your models here

class Job(models.Model):
    title = models.CharField(max_length=150)
    company = models.CharField(max_length=150)
    location = models.CharField(max_length=100)
    description = models.TextField()
    salary = models.CharField(max_length=50)
    skills = models.TextField()