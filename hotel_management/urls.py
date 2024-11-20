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
from django.shortcuts import render, redirect
from core.forms import BookingForm
from core.views import payment_list, payment_create, payment_edit, payment_delete

def home_view(request):
    return HttpResponse("Welcome to the Hotel Management System!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('check-availability/<int:room_id>/', views.check_room_availability, name='check_availability'),
    path('room/<int:room_id>/calendar/', views.room_calendar_view, name='room_calendar'),
    path('', views.dashboard, name='dashboard'),
    #code for user site below
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/new/', views.room_create, name='create_room'),
    path('rooms/<int:room_id>/edit/', views.room_edit, name='room_edit'),
    path('rooms/<int:room_id>/delete/', views.room_delete, name='room_delete'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/new/', views.new_booking, name='new_booking'),    
    path('bookings/<int:booking_id>/edit/', views.booking_edit, name='booking_edit'),
    path('bookings/<int:booking_id>/delete/', views.booking_delete, name='booking_delete'),
    path('payments/', payment_list, name='payment_list'),
    path('payments/new/', payment_create, name='payment_create'),
    path('payments/<int:payment_id>/edit/', payment_edit, name='payment_edit'),
    path('payments/<int:payment_id>/delete/', payment_delete, name='payment_delete'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/<int:customer_id>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:customer_id>/delete/', views.customer_delete, name='customer_delete'),
    path('reviews/', views.review_list, name='review_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
from core.views import booking_view

urlpatterns += [
    path('book-room/', booking_view, name='book_room'),
]

