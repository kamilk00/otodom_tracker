from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.property_list, name = 'property_list'),
    path('ogloszenie/<int:pk>/', views.property_detail, name = 'property_detail'),
    path('property/<int:pk>/delete/', views.property_delete, name = 'property_delete'),
]