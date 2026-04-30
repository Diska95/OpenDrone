from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('create/', views.create_order, name='create_order'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/status/', views.update_order_status, name='order_status'),
    path('<int:pk>/dispute/', views.open_dispute, name='open_dispute'),
]
