from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from datetime import datetime
import os

from .models import UploadedImage, RecoveryPlan
from .yolo import predict
from .forms import CustomUserCreationForm, CustomAuthenticationForm, RVCSSQuizForm
from .utils import get_default_plan_for_stage

from django.db.models import Count
from .models import UploadedImage

from django.contrib.auth.views import LogoutView

from django.core.files.base import ContentFile
import requests

import csv
from django.http import HttpResponse


@login_required
def export_user_reports_csv(request):
    # Create the HttpResponse object with CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_reports.csv"'

    writer = csv.writer(response)
    
    # Write CSV header row
    writer.writerow(['Upload Date', 'Stage', 'rVCSS Score', 'Recovery Plan', 'Plan Date'])

    user = request.user

    # Fetch user data
    uploads = UploadedImage.objects.filter(user=user).order_by('uploaded_at')
    plans = RecoveryPlan.objects.filter(user=user).order_by('created_at')

    # Create a map from stage to plan for easier lookup (optional)
    plan_map = {}
    for plan in plans:
        plan_map.setdefault(plan.stage, []).append(plan)

    # Combine data row-wise (assuming you want one row per UploadedImage)
    for upload in uploads:
        plans_for_stage = plan_map.get(upload.stage, [])
        # Join plan texts and dates for the stage, or leave empty
        plans_text = " | ".join([p.plan_text for p in plans_for_stage]) if plans_for_stage else ''
        plans_dates = " | ".join([p.created_at.strftime("%Y-%m-%d") for p in plans_for_stage]) if plans_for_stage else ''

        writer.writerow([
            upload.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
            upload.stage,
            upload.rvcss_score,
            plans_text,
            plans_dates,
        ])

    return response



@login_required
def save_prediction(request):
    if request.method == 'POST':
        stage = request.POST.get('stage')
        rvcss_score = int(request.POST.get('rvcss_score', 0))

        image_path = request.session.get('saved_image_path', '')
        if not image_path:
            messages.error(request, "No image found in session. Please upload again.")
            return redirect('upload_image')

        # ✅ Check if this exact image path + user + stage + score already saved
        existing = UploadedImage.objects.filter(
            user=request.user,
            stage=stage,
            rvcss_score=rvcss_score,
            image=image_path
        ).exists()

        if not existing:
            UploadedImage.objects.create(
                user=request.user,
                image=image_path,
                uploaded_at=datetime.now(),
                stage=stage,
                rvcss_score=rvcss_score
            )

        # ✅ Independently check if RecoveryPlan for this user + stage exists
        if stage and not RecoveryPlan.objects.filter(user=request.user, stage=stage).exists():
            RecoveryPlan.objects.create(
                user=request.user,
                plan_text=get_default_plan_for_stage(stage),
                stage=stage,
                created_at=datetime.now()
            )

        # ✅ Mark session result as saved
        request.session['result_saved'] = True
        messages.success(request, "Result and recovery plan saved successfully!")

        # ✅ Clean stale session data
        keys_to_clear = ['saved_image_path', 'result_image_path', 'labels', 'rvcss_score', 'status', 'stage']
        for key in keys_to_clear:
            request.session.pop(key, None)

        return redirect('dashboard')

    return redirect('home')



class LogoutView(LogoutView):
    # Allow GET requests for logout
    http_method_names = ['get', 'post']

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/signup.html', {'form': form})


from django.contrib.auth import get_user_model

