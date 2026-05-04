from django.db import models
from django.contrib.auth.models import User

class Master(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='masters/')
    rating = models.FloatField(default=5.0)
    specialty = models.CharField(max_length=100, blank=True, help_text="e.g. Барбер-стиліст, Стиліст-колорист")
    experience = models.CharField(max_length=100, help_text="e.g. 8 років досвіду")
    clients_count = models.PositiveIntegerField(default=0, help_text="Кількість клієнтів")
    tags = models.CharField(max_length=200, help_text="Comma-separated tags e.g. Fade, Colorist")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def __str__(self):
        return self.name

class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    hair_type = models.CharField(max_length=50)
    face_shape = models.CharField(max_length=50)
    lifestyle = models.CharField(max_length=50, blank=True)
    priority = models.CharField(max_length=50, blank=True, help_text="What is most important: Practicality, Style, etc.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result {self.id} for {self.user or 'Guest'}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, default='pending', choices=[('pending', 'Pending'), ('confirmed', 'Confirmed')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking: {self.user} -> {self.master}"
