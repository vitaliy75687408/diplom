from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Hairstyle(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва")
    name_en = models.CharField(max_length=100, blank=True, verbose_name="Назва (англійською)")
    description = models.TextField(verbose_name="Опис")
    category = models.CharField(
        max_length=20,
        choices=[
            ('men', 'Чоловіча'),
            ('women', 'Жіноча'),
            ('unisex', 'Унісекс'),
        ],
        default='unisex',
        verbose_name="Категорія"
    )
    image = models.ImageField(upload_to='hairstyles/', verbose_name="Зображення", blank=True, null=True)
    overlay_image = models.ImageField(upload_to='hairstyles/overlays/', verbose_name="Оверлей для примірки (PNG)", blank=True, null=True, help_text="PNG з прозорістю для накладання на фото користувача")
    master_count = models.IntegerField(default=0, verbose_name="Кількість майстрів")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Зачіска"
        verbose_name_plural = "Зачіски"
        ordering = ['-master_count']

    def __str__(self):
        return self.name


class FaceShape(models.Model):
    name = models.CharField(max_length=50, verbose_name="Назва форми обличчя")
    description = models.TextField(verbose_name="Опис")
    suitable_hairstyles = models.ManyToManyField(Hairstyle, related_name='suitable_for_shapes', verbose_name="Підходящі зачіски")

    class Meta:
        verbose_name = "Форма обличчя"
        verbose_name_plural = "Форми обличчя"

    def __str__(self):
        return self.name
