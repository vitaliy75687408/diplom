import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from styleai.views import generate_recommendations
from hairstyles.models import UserPhoto

def test_rec():
    # Test for Men
    photo_m = UserPhoto(predicted_gender='men')
    recs_m = generate_recommendations(photo_m)
    print(f"Men Recommendations: {[r.hairstyle.name for r in recs_m]}")

    # Test for Women
    photo_w = UserPhoto(predicted_gender='women')
    recs_w = generate_recommendations(photo_w)
    print(f"Women Recommendations: {[r.hairstyle.name for r in recs_w]}")

if __name__ == "__main__":
    test_rec()
