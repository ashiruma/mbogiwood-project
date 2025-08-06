from django.contrib import admin
from django.urls import path, include  # Make sure 'include' is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This is the crucial line:
    # It tells the project to look at core/urls.py for any matching routes.
    path('', include('core.urls')),
]