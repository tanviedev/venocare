from django.contrib import admin
from .models import User, UploadedImage, RecoveryPlan

admin.site.register(User)
admin.site.register(UploadedImage)
admin.site.register(RecoveryPlan)

