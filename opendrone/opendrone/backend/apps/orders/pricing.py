from decimal import Decimal
import math
import logging

logger = logging.getLogger(__name__)

PLATFORM_COMMISSION_RATE = Decimal('0.10')
COMPONENTS_MARGIN_RATE = Decimal('0.12')
DESIGNER_ADMIN_FEE_RATE = Decimal('0.025')
FAST_TRACK_PREMIUM = Decimal('0.30')
STRIPE_RATE = Decimal('0.0165')
STRIPE_FIXED = Decimal('0.25')
INSURANCE_RATE = Decimal('0.02')


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def get_project_complexity(project):
    return project.difficulty


def calculate_order_price(project, print_node, assembly_center, mode, quantity, is_fast_track):
    from apps.orders.models import Order

    bom_total = sum(
        item.unit_price_eur * item.quantity
        for item in project.bom_items.all()
    )
    components_cost = Decimal(str(bom_total)) * quantity
    components_margin = components_cost * COMPONENTS_MARGIN_RATE

    filament_grams = Decimal('200')
    validation = project.validations.last() if hasattr(project, 'validations') else None
    if validation and validation.estimated_filament_grams:
        filament_grams = Decimal(str(validation.estimated_filament_grams))

    print_cost = Decimal(str(print_node.print_node_profile.price_per_gram)) * filament_grams * quantity

    design_fee_gross = (Decimal(str(project.royalty_percentage)) / 100) * (print_cost + components_cost)

    assembly_cost = Decimal('0')
    if mode == Order.Mode.ASSEMBLED and assembly_center:
        complexity = get_project_complexity(project)
        profile = assembly_center.assembly_profile
        price_map = {
            'basic': profile.assembly_price_basic,
            'intermediate': profile.assembly_price_intermediate,
            'advanced': profile.assembly_price_advanced,
        }
        assembly_cost = Decimal(str(price_map.get(complexity, profile.assembly_price_basic))) * quantity

    subtotal = print_cost + components_cost + design_fee_gross + assembly_cost
    platform_commission = subtotal * PLATFORM_COMMISSION_RATE

    fast_track_fee = Decimal('0')
    if is_fast_track:
        fast_track_fee = subtotal * FAST_TRACK_PREMIUM

    insurance_amount = (print_cost + components_cost) * INSURANCE_RATE
    gross_total = subtotal + platform_commission + components_margin + fast_track_fee + insurance_amount
    stripe_fee = gross_total * STRIPE_RATE + STRIPE_FIXED
    total = gross_total + stripe_fee

    def r(v):
        return v.quantize(Decimal('0.01'))

    return {
        'design_fee': r(design_fee_gross),
        'print_cost': r(print_cost),
        'components_cost': r(components_cost),
        'assembly_cost': r(assembly_cost),
        'fast_track_fee': r(fast_track_fee),
        'components_margin': r(components_margin),
        'platform_commission': r(platform_commission),
        'insurance_amount': r(insurance_amount),
        'stripe_fee': r(stripe_fee),
        'total_amount': r(total),
    }


def find_best_print_node(project, shipping_lat, shipping_lon):
    from apps.users.models import PrintNodeProfile

    required_material = 'PETG'
    candidates = list(PrintNodeProfile.objects.filter(
        is_certified=True, is_active=True,
    ).select_related('user'))
    candidates = [c for c in candidates if required_material in (c.materials or [])]
    if not candidates:
        candidates = list(PrintNodeProfile.objects.filter(is_active=True).select_related('user'))
    if not candidates:
        return None

    scored = []
    for node in candidates:
        try:
            distance_km = haversine(float(node.latitude), float(node.longitude), shipping_lat, shipping_lon)
        except Exception:
            distance_km = 9999

        material_rating = float(node.rating_by_material.get(required_material, float(node.rating or 3)))
        load_ratio = node.current_load / max(node.hourly_capacity, 1)

        score = (
            material_rating * 30 +
            max(0, 10 - distance_km / 10) * 25 +
            (1 - load_ratio) * 20 +
            float(node.rating or 3) * 15 +
            (1 / max(float(node.price_per_gram), 0.01)) * 10
        )
        scored.append((score, node))

    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[0][1].user
