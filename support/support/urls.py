from django.urls import path
from .views import exchange_rate_view

urlpatterns = [
    path('exchange-rate/', exchange_rate_view),
]
