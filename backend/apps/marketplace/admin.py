from django.contrib import admin
from .models import DroneCategory, DroneProject, ProjectFile, BOMItem, ProjectReview, Brand


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_partner', 'is_active', 'categories', 'sort_order']
    list_filter = ['is_partner', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_partner', 'is_active', 'sort_order']


@admin.register(DroneCategory)
class DroneCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 0


class BOMItemInline(admin.TabularInline):
    model = BOMItem
    extra = 0


@admin.register(DroneProject)
class DroneProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'designer', 'category', 'status', 'license_type', 'rating', 'order_count']
    list_filter = ['status', 'license_type', 'difficulty', 'is_university_project', 'is_featured']
    search_fields = ['title', 'description', 'designer__email']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectFileInline, BOMItemInline]
    actions = ['approve_projects', 'reject_projects']

    def approve_projects(self, request, queryset):
        from django.utils import timezone
        queryset.update(status=DroneProject.Status.PUBLISHED, published_at=timezone.now())
    approve_projects.short_description = 'Approva e pubblica progetti selezionati'

    def reject_projects(self, request, queryset):
        queryset.update(status=DroneProject.Status.REJECTED)
    reject_projects.short_description = 'Rifiuta progetti selezionati'


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ['filename', 'project', 'file_type', 'is_public', 'created_at']
    list_filter = ['file_type', 'is_public']


@admin.register(BOMItem)
class BOMItemAdmin(admin.ModelAdmin):
    list_display = ['component_name', 'project', 'quantity', 'unit_price_eur', 'is_available']


@admin.register(ProjectReview)
class ProjectReviewAdmin(admin.ModelAdmin):
    list_display = ['project', 'reviewer', 'rating_documentation', 'rating_performance', 'created_at']
