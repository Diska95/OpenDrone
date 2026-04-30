from django.contrib import admin
from django.utils import timezone
from .models import Order, OrderStatusHistory, Dispute


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['status', 'changed_by', 'note', 'created_at']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'project', 'status', 'mode', 'total_amount', 'created_at']
    list_filter = ['status', 'mode', 'is_fast_track']
    search_fields = ['customer__email', 'project__title', 'stripe_payment_intent_id']
    readonly_fields = [
        'design_fee', 'print_cost', 'components_cost', 'assembly_cost',
        'fast_track_fee', 'platform_commission', 'components_margin',
        'stripe_fee', 'insurance_amount', 'total_amount',
        'stripe_payment_intent_id', 'created_at', 'updated_at',
    ]
    inlines = [OrderStatusHistoryInline]
    actions = ['mark_payment_confirmed']

    def mark_payment_confirmed(self, request, queryset):
        for order in queryset:
            order.status = Order.Status.PAYMENT_CONFIRMED
            order.payment_confirmed_at = timezone.now()
            order.save()
            OrderStatusHistory.objects.create(
                order=order, status=order.status, changed_by=request.user,
                note='Pagamento confermato manualmente da admin'
            )
    mark_payment_confirmed.short_description = 'Conferma pagamento (manuale)'


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ['order', 'opened_by', 'status', 'created_at']
    list_filter = ['status']
