
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LogoutView, LoginView
urlpatterns = [
    path('admin/', admin.site.urls),

    # Login URL using built-in LoginView
    path('login/', LoginView.as_view(), name='login'),

    # Logout URL (optional)
    path('logout/', LogoutView.as_view(), name='logout'),

    # Your app URLs here
    path('', include('core.urls')),  # Assuming 'core' is your app name
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

