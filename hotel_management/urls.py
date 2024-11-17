"""
URL configuration for hotel_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from core import views
from django.urls import path
from django.http import HttpResponse

def home_view(request):
    return HttpResponse("Welcome to the Hotel Management System!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('check-availability/<int:room_id>/', views.check_room_availability, name='check_availability'),
    path('room/<int:room_id>/calendar/', views.room_calendar_view, name='room_calendar'),
    path('', admin.site.urls),  # Add this line
]
