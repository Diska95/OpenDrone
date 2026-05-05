from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('my/', views.MyProjectsView.as_view(), name='my_projects'),
    path('admin/pending/', views.AdminPendingProjectsView.as_view(), name='admin_pending_projects'),
    path('admin/all/', views.AdminAllProjectsView.as_view(), name='admin_all_projects'),
    path('admin/archived/', views.AdminArchivedProjectsView.as_view(), name='admin_archived_projects'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('brands/', views.BrandListView.as_view(), name='brand_list'),
    path('<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<slug:slug>/publish/', views.publish_project, name='publish_project'),
    path('<slug:slug>/approve/', views.approve_project, name='approve_project'),
    path('<slug:slug>/reject/', views.reject_project, name='reject_project'),
    path('<slug:slug>/archive/', views.archive_project, name='archive_project'),
    path('<slug:slug>/unarchive/', views.unarchive_project, name='unarchive_project'),
    path('<slug:slug>/fork/', views.fork_project, name='fork_project'),
    path('<slug:slug>/files/', views.ProjectFilesView.as_view(), name='project_files'),
    path('<slug:slug>/bom/', views.BOMView.as_view(), name='project_bom'),
    path('<slug:slug>/bom/<int:pk>/', views.BOMItemDetailView.as_view(), name='bom_item_detail'),
    path('<slug:slug>/reviews/', views.ProjectReviewsView.as_view(), name='project_reviews'),
]
