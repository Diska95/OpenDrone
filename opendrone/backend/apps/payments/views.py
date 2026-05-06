import stripe
import logging
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone

from .models import RoyaltyLedger, Subscription
from apps.orders.models import Order, OrderStatusHistory

logger = logging.getLogger(__name__)


def _stripe():
    """Inizializza la api key al call-time invece che al module-load.
    Permette key rotation senza restart e niente fail se settings non pronto."""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def _stripe_secret_configured():
    sk = settings.STRIPE_SECRET_KEY or ''
    return bool(sk) and not sk.endswith('xxx')


def _stripe_webhook_secret_configured():
    ws = settings.STRIPE_WEBHOOK_SECRET or ''
    return bool(ws) and not ws.endswith('xxx')

PLAN_PRICES = {
    'creator_monthly': {'amount': Decimal('49.00'), 'plan': 'creator', 'cycle': 'monthly'},
    'creator_annual':  {'amount': Decimal('39.00'), 'plan': 'creator', 'cycle': 'annual'},
    'hub_monthly':     {'amount': Decimal('79.00'), 'plan': 'hub', 'cycle': 'monthly'},
    'hub_annual':      {'amount': Decimal('59.00'), 'plan': 'hub', 'cycle': 'annual'},
}


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        if not _stripe_webhook_secret_configured():
            logger.error(
                'Stripe webhook ricevuto ma STRIPE_WEBHOOK_SECRET non configurato. '
                'Endpoint disabilitato per sicurezza.'
            )
            return Response({'detail': 'Webhook non configurato.'}, status=503)

        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        try:
            event = _stripe().Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            logger.warning('Stripe webhook payload malformato.')
            return Response(status=400)
        except stripe.error.SignatureVerificationError:
            logger.warning('Stripe webhook signature non valida.')
            return Response(status=400)

        handlers = {
            'payment_intent.succeeded': self._handle_payment_succeeded,
            'payment_intent.payment_failed': self._handle_payment_failed,
        }
        handler = handlers.get(event['type'])
        if handler:
            handler(event['data']['object'])

        return Response({'received': True})

    def _handle_payment_succeeded(self, payment_intent):
        try:
            order = Order.objects.get(stripe_payment_intent_id=payment_intent['id'])
            self._execute_transfers(order)
        except Order.DoesNotExist:
            logger.warning(f"Ordine non trovato per PaymentIntent {payment_intent['id']}")

    def _handle_payment_failed(self, payment_intent):
        try:
            order = Order.objects.get(stripe_payment_intent_id=payment_intent['id'])
            order.status = Order.Status.CANCELLED
            order.save()
        except Order.DoesNotExist:
            pass

    def _execute_transfers(self, order):
        transfers = {}
        designer = order.project.designer

        if designer.stripe_account_id and order.design_fee > 0:
            net = order.design_fee * Decimal('0.975')
            try:
                t = _stripe().Transfer.create(
                    amount=int(net * 100),
                    currency='eur',
                    destination=designer.stripe_account_id,
                    transfer_group=f'ORDER_{order.id}',
                )
                transfers['designer'] = t.id
                RoyaltyLedger.objects.create(
                    designer=designer, order=order, project=order.project,
                    gross_amount=order.design_fee,
                    platform_admin_fee=order.design_fee * Decimal('0.025'),
                    net_amount=net, is_paid=True, stripe_transfer_id=t.id,
                    paid_at=timezone.now(),
                    period_month=timezone.now().replace(day=1).date(),
                )
            except stripe.error.StripeError as e:
                logger.error(f"Errore transfer designer: {e}")

        if order.print_node and order.print_node.stripe_account_id and order.print_cost > 0:
            try:
                t = _stripe().Transfer.create(
                    amount=int(order.print_cost * 100),
                    currency='eur',
                    destination=order.print_node.stripe_account_id,
                    transfer_group=f'ORDER_{order.id}',
                )
                transfers['print_node'] = t.id
            except stripe.error.StripeError as e:
                logger.error(f"Errore transfer nodo stampa: {e}")

        if order.assembly_center and order.assembly_center.stripe_account_id and order.assembly_cost > 0:
            try:
                t = _stripe().Transfer.create(
                    amount=int(order.assembly_cost * 100),
                    currency='eur',
                    destination=order.assembly_center.stripe_account_id,
                    transfer_group=f'ORDER_{order.id}',
                )
                transfers['assembly_center'] = t.id
            except stripe.error.StripeError as e:
                logger.error(f"Errore transfer centro assemblaggio: {e}")

        order.stripe_transfer_ids = transfers
        order.status = Order.Status.PAYMENT_CONFIRMED
        order.payment_confirmed_at = timezone.now()
        order.save()
        OrderStatusHistory.objects.create(
            order=order, status=order.status, note='Pagamento confermato, trasferimenti eseguiti'
        )
        from apps.marketplace.models import DroneProject
        DroneProject.objects.filter(pk=order.project.pk).update(
            order_count=order.project.order_count + 1
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def royalty_list(request):
    royalties = RoyaltyLedger.objects.filter(designer=request.user).select_related('order', 'project')
    data = [
        {
            'id': r.id,
            'project_title': r.project.title,
            'order_id': r.order.id,
            'gross_amount': str(r.gross_amount),
            'net_amount': str(r.net_amount),
            'is_paid': r.is_paid,
            'paid_at': r.paid_at,
            'period_month': r.period_month,
        }
        for r in royalties
    ]
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def subscription_plans(request):
    return Response({
        'plans': [
            {'id': 'creator_monthly', 'name': 'Creator', 'price': 49, 'cycle': 'mensile', 'description': 'Per designer professionali'},
            {'id': 'creator_annual',  'name': 'Creator Annual', 'price': 39, 'cycle': 'mensile (annuale)', 'description': 'Risparmia 20%'},
            {'id': 'hub_monthly',     'name': 'Hub', 'price': 79, 'cycle': 'mensile', 'description': 'Per nodi e centri'},
            {'id': 'hub_annual',      'name': 'Hub Annual', 'price': 59, 'cycle': 'mensile (annuale)', 'description': 'Risparmia 25%'},
        ]
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe(request):
    # SECURITY: stub disabilitato. La versione precedente creava una
    # Subscription(status='active') senza alcun pagamento Stripe — qualunque
    # utente autenticato poteva auto-attivarsi un piano. La rotta resta
    # esposta per non rompere chiamate frontend, ma risponde 503 finché
    # non viene wired Stripe Checkout / Stripe Subscription propriamente.
    logger.warning(
        'subscribe() chiamato da user_id=%s — endpoint disabilitato per security fix.',
        request.user.id,
    )
    return Response(
        {'detail': 'Abbonamenti non ancora disponibili. Contatta il supporto.'},
        status=503,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_subscription(request):
    sub = Subscription.objects.filter(user=request.user, status='active').first()
    if not sub:
        return Response({'subscription': None})
    return Response({'subscription': {
        'plan_type': sub.plan_type,
        'billing_cycle': sub.billing_cycle,
        'amount_eur': str(sub.amount_eur),
        'status': sub.status,
        'created_at': sub.created_at,
    }})
