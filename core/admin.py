from django.contrib import admin
from .models import Master, QuizResult, Booking

@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'tags', 'experience')
    search_fields = ('name', 'tags')

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'hair_type', 'face_shape', 'created_at')
    list_filter = ('hair_type', 'face_shape')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'master', 'date_time', 'status')
    list_filter = ('status', 'date_time')


