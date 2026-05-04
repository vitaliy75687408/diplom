import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from hairstyles.models import Hairstyle, FaceShape

def populate_relationships():
    # 1. Створюємо форми обличчя, якщо їх немає
    shapes_data = [
        "Овальна", "Кругла", "Квадратна", "Подовжена", "Серце"
    ]
    for s_name in shapes_data:
        FaceShape.objects.get_or_create(name=s_name)
    
    # 2. Мапінг: які зачіски підходять яким формам
    # Це базовий мапінг для демонстрації
    mapping = {
        "Овальна": ["Drop Fade", "Taper Fade", "Slick Back", "Quiff", "Pompadour", "Buzz Cut", "Bob", "Каре"],
        "Кругла": ["High Fade", "Pompadour", "Quiff", "Faux Hawk", "Textured Crop", "Pixie Cut", "Піксі"],
        "Квадратна": ["Low Fade", "Mid Fade", "Slick Back", "Crew Cut", "Buzz Cut", "Bob", "Гарсон"],
        "Подовжена": ["Taper Fade", "Side Part", "Slick Back", "Crew Cut", "Bob", "Сесон", "Каре"],
        "Серце": ["Textured Crop", "Faux Hawk", "Undercut", "Long Wavy Hair", "Шеггі", "Кучерявий Боб"]
    }
    
    for s_name, style_names in mapping.items():
        shape = FaceShape.objects.get(name=s_name)
        for h_name in style_names:
            try:
                style = Hairstyle.objects.get(name=h_name)
                shape.suitable_hairstyles.add(style)
                print(f"Linked {h_name} to {s_name}")
            except Hairstyle.DoesNotExist:
                print(f"Hairstyle {h_name} not found in DB")

if __name__ == "__main__":
    populate_relationships()
