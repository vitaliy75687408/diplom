from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from hairstyles.models import Hairstyle


class Service(models.Model):
    """Тип послуги: Стрижка, Фарбування, Укладка, Борода, Дитяча стрижка, Брови тощо."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Назва")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Іконка (CSS клас)",
                            help_text="Наприклад: fas fa-cut")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Послуга"
        verbose_name_plural = "Послуги"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Master(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Ім'я")
    last_name = models.CharField(max_length=100, verbose_name="Прізвище")
    profession = models.CharField(
        max_length=50,
        choices=[
            ('barber', 'Барбер'),
            ('stylist', 'Стиліст'),
            ('colorist', 'Колорист'),
        ],
        verbose_name="Професія"
    )
    experience_years = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Роки досвіду"
    )
    city = models.CharField(max_length=100, verbose_name="Місто")
    district = models.CharField(max_length=100, blank=True, verbose_name="Район")
    address = models.CharField(max_length=255, blank=True, verbose_name="Адреса / Барбершоп")
    photo = models.ImageField(upload_to='masters/', verbose_name="Фото", blank=True, null=True)

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name="Рейтинг"
    )
    specialties = models.ManyToManyField(Hairstyle, related_name='masters', verbose_name="Спеціалізації")
    services = models.ManyToManyField('Service', related_name='masters_offering', blank=True, verbose_name="Послуги")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email")
    default_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name="Ціна за стрижку (грн)", validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    telegram_chat_id = models.BigIntegerField(null=True, blank=True, verbose_name="Telegram Chat ID")
    level = models.CharField(
        max_length=20,
        choices=[
            ('top', 'Топ-майстер'),
            ('average', 'Середній майстер'),
        ],
        default='average',
        verbose_name="Рівень майстра"
    )

    class Meta:
        verbose_name = "Майстер"
        verbose_name_plural = "Майстри"
        ordering = ['-rating', '-experience_years']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def location(self):
        parts = []
        if self.city:
            parts.append(self.city)
        if self.district:
            parts.append(self.district)
        if self.address:
            parts.append(self.address)
        return ", ".join(parts)



class Review(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='reviews', verbose_name="Майстер")
    author_name = models.CharField(max_length=100, verbose_name="Ім'я автора")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Рейтинг"
    )
    text = models.TextField(verbose_name="Текст відгуку")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        ordering = ['-created_at']

    def __str__(self):
        return f"Відгук від {self.author_name} для {self.master}"

class Barber(models.Model):
    """Барбер для сторінки process_look (зв'язок із зачісками з hairstyles)."""
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=200, blank=True)
    rating = models.FloatField(default=5.0)
    image = models.ImageField(upload_to='barbers/', blank=True, null=True)
    styles = models.ManyToManyField(Hairstyle, related_name='barbers', blank=True)

    def __str__(self):
        return self.name


class MasterPhoto(models.Model):
    """Фото майстра або його робіт (портфоліо). Прив'язка до майстра."""
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='gallery_photos', verbose_name="Майстер")
    image = models.ImageField(upload_to='masters/gallery/', verbose_name="Фото")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Підпис")
    is_work = models.BooleanField(default=True, verbose_name="Робота (портфоліо)")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Фото майстра"
        verbose_name_plural = "Фото майстрів (галерея)"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.master.full_name}: {self.caption or 'Фото'}"


class Booking(models.Model):
    """Запис до майстра: тип стрижки, дата, час, клієнт, ціна."""
    STATUS_CHOICES = [
        ('pending', 'Очікує підтвердження'),
        ('confirmed', 'Підтверджено'),
        ('cancelled', 'Скасовано'),
    ]
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='bookings', verbose_name="Майстер")
    service = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Послуга")
    hairstyle = models.ForeignKey(Hairstyle, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings', verbose_name="Тип стрижки")
    client_name = models.CharField(max_length=200, verbose_name="Ім'я клієнта")
    client_phone = models.CharField(max_length=20, verbose_name="Телефон")
    date = models.DateField(verbose_name="Дата")
    time_slot = models.CharField(max_length=5, verbose_name="Час")  # "10:00", "14:00"
    price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name="Ціна (грн)", validators=[MinValueValidator(0)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    client_chat_id = models.BigIntegerField(null=True, blank=True, verbose_name="Client Telegram Chat ID")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Запис"
        verbose_name_plural = "Записи"
        ordering = ['date', 'time_slot']

    def __str__(self):
        return f"{self.client_name} → {self.master} ({self.date} {self.time_slot})"


class Barbershop(models.Model):
    """Барбершоп-партнер для секції «Наші партнери» на головній."""
    name = models.CharField(max_length=200, verbose_name="Назва")
    logo = models.ImageField(upload_to='barbershops/', verbose_name="Логотип", blank=True, null=True)
    address = models.CharField(max_length=300, blank=True, verbose_name="Адреса")
    city = models.CharField(max_length=100, blank=True, verbose_name="Місто")
    website = models.URLField(blank=True, verbose_name="Сайт")
    description = models.TextField(blank=True, verbose_name="Опис")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Барбершоп-партнер"
        verbose_name_plural = "Барбершопи-партнери"
        ordering = ['name']

    def __str__(self):
        return self.name