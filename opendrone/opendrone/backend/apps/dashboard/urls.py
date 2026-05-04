from django.urls import path
from . import views

urlpatterns = [
    path('designer/', views.designer_dashboard, name='designer_dashboard'),
    path('print-node/', views.print_node_dashboard, name='print_node_dashboard'),
    path('assembly/', views.assembly_dashboard, name='assembly_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
]
