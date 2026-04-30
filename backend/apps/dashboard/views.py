from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Avg
from apps.orders.models import Order
from apps.marketplace.models import DroneProject
from apps.payments.models import RoyaltyLedger


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def designer_dashboard(request):
    user = request.user
    projects = DroneProject.objects.filter(designer=user)
    royalties = RoyaltyLedger.objects.filter(designer=user)
    return Response({
        'projects_total': projects.count(),
        'projects_published': projects.filter(status='published').count(),
        'projects_draft': projects.filter(status='draft').count(),
        'total_orders': projects.aggregate(s=Sum('order_count'))['s'] or 0,
        'total_royalties_earned': str(royalties.aggregate(s=Sum('gross_amount'))['s'] or 0),
        'total_royalties_net': str(royalties.aggregate(s=Sum('net_amount'))['s'] or 0),
        'pending_royalties': str(royalties.filter(is_paid=False).aggregate(s=Sum('net_amount'))['s'] or 0),
        'avg_rating': float(projects.aggregate(a=Avg('rating'))['a'] or 0),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def print_node_dashboard(request):
    orders = Order.objects.filter(print_node=request.user)
    return Response({
        'orders_total': orders.count(),
        'orders_active': orders.filter(status__in=['assigned_print', 'printing']).count(),
        'orders_completed': orders.filter(status='delivered').count(),
        'orders_disputed': orders.filter(status='disputed').count(),
        'total_revenue': str(orders.filter(status='delivered').aggregate(s=Sum('print_cost'))['s'] or 0),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assembly_dashboard(request):
    orders = Order.objects.filter(assembly_center=request.user)
    return Response({
        'orders_total': orders.count(),
        'orders_active': orders.filter(status__in=['assigned_assembly', 'assembling', 'testing']).count(),
        'orders_completed': orders.filter(status='delivered').count(),
        'total_revenue': str(orders.filter(status='delivered').aggregate(s=Sum('assembly_cost'))['s'] or 0),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    if not (request.user.is_staff or request.user.has_role('admin')):
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied()
    orders = Order.objects.all()
    projects = DroneProject.objects.all()
    return Response({
        'orders_total': orders.count(),
        'orders_pending_payment': orders.filter(status='pending').count(),
        'orders_active': orders.filter(status__in=['payment_confirmed', 'assigned_print', 'printing', 'print_done', 'assembling']).count(),
        'orders_delivered': orders.filter(status='delivered').count(),
        'orders_disputed': orders.filter(status='disputed').count(),
        'total_gmv': str(orders.filter(status='delivered').aggregate(s=Sum('total_amount'))['s'] or 0),
        'total_commission': str(orders.filter(status='delivered').aggregate(s=Sum('platform_commission'))['s'] or 0),
        'projects_published': projects.filter(status='published').count(),
        'projects_pending': projects.filter(status__in=['pending_validation', 'pending_review']).count(),
    })
