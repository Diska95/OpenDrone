from django.urls import path
from . import views

urlpatterns = [
    path('print/', views.PrintNodeListView.as_view(), name='print_node_list'),
    path('print/<int:pk>/', views.PrintNodeDetailView.as_view(), name='print_node_detail'),
    path('assembly/', views.AssemblyCenterListView.as_view(), name='assembly_list'),
    path('assembly/<int:pk>/', views.AssemblyCenterDetailView.as_view(), name='assembly_detail'),
]
