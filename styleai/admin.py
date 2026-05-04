from django.contrib import admin
from .models import UserPhoto, AIRecommendation, HairSurvey


@admin.register(HairSurvey)
class HairSurveyAdmin(admin.ModelAdmin):
    list_display = ['id', 'hair_type', 'lifestyle', 'covers_ears', 'long_hairstyle', 'short_hairstyle', 'created_at']
    list_filter = ['hair_type', 'lifestyle', 'created_at']


@admin.register(UserPhoto)
class UserPhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'face_shape', 'analyzed_at']
    list_filter = ['analyzed_at', 'face_shape']
    readonly_fields = ['analyzed_at']


@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ['hairstyle', 'user_photo', 'confidence_score', 'created_at']
    list_filter = ['created_at', 'confidence_score']
    search_fields = ['hairstyle__name']
