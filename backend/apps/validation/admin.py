from django.contrib import admin
from .models import ValidationReport


@admin.register(ValidationReport)
class ValidationReportAdmin(admin.ModelAdmin):
    list_display = ['project', 'status', 'is_printable', 'estimated_filament_grams', 'validated_at']
    list_filter = ['status', 'is_printable']
