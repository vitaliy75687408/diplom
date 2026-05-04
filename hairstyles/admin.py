from django.contrib import admin
from .models import Hairstyle, FaceShape


@admin.register(Hairstyle)
class HairstyleAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'master_count', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'name_en': ('name',)}


@admin.register(FaceShape)
class FaceShapeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    filter_horizontal = ['suitable_hairstyles']
