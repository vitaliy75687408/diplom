from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from hairstyles.models import Hairstyle, FaceShape


class UserPhoto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='photos')
    photo = models.ImageField(upload_to='user_photos/', verbose_name="Фото користувача")
    face_shape = models.ForeignKey(FaceShape, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Форма обличчя")
    survey = models.ForeignKey('HairSurvey', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_photos', verbose_name="Опитування")
    predicted_gender = models.CharField(max_length=10, null=True, blank=True, verbose_name="Стать (AI)")
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Фото користувача"
        verbose_name_plural = "Фото користувачів"
        ordering = ['-analyzed_at']

    def __str__(self):
        return f"Фото від {self.analyzed_at.strftime('%Y-%m-%d %H:%M')}"


class HairSurvey(models.Model):
    """Опитування: тип волосся, спосіб життя, побажання до зачіски"""
    HAIR_TYPE_CHOICES = [
        ('straight', 'Пряме'),
        ('wavy', 'Хвилясте'),
        ('curly', 'Кучеряве'),
        ('coily', 'Сильно кучеряве'),
        ('thin', 'Тонке'),
        ('thick', 'Густе'),
    ]
    LIFESTYLE_CHOICES = [
        ('active', 'Активний (спорт, рух)'),
        ('office', 'Офісний / діловий'),
        ('creative', 'Креативний / творчий'),
        ('minimal', 'Мінімальний догляд'),
        ('casual', 'Повсякденний'),
    ]
    hair_type = models.CharField(max_length=20, choices=HAIR_TYPE_CHOICES, verbose_name="Тип волосся", blank=True)
    lifestyle = models.CharField(max_length=20, choices=LIFESTYLE_CHOICES, verbose_name="Спосіб життя", blank=True)
    face_shape_extra = models.CharField(max_length=20, verbose_name="Форма обличчя (з опитування)", blank=True)
    hair_length_extra = models.CharField(max_length=20, verbose_name="Довжина волосся (з опитування)", blank=True)
    priority_extra = models.CharField(max_length=20, verbose_name="Пріоритет (з опитування)", blank=True)
    care_time_extra = models.CharField(max_length=20, verbose_name="Час на догляд (з опитування)", blank=True)
    covers_ears = models.BooleanField(default=False, verbose_name="Закривати вуха")
    long_hairstyle = models.BooleanField(default=False, verbose_name="Подовжена зачіска")
    short_hairstyle = models.BooleanField(default=False, verbose_name="Коротка стрижка")
    low_maintenance = models.BooleanField(default=False, verbose_name="Мінімум догляду")
    volume = models.BooleanField(default=False, verbose_name="Об'єм")
    notes = models.TextField(blank=True, verbose_name="Додаткові побажання")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Опитування зачіски"
        verbose_name_plural = "Опитування зачісок"
        ordering = ['-created_at']

    def __str__(self):
        return f"Опитування {self.created_at.strftime('%d.%m.%Y %H:%M')}"


class AIRecommendation(models.Model):
    user_photo = models.ForeignKey(UserPhoto, on_delete=models.CASCADE, related_name='recommendations')
    hairstyle = models.ForeignKey(Hairstyle, on_delete=models.CASCADE, related_name='recommendations')
    confidence_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Рівень впевненості"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Рекомендація AI"
        verbose_name_plural = "Рекомендації AI"
        ordering = ['-confidence_score']

    def __str__(self):
        return f"{self.hairstyle.name} ({self.confidence_score:.2%})"
