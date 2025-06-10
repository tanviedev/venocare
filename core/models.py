from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

# Don't override User here again — it's your custom model already!
class User(AbstractUser):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('caregiver', 'Caregiver'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

# Get reference to custom user model (after defining it)

class UploadedImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/')
    stage_labels = models.JSONField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    stage = models.CharField(max_length=50, blank=True)
    rvcss_score = models.IntegerField(null=True, blank=True)

class RecoveryPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    stage = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Plan for {self.user.username}-{self.stage}-{self.created_at}"
    
class DailyCheckin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    uploaded_photo = models.BooleanField(default=False)
    wore_socks = models.BooleanField(default=False)
    took_medication = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    streak = models.IntegerField(default=0)
    last_checkin = models.DateField(null=True, blank=True)
    badges = models.JSONField(default=list)  # ["3-day streak", "1-week warrior"]
