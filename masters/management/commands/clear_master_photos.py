# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from masters.models import Master


class Command(BaseCommand):
    help = 'Видаляє фото у всіх майстрів (залишає майстрів без фото)'

    def handle(self, *args, **options):
        count = 0
        for master in Master.objects.all():
            if master.photo:
                try:
                    master.photo.delete(save=False)
                except Exception:
                    pass
                master.photo = None
                master.save()
                count += 1
                self.stdout.write(f'  Видалено фото: {master.full_name}')
        self.stdout.write(self.style.SUCCESS(f'Готово. Фото видалено у {count} майстрів.'))
