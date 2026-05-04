import logging
import stripe
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone

from .models import Order, OrderStatusHistory
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer, DisputeSerializer
from .pricing import calculate_order_price, find_best_print_node
from apps.marketplace.models import DroneProject

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.has_role('admin') or user.is_staff:
            return Order.objects.all().select_related('customer', 'project', 'print_node', 'assembly_center')
        return Order.objects.filter(customer=user).select_related('project')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    serializer = OrderCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        project = DroneProject.objects.prefetch_related('bom_items').get(
            id=data['project_id'],
            status=DroneProject.Status.PUBLISHED
        )
    except DroneProject.DoesNotExist:
        return Response({'detail': 'Progetto non trovato o non disponibile.'}, status=400)

    shipping = data['shipping_address']
    shipping_lat = float(shipping.get('latitude', 44.4))
    shipping_lon = float(shipping.get('longitude', 11.3))

    print_node_user = find_best_print_node(project, shipping_lat, shipping_lon)
    if not print_node_user:
        return Response({'detail': 'Nessun nodo di stampa disponibile al momento.'}, status=503)

    assembly_center_user = None
    if data['mode'] == Order.Mode.ASSEMBLED:
        from apps.users.models import AssemblyCenterProfile
        ac = AssemblyCenterProfile.objects.filter(is_certified=True, is_active=True).first()
        assembly_center_user = ac.user if ac else None

    pricing = calculate_order_price(
        project=project,
        print_node=print_node_user,
        assembly_center=assembly_center_user,
        mode=data['mode'],
        quantity=data['quantity'],
        is_fast_track=data['is_fast_track'],
    )

    order = Order.objects.create(
        customer=request.user,
        project=project,
        print_node=print_node_user,
        assembly_center=assembly_center_user,
        mode=data['mode'],
        quantity=data['quantity'],
        is_fast_track=data['is_fast_track'],
        shipping_address=data['shipping_address'],
        **pricing
    )

    OrderStatusHistory.objects.create(
        order=order, status=order.status, changed_by=request.user, note='Ordine creato'
    )

    if settings.STRIPE_SECRET_KEY and not settings.STRIPE_SECRET_KEY.endswith('xxx'):
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),
                currency='eur',
                metadata={'order_id': str(order.id)},
                transfer_group=f'ORDER_{order.id}',
            )
            order.stripe_payment_intent_id = intent.id
            order.save()
            return Response({
                'order': OrderSerializer(order).data,
                'client_secret': intent.client_secret,
                'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            }, status=201)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")

    return Response({'order': OrderSerializer(order).data}, status=201)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.has_role('admin'):
            return Order.objects.all()
        return Order.objects.filter(customer=user)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, pk):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'detail': 'Ordine non trovato.'}, status=404)

    user = request.user
    can_update = (
        user.is_staff or user.has_role('admin') or
        order.print_node == user or
        order.assembly_center == user
    )
    if not can_update:
        return Response({'detail': 'Non autorizzato.'}, status=403)

    serializer = OrderStatusUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    d = serializer.validated_data

    order.status = d['status']
    if d.get('tracking_number'):
        order.tracking_number = d['tracking_number']
    if d.get('tracking_url'):
        order.tracking_url = d['tracking_url']
    if d.get('courier'):
        order.courier = d['courier']
    if d['status'] == Order.Status.SHIPPED:
        order.shipped_at = timezone.now()
    elif d['status'] == Order.Status.DELIVERED:
        order.delivered_at = timezone.now()
    order.save()

    OrderStatusHistory.objects.create(
        order=order, status=order.status, changed_by=user,
        note=d.get('note', '')
    )
    return Response(OrderSerializer(order).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def open_dispute(request, pk):
    order = generics.get_object_or_404(Order, pk=pk, customer=request.user)
    if order.status in [Order.Status.CANCELLED, Order.Status.REFUNDED]:
        return Response({'detail': 'Non puoi aprire una disputa su questo ordine.'}, status=400)
    serializer = DisputeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dispute = serializer.save(order=order, opened_by=request.user)
    order.status = Order.Status.DISPUTED
    order.save()
    return Response(DisputeSerializer(dispute).data, status=201)
