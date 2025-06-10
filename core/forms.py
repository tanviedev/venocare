from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']  # Add fields you want users to fill

class CustomAuthenticationForm(AuthenticationForm):
    pass

class RVCSSQuizForm(forms.Form):
    PAIN_CHOICES = [(0, 'N/A'), (1, 'Mild'), (2, 'Moderate'), (3, 'Severe')]
    pain = forms.ChoiceField(choices=PAIN_CHOICES, widget=forms.RadioSelect, label="Pain or discomfort", required=False)
    varicose = forms.ChoiceField(choices=PAIN_CHOICES, widget=forms.RadioSelect, label="Varicose veins", required=False)
    edema = forms.ChoiceField(choices=PAIN_CHOICES, widget=forms.RadioSelect, label="Venous edema", required=False)
    pigmentation = forms.ChoiceField(choices=PAIN_CHOICES, widget=forms.RadioSelect, label="Skin pigmentation", required=False)
    inflammation = forms.ChoiceField(choices=PAIN_CHOICES, widget=forms.RadioSelect, label="Inflammation", required=False)
    induration = forms.ChoiceField(choices=PAIN_CHOICES, widget=forms.RadioSelect, label="Induration", required=False)
    ulcer_number = forms.ChoiceField(choices=PAIN_CHOICES, widget=forms.RadioSelect, label="Active ulcer number", required=False)
    ulcer_duration = forms.ChoiceField(choices=PAIN_CHOICES, widget=forms.RadioSelect, label="Ulcer duration", required=False)
    ulcer_size = forms.ChoiceField(choices=PAIN_CHOICES, widget=forms.RadioSelect, label="Ulcer size", required=False)
    compression = forms.ChoiceField(choices=PAIN_CHOICES, widget=forms.RadioSelect, label="Compression therapy", required=False)

class DailyCheckinForm(forms.Form):
    uploaded_photo = forms.BooleanField(label="Uploaded today's leg photo?", required=False)
    wore_socks = forms.BooleanField(label="Wore compression socks today?", required=False)
    took_medication = forms.BooleanField(label="Took medication today?", required=False)
