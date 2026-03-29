from django.urls import path
from .views import index
from django.urls import path
from .views import index, feedback_page   # 🔥 yaha hona chahiye

urlpatterns = [
    path('', index, name='home'),
    path('feedback/', feedback_page),
]