from django.db import models


class RoyaltyLedger(models.Model):
    designer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='royalties')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    project = models.ForeignKey('marketplace.DroneProject', on_delete=models.CASCADE)
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_admin_fee = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    stripe_transfer_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    period_month = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Subscription(models.Model):
    class PlanType(models.TextChoices):
        CREATOR = 'creator', 'Creator'
        HUB = 'hub', 'Hub'

    class BillingCycle(models.TextChoices):
        MONTHLY = 'monthly', 'Mensile'
        ANNUAL = 'annual', 'Annuale'

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='subscriptions')
    plan_type = models.CharField(max_length=20, choices=PlanType.choices)
    billing_cycle = models.CharField(max_length=10, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_price_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default='active')
    amount_eur = models.DecimalField(max_digits=8, decimal_places=2)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
