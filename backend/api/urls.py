from django.urls import path
from .views import predict_view, health_view

urlpatterns = [
    path('predict/', predict_view, name='predict'),
    path('health/', health_view, name='health'),
]