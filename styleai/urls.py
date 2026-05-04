from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('opytuvannya/', views.survey_page, name='survey'),
    path('hairstyle-selection/', views.hairstyle_selection, name='hairstyle_selection'),
    path('generate-hairstyle/', views.generate_hairstyle, name='generate_hairstyle'),
    path('api/upload-photo/', views.upload_photo_api, name='upload_photo_api'),
    path('api/set-city/', views.set_city, name='set_city'),
    path('temp-restore-shaggy/', views.temp_restore_shaggy),
    # Завантаження кастомних фото зачісок
    path('upload-hairstyle-image/', views.upload_hairstyle_image, name='upload_hairstyle_image'),
    path('upload-hairstyle-image/status/', views.upload_hairstyle_status, name='upload_hairstyle_status'),
]

