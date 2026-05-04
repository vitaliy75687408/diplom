from django.contrib import admin
from .models import Master, Review, Booking, MasterPhoto, Barbershop, Service


class MasterPhotoInline(admin.TabularInline):
    model = MasterPhoto
    extra = 0
    fields = ['image', 'caption', 'is_work', 'order']


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'profession', 'city', 'rating', 'experience_years', 'default_price', 'telegram_chat_id']
    list_filter = ['profession', 'city', 'rating']
    search_fields = ['first_name', 'last_name', 'city', 'district']
    filter_horizontal = ['specialties', 'services']
    inlines = [MasterPhotoInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'master', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['author_name', 'text']


@admin.register(MasterPhoto)
class MasterPhotoAdmin(admin.ModelAdmin):
    list_display = ['master', 'caption', 'is_work', 'order', 'created_at']
    list_filter = ['is_work', 'master']
    search_fields = ['caption', 'master__first_name', 'master__last_name']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'client_phone', 'client_chat_id', 'master', 'hairstyle', 'date', 'time_slot', 'price', 'status', 'created_at']
    list_filter = ['status', 'date', 'master']
    search_fields = ['client_name', 'client_phone']
    date_hierarchy = 'date'


@admin.register(Barbershop)
class BarbershopAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'address', 'website']
    list_filter = ['city']
    search_fields = ['name', 'city', 'address']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'order']
    list_editable = ['order']
    search_fields = ['name']
