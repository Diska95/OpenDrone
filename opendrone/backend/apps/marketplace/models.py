from django.db import models
from django.utils.text import slugify


class DroneCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categorie'

    def __str__(self):
        return self.name


class DroneProject(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Bozza'
        PENDING_VALIDATION = 'pending_validation', 'In validazione'
        PENDING_REVIEW = 'pending_review', 'In revisione'
        PUBLISHED = 'published', 'Pubblicato'
        SUSPENDED = 'suspended', 'Sospeso'
        REJECTED = 'rejected', 'Rifiutato'

    class LicenseType(models.TextChoices):
        OPEN_SOURCE = 'open_source', 'Open Source'
        OPEN_ROYALTY = 'open_royalty', 'Open con Royalty'
        COMMERCIAL = 'commercial', 'Commerciale'
        UNIVERSITY = 'university', 'Universitario'

    class DifficultyLevel(models.TextChoices):
        BASIC = 'basic', 'Base'
        INTERMEDIATE = 'intermediate', 'Intermedio'
        ADVANCED = 'advanced', 'Avanzato'

    designer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    category = models.ForeignKey(DroneCategory, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    license_type = models.CharField(max_length=20, choices=LicenseType.choices, default=LicenseType.OPEN_ROYALTY)
    royalty_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    difficulty = models.CharField(max_length=20, choices=DifficultyLevel.choices, default=DifficultyLevel.BASIC)
    estimated_weight_grams = models.IntegerField(default=0)
    estimated_flight_time_minutes = models.IntegerField(default=0)
    max_payload_grams = models.IntegerField(default=0)
    operating_range_km = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    use_cases = models.JSONField(default=list)
    estimated_print_cost_min = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estimated_print_cost_max = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estimated_print_time_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    estimated_total_cost_min = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estimated_total_cost_max = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    easa_category = models.CharField(max_length=50, blank=True)
    compliance_notes = models.TextField(blank=True)
    view_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    order_count = models.IntegerField(default=0)
    fork_count = models.IntegerField(default=0)
    flag_count = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    version = models.CharField(max_length=20, default='1.0.0')
    parent_project = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='forks')
    is_university_project = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while DroneProject.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProjectFile(models.Model):
    class FileType(models.TextChoices):
        STL = 'stl', 'File STL'
        BOM = 'bom', 'Bill of Materials'
        FIRMWARE_CONFIG = 'firmware', 'Configurazione Firmware'
        WIRING_DIAGRAM = 'wiring', 'Schema Cablaggio'
        ASSEMBLY_GUIDE = 'assembly', 'Guida Assemblaggio'
        IMAGE = 'image', 'Immagine'
        VIDEO_URL = 'video_url', 'Video URL'
        OTHER = 'other', 'Altro'

    project = models.ForeignKey(DroneProject, on_delete=models.CASCADE, related_name='files')
    file_type = models.CharField(max_length=20, choices=FileType.choices)
    file = models.FileField(upload_to='projects/', blank=True, null=True)
    external_url = models.URLField(blank=True)
    filename = models.CharField(max_length=255)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class BOMItem(models.Model):
    project = models.ForeignKey(DroneProject, on_delete=models.CASCADE, related_name='bom_items')
    component_name = models.CharField(max_length=200)
    manufacturer = models.CharField(max_length=100, blank=True)
    brand = models.ForeignKey('Brand', null=True, blank=True, on_delete=models.SET_NULL, related_name='bom_uses')
    model_number = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(default=1)
    unit_price_eur = models.DecimalField(max_digits=8, decimal_places=2)
    supplier_url = models.URLField(blank=True)
    is_available = models.BooleanField(default=True)
    notes = models.CharField(max_length=500, blank=True)
    category = models.CharField(max_length=50, default='other')

    def __str__(self):
        return f"{self.component_name} x{self.quantity}"


class Brand(models.Model):
    """Catalogo brand componenti drone, con supporto a partner commerciali."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    website = models.URLField(blank=True)
    default_supplier_url = models.URLField(
        blank=True,
        help_text='URL fornitore default (può contenere affiliate ID).'
    )
    categories = models.JSONField(
        default=list,
        help_text='Categorie BOM in cui questo brand è rilevante (motor, esc, fc, …).'
    )
    is_partner = models.BooleanField(default=False, help_text='Accordo commerciale attivo.')
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=100)

    class Meta:
        ordering = ['-is_partner', 'sort_order', 'name']

    def __str__(self):
        return f"{self.name}{' ★' if self.is_partner else ''}"


class ProjectReview(models.Model):
    project = models.ForeignKey(DroneProject, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='given_reviews')
    rating_documentation = models.IntegerField()
    rating_difficulty_accuracy = models.IntegerField()
    rating_performance = models.IntegerField()
    comment = models.TextField()
    build_photos = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['project', 'reviewer']
