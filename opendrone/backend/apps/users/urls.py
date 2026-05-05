from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('google/', views.google_auth_view, name='google_auth'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.MeView.as_view(), name='me'),
    path('me/password/', views.change_password_view, name='change_password'),
    path('profile/print-node/', views.PrintNodeProfileView.as_view(), name='print_node_profile'),
    path('profile/assembly/', views.AssemblyCenterProfileView.as_view(), name='assembly_profile'),
    path('profile/designer/', views.DesignerProfileView.as_view(), name='designer_profile'),
    path('admin/users/', views.AdminUsersListView.as_view(), name='admin_users_list'),
    path('admin/users/<int:pk>/', views.admin_update_user, name='admin_user_update'),
]
