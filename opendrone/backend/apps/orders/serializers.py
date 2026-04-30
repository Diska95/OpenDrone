from rest_framework import serializers
from .models import Order, OrderStatusHistory, Dispute
from apps.marketplace.serializers import DroneProjectListSerializer


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = '__all__'


class DisputeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = '__all__'
        read_only_fields = ['opened_by', 'order', 'status', 'resolved_at']


class OrderSerializer(serializers.ModelSerializer):
    project_data = DroneProjectListSerializer(source='project', read_only=True)
    history = OrderStatusHistorySerializer(many=True, read_only=True)
    disputes = DisputeSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = [
            'customer', 'status', 'print_node', 'assembly_center',
            'design_fee', 'print_cost', 'components_cost', 'assembly_cost',
            'fast_track_fee', 'platform_commission', 'components_margin',
            'stripe_fee', 'insurance_amount', 'total_amount',
            'stripe_payment_intent_id', 'stripe_transfer_ids',
            'created_at', 'updated_at', 'payment_confirmed_at', 'shipped_at', 'delivered_at',
        ]


class OrderCreateSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    mode = serializers.ChoiceField(choices=['kit', 'assembled'])
    quantity = serializers.IntegerField(min_value=1, max_value=10, default=1)
    is_fast_track = serializers.BooleanField(default=False)
    shipping_address = serializers.DictField()


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)
    note = serializers.CharField(required=False, allow_blank=True)
    tracking_number = serializers.CharField(required=False, allow_blank=True)
    tracking_url = serializers.URLField(required=False, allow_blank=True)
    courier = serializers.CharField(required=False, allow_blank=True)
