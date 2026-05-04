from django.core.management.base import BaseCommand
from masters.models import Master, Service


SERVICES_DATA = [
    {'name': 'Стрижка',         'icon': 'fas fa-cut',             'order': 1},
    {'name': 'Фарбування',      'icon': 'fas fa-palette',         'order': 2},
    {'name': 'Укладка',         'icon': 'fas fa-wind',            'order': 3},
    {'name': 'Борода',          'icon': 'fas fa-face-grin-beam',   'order': 4},
    {'name': 'Дитяча стрижка',  'icon': 'fas fa-child',           'order': 5},
    {'name': 'Брови',           'icon': 'fas fa-eye',             'order': 6},
]

# Правила автоматичного призначення послуг за професією майстра
PROFESSION_SERVICES = {
    'barber':   ['Стрижка', 'Борода', 'Дитяча стрижка'],
    'stylist':  ['Стрижка', 'Фарбування', 'Укладка', 'Брови', 'Дитяча стрижка'],
    'colorist': ['Фарбування', 'Укладка', 'Стрижка'],
}


class Command(BaseCommand):
    help = 'Створити послуги (Service) і автоматично призначити майстрам за їхньою професією.'

    def handle(self, *args, **options):
        # 1. Створити послуги
        for data in SERVICES_DATA:
            svc, created = Service.objects.get_or_create(
                name=data['name'],
                defaults={'icon': data['icon'], 'order': data['order']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  + Created service: {svc.name}'))
            else:
                self.stdout.write(f'  [v] Service already exists: {svc.name}')

        # 2. Призначити послуги майстрам за їхньою професією
        all_services = {s.name: s for s in Service.objects.all()}
        assigned_count = 0

        for master in Master.objects.all():
            service_names = PROFESSION_SERVICES.get(master.profession, ['Стрижка'])
            svcs_to_add = [all_services[n] for n in service_names if n in all_services]
            if svcs_to_add:
                master.services.add(*svcs_to_add)
                assigned_count += 1
                self.stdout.write(f'  -> {master.full_name} ({master.get_profession_display()}): '
                                  f'{", ".join(s.name for s in svcs_to_add)}')

        self.stdout.write(self.style.SUCCESS(
            f'\nГотово! Створено {len(SERVICES_DATA)} послуг, призначено {assigned_count} майстрам.'
        ))
