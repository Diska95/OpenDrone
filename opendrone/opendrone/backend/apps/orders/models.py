from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'In attesa pagamento'
        PAYMENT_CONFIRMED = 'payment_confirmed', 'Pagamento confermato'
        ASSIGNED_PRINT = 'assigned_print', 'Assegnato a nodo stampa'
        PRINTING = 'printing', 'In stampa'
        PRINT_DONE = 'print_done', 'Stampa completata'
        ASSIGNED_ASSEMBLY = 'assigned_assembly', 'Assegnato a centro assemblaggio'
        ASSEMBLING = 'assembling', 'In assemblaggio'
        TESTING = 'testing', 'In test'
        SHIPPED = 'shipped', 'Spedito'
        DELIVERED = 'delivered', 'Consegnato'
        DISPUTED = 'disputed', 'In disputa'
        CANCELLED = 'cancelled', 'Annullato'
        REFUNDED = 'refunded', 'Rimborsato'

    class Mode(models.TextChoices):
        KIT = 'kit', 'Kit da assemblare'
        ASSEMBLED = 'assembled', 'Prodotto assemblato'

    customer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='orders')
    project = models.ForeignKey('marketplace.DroneProject', on_delete=models.CASCADE)
    print_node = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='print_orders')
    assembly_center = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='assembly_orders')
    mode = models.CharField(max_length=20, choices=Mode.choices, default=Mode.KIT)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    quantity = models.IntegerField(default=1)
    is_fast_track = models.BooleanField(default=False)
    design_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    print_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    components_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    assembly_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fast_track_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    components_margin = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stripe_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    insurance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_transfer_ids = models.JSONField(default=dict)
    shipping_address = models.JSONField(default=dict)
    tracking_number = models.CharField(max_length=100, blank=True)
    tracking_url = models.URLField(blank=True)
    courier = models.CharField(max_length=50, blank=True)
    insurance_included = models.BooleanField(default=True)
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ordine #{self.id} — {self.project.title}"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=30)
    changed_by = models.ForeignKey('users.User', null=True, on_delete=models.SET_NULL)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class Dispute(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Aperta'
        UNDER_REVIEW = 'under_review', 'In revisione'
        RESOLVED_REFUND = 'resolved_refund', 'Risolta con rimborso'
        RESOLVED_REPRINT = 'resolved_reprint', 'Risolta con ristampa'
        CLOSED = 'closed', 'Chiusa'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='disputes')
    opened_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    reason = models.TextField()
    evidence_urls = models.JSONField(default=list)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.OPEN)
    resolution_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