def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST['username']
        password = request.POST['password']

        # support email login too
        user = authenticate(request, username=username_or_email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect after login
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You’ve been logged out.")
    return redirect('home')


def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        if not image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            messages.error(request, "Only .jpg, .jpeg, and .png files are allowed.")
            return redirect('upload_image')

        fs = FileSystemStorage()
        saved_path = fs.save(image.name, image)
        full_path = os.path.join(settings.MEDIA_ROOT, saved_path)

        try:
            result, result_image_path, status, labels = predict(full_path)
            if isinstance(labels, list) and len(labels) == 1 and isinstance(labels[0], list):
                labels = labels[0]  # flatten nested list
        except Exception as e:
            messages.error(request, f"Error processing image: {e}")
            return redirect('upload_image')

        # ✅ FIXED: Use labels from prediction, not session
        print("Predicted labels:", labels)

        status_label = "infected" if "infected" in labels else "normal"

        cvi_labels = [lbl for lbl in labels if lbl.startswith('cvi')]
        if cvi_labels:
            # Get highest stage (e.g., cvi4 > cvi3)
            stage_label = max(cvi_labels, key=lambda x: int(x.replace("cvi", "")))
        else:
            stage_label = ''

        # ✅ Store all info in session correctly
        request.session['saved_image_path'] = saved_path
        request.session['result_image_path'] = result_image_path
        request.session['status'] = status_label
        request.session['labels'] = labels
        request.session['stage'] = stage_label

        return redirect('quiz')

    return render(request, 'core/upload.html')

def quiz(request):
    if request.method == 'POST':
        form = RVCSSQuizForm(request.POST)
        if form.is_valid():
            score = 0
            for value in form.cleaned_data.values():
                try:
                    score += int(value)
                except (TypeError, ValueError):
                    score += 0  # fallback

            saved_path = request.session.get('saved_image_path')
            result_image_path = request.session.get('result_image_path')
            labels = request.session.get('labels', [])
            print("Labels in session:", labels)

            status_label = next((lbl for lbl in labels if lbl == 'infected'), 'normal')
            stage_label = next((lbl for lbl in labels if lbl.startswith('cvi')), '')

            if not saved_path or not result_image_path:
                messages.error(request, "Session expired or image missing. Please re-upload.")
                return redirect('upload_image')

            # Store info in session only, no DB save
            request.session['rvcss_score'] = score
            request.session['status'] = status_label
            request.session['stage'] = stage_label

            messages.success(request, f"rVCSS Quiz submitted successfully! Score: {score}")
            return redirect('result')

    else:
        form = RVCSSQuizForm()

    return render(request, 'core/quiz.html', {'form': form})


def result_view(request):
    saved_image = request.session.get('saved_image_path', None)
    result_image = request.session.get('result_image_path', None)
    labels = request.session.get('labels', [])
    rvcss_score = request.session.get('rvcss_score', None)
    status = request.session.get('status', '')
    stage = request.session.get('stage', '')

    request.session['result_saved'] = False
    
    return render(request, 'core/result.html', {
        'original_image': saved_image,
        'result_image': result_image,
        'stages': labels,
        'rvcss_score': rvcss_score,
        'status': status,
        'stage': stage,
        'result_saved':request.session.get('result_saved', False),
        'MEDIA_URL': settings.MEDIA_URL,
    })

@login_required
def my_recovery_plan(request):
    plans = RecoveryPlan.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/recov_plan.html', {'plans': plans})


def home(request):
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    images = UploadedImage.objects.filter(user=request.user).order_by('uploaded_at')

    dates = [img.uploaded_at.strftime("%Y-%m-%d") for img in images]
    scores = [img.rvcss_score for img in images]
    stages = [img.stage for img in images]

    return render(request, 'core/dashboard.html', {
        'dates': dates,
        'scores': scores,
        'stages': stages,
        'images': images,
    })


from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DailyCheckinForm
from .models import DailyCheckin, UserProfile
import random

QUOTES = [
    "One step at a time, you're healing. 💚",
    "Compression is key! Stay strong!",
    "Every photo brings you closer to recovery.",
    "Your health journey matters. Keep showing up!",
]

def daily_checkin(request):
    today = timezone.now().date()

    if request.method == 'POST':
        form = DailyCheckinForm(request.POST)
        if form.is_valid():
            checkin, created = DailyCheckin.objects.get_or_create(user=request.user, date=today)
            checkin.uploaded_photo = form.cleaned_data['uploaded_photo']
            checkin.wore_socks = form.cleaned_data['wore_socks']
            checkin.took_medication = form.cleaned_data['took_medication']
            checkin.save()

            # Handle streak logic
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            if profile.last_checkin == today - timezone.timedelta(days=1):
                profile.streak += 1
            else:
                profile.streak = 1
            profile.last_checkin = today

            # Assign badges
            badges = profile.badges or []
            if profile.streak == 3 and "3-day streak" not in badges:
                badges.append("3-day streak")
            elif profile.streak == 7 and "1-week warrior" not in badges:
                badges.append("1-week warrior")

            profile.badges = badges
            profile.save()

            messages.success(request, "Check-in completed! Keep going! 💪")
            return redirect('dashboard')
    else:
        form = DailyCheckinForm()

    # 💡 This line should go here, only once
    quote = random.choice(QUOTES)
    return render(request, 'core/daily_checkin.html', {'form': form, 'motivational_quote': quote})
