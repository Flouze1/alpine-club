from django.db import models

# Create your models here.
class mountains(models.Model):
    name=models.CharField(max_length=150)
    height=models.FloatField()
    country=models.CharField(max_length=100)
    difficulty=models.CharField(max_length=10)
