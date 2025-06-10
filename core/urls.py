from django.urls import path
from . import views
from .views import login_view
from .views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_image, name='upload_image'),
    path('quiz/', views.quiz, name='quiz'),
    path('result/', views.result_view, name='result'),
    path('my-recovery-plan/', views.my_recovery_plan, name='my_recovery_plan'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('save_prediction/', views.save_prediction, name='save_prediction'),
    path('export-reports/', views.export_user_reports_csv, name='export_user_reports_csv'),
    path('checkin/', views.daily_checkin, name='daily_checkin'),
]

