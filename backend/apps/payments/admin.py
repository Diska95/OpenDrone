from django.contrib import admin
from .models import RoyaltyLedger, Subscription


@admin.register(RoyaltyLedger)
class RoyaltyLedgerAdmin(admin.ModelAdmin):
    list_display = ['designer', 'project', 'gross_amount', 'net_amount', 'is_paid', 'paid_at', 'period_month']
    list_filter = ['is_paid', 'period_month']
    search_fields = ['designer__email', 'project__title']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan_type', 'billing_cycle', 'amount_eur', 'status', 'created_at']
    list_filter = ['plan_type', 'billing_cycle', 'status']
