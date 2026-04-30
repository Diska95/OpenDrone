from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, DesignerProfile, PrintNodeProfile, AssemblyCenterProfile


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    ordering = ['-created_at']
    list_display = ['email', 'first_name', 'last_name', 'roles', 'is_verified', 'is_active']
    list_filter = ['is_active', 'is_staff', 'is_verified']
    search_fields = ['email', 'first_name', 'last_name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Dati personali', {'fields': ('first_name', 'last_name', 'bio', 'avatar')}),
        ('Ruoli e stato', {'fields': ('roles', 'is_verified', 'is_active', 'is_staff', 'is_superuser')}),
        ('Stripe', {'fields': ('stripe_account_id', 'stripe_customer_id')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2', 'roles')}),
    )


@admin.register(PrintNodeProfile)
class PrintNodeProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'city', 'is_certified', 'is_active', 'rating']
    list_filter = ['is_certified', 'is_active']


@admin.register(AssemblyCenterProfile)
class AssemblyCenterProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'city', 'is_certified', 'max_complexity', 'rating']


@admin.register(DesignerProfile)
class DesignerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_certified', 'rating', 'total_royalties_earned']
