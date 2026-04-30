from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email obbligatoria')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('roles', ['admin'])
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    # ['designer', 'print_node', 'assembly_center', 'customer', 'admin']
    roles = models.JSONField(default=list)
    stripe_account_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_role(self, role):
        return role in (self.roles or [])


class DesignerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='designer_profile')
    portfolio_url = models.URLField(blank=True)
    university = models.CharField(max_length=200, blank=True)
    is_university_project = models.BooleanField(default=False)
    is_certified = models.BooleanField(default=False)
    total_royalties_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)

    def __str__(self):
        return f"Designer: {self.user.email}"


class PrintNodeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='print_node_profile')
    business_name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=2)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    materials = models.JSONField(default=list)
    max_print_volume_mm = models.JSONField(default=dict)
    hourly_capacity = models.IntegerField(default=8)
    price_per_gram = models.DecimalField(max_digits=6, decimal_places=3, default=0.05)
    sla_hours = models.IntegerField(default=72)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_by_material = models.JSONField(default=dict)
    is_certified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    current_load = models.IntegerField(default=0)
    total_orders_completed = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Nodo stampa: {self.business_name}"


class AssemblyCenterProfile(models.Model):
    class ComplexityLevel(models.TextChoices):
        BASIC = 'basic', 'Base'
        INTERMEDIATE = 'intermediate', 'Intermedio'
        ADVANCED = 'advanced', 'Avanzato'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='assembly_profile')
    business_name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=2)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    max_complexity = models.CharField(max_length=20, choices=ComplexityLevel.choices, default=ComplexityLevel.BASIC)
    assembly_price_basic = models.DecimalField(max_digits=8, decimal_places=2, default=150)
    assembly_price_intermediate = models.DecimalField(max_digits=8, decimal_places=2, default=250)
    assembly_price_advanced = models.DecimalField(max_digits=8, decimal_places=2, default=400)
    monthly_capacity = models.IntegerField(default=10)
    is_certified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_orders_completed = models.IntegerField(default=0)

    def __str__(self):
        return f"Centro assemblaggio: {self.business_name}"
