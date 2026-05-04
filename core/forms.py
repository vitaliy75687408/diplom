from django import forms

class QuizForm(forms.Form):
    # Reduced/Removed dependence on Service model for now or defined locally
    FACE_SHAPE_CHOICES = [
        ('oval', 'Овальне'),
        ('round', 'Кругле'),
        ('square', 'Квадратне'),
        ('heart', 'Серцеподібне'),
    ]
    HAIR_TYPE_CHOICES = [
        ('straight', 'Пряме'),
        ('wavy', 'Хвилясте'),
        ('curly', 'Кучеряве'),
    ]

    face_shape = forms.ChoiceField(choices=FACE_SHAPE_CHOICES)
    hair_type = forms.ChoiceField(choices=HAIR_TYPE_CHOICES)
