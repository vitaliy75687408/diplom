from django.urls import path
from . import views

urlpatterns = [
    path('', views.find_master, name='find_master'),
    path('booking/', views.booking_page, name='booking'),
    path('booking/api/styles/', views.booking_api_styles, name='booking_api_styles'),
    path('booking/api/masters/', views.booking_api_masters, name='booking_api_masters'),
    path('booking/api/slots/', views.booking_api_slots, name='booking_api_slots'),
    path('booking/api/dates/', views.booking_api_dates, name='booking_api_dates'),
    path('booking/create/', views.booking_create, name='booking_create'),
    path('analyze/', views.analyze_and_find_barber, name='analyze_barber'),
    path('<int:master_id>/', views.master_detail, name='master_detail'),
]
