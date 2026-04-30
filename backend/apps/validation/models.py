from django.db import models


class ValidationReport(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'In attesa'
        PASSED = 'passed', 'Superata'
        FAILED = 'failed', 'Fallita'
        WARNING = 'warning', 'Con avvisi'

    project = models.ForeignKey('marketplace.DroneProject', on_delete=models.CASCADE, related_name='validations')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    is_printable = models.BooleanField(default=False)
    min_wall_thickness_mm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    has_open_surfaces = models.BooleanField(default=False)
    has_non_manifold = models.BooleanField(default=False)
    overhang_angle_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    estimated_print_time_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    estimated_filament_grams = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    issues = models.JSONField(default=list)
    warnings = models.JSONField(default=list)
    raw_report = models.JSONField(default=dict)
    validated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-validated_at']
