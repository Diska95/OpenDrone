from django.urls import path
from . import views

urlpatterns = [
    path('stl/', views.upload_and_validate_stl, name='validate_stl'),
    path('<int:project_id>/result/', views.validation_result, name='validation_result'),
]
