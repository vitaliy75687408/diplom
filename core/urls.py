from django.urls import path
from .views import HomeView, MasterListView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('masters/', MasterListView.as_view(), name='master_list'),
]

