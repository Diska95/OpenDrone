"""
Servizi GDPR per i diritti degli interessati (art. 15-22).

- export_user_data: art. 15 (accesso) + art. 20 (portabilita').
- anonymize_account: art. 17 (oblio) con preservazione dati contabili
  obbligatori per legge (10 anni). L'account viene disattivato e
  pseudonimizzato, gli ordini/royalty restano collegati ad un User
  "anonimo" cosi' da non rompere FK e contabilita'.
"""
import logging
import uuid
from django.utils import timezone

logger = logging.getLogger(__name__)


def export_user_data(user) -> dict:
    """Restituisce un dict serializzabile JSON con TUTTI i dati personali
    riferibili a `user`. Include anche dati relazionali (ordini, recensioni,
    royalty) ma in forma sintetica per evitare payload giganteschi.
    """
    from apps.marketplace.models import DroneProject, ProjectReview
    from apps.orders.models import Order
    from apps.payments.models import RoyaltyLedger, Subscription
    from apps.notifications.models import Notification

    def _profile_dict(profile, fields):
        if profile is None:
            return None
        return {f: getattr(profile, f, None) for f in fields}

    designer = getattr(user, 'designer_profile', None)
    print_node = getattr(user, 'print_node_profile', None)
    assembly = getattr(user, 'assembly_profile', None)

    return {
        '_meta': {
            'export_format': 'opendrone-user-export',
            'export_version': '1.0',
            'generated_at': timezone.now().isoformat(),
            'note': (
                'Questo file contiene tutti i tuoi dati personali trattati da OpenDrone. '
                'Per i diritti GDPR (rettifica, cancellazione, opposizione) vedi la Privacy Policy.'
            ),
        },
        'account': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user.bio,
            'avatar': user.avatar.url if user.avatar else None,
            'roles': user.roles,
            'is_verified': user.is_verified,
            'is_active': user.is_active,
            'stripe_account_id': user.stripe_account_id,
            'stripe_customer_id': user.stripe_customer_id,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
        },
        'profiles': {
            'designer': _profile_dict(designer, [
                'portfolio_url', 'university', 'is_university_project',
                'is_certified', 'total_royalties_earned', 'rating', 'total_reviews',
            ]),
            'print_node': _profile_dict(print_node, [
                'business_name', 'address', 'city', 'province',
                'latitude', 'longitude', 'materials', 'max_print_volume_mm',
                'hourly_capacity', 'price_per_gram', 'sla_hours',
                'is_certified', 'is_active', 'rating',
            ]),
            'assembly_center': _profile_dict(assembly, [
                'business_name', 'address', 'city', 'province',
                'latitude', 'longitude', 'max_complexity',
                'assembly_price_basic', 'assembly_price_intermediate', 'assembly_price_advanced',
                'monthly_capacity', 'is_certified', 'is_active', 'rating',
            ]),
        },
        'projects_published': [
            {
                'id': p.id, 'slug': p.slug, 'title': p.title,
                'status': p.status, 'license_type': p.license_type,
                'created_at': p.created_at.isoformat(),
                'order_count': p.order_count, 'rating': float(p.rating),
            }
            for p in DroneProject.objects.filter(designer=user)
        ],
        'orders_placed': [
            {
                'id': o.id, 'project_title': o.project.title if o.project_id else None,
                'status': o.status, 'mode': o.mode, 'quantity': o.quantity,
                'total_amount': str(o.total_amount),
                'shipping_address': o.shipping_address,
                'tracking_number': o.tracking_number,
                'created_at': o.created_at.isoformat(),
                'delivered_at': o.delivered_at.isoformat() if o.delivered_at else None,
            }
            for o in Order.objects.filter(customer=user).select_related('project')
        ],
        'orders_as_print_node': [
            {'id': o.id, 'status': o.status, 'created_at': o.created_at.isoformat()}
            for o in Order.objects.filter(print_node=user)
        ],
        'orders_as_assembly_center': [
            {'id': o.id, 'status': o.status, 'created_at': o.created_at.isoformat()}
            for o in Order.objects.filter(assembly_center=user)
        ],
        'reviews_written': [
            {
                'id': r.id, 'project_slug': r.project.slug,
                'rating_documentation': r.rating_documentation,
                'rating_difficulty_accuracy': r.rating_difficulty_accuracy,
                'rating_performance': r.rating_performance,
                'comment': r.comment,
                'created_at': r.created_at.isoformat(),
            }
            for r in ProjectReview.objects.filter(reviewer=user).select_related('project')
        ],
        'royalties': [
            {
                'id': r.id, 'project_title': r.project.title if r.project_id else None,
                'gross_amount': str(r.gross_amount),
                'net_amount': str(r.net_amount),
                'is_paid': r.is_paid,
                'paid_at': r.paid_at.isoformat() if r.paid_at else None,
                'period_month': r.period_month.isoformat() if r.period_month else None,
            }
            for r in RoyaltyLedger.objects.filter(designer=user).select_related('project')
        ],
        'subscriptions': [
            {
                'id': s.id, 'plan_type': s.plan_type, 'billing_cycle': s.billing_cycle,
                'status': s.status, 'amount_eur': str(s.amount_eur),
                'created_at': s.created_at.isoformat(),
                'cancelled_at': s.cancelled_at.isoformat() if s.cancelled_at else None,
            }
            for s in Subscription.objects.filter(user=user)
        ],
        'notifications_recent': [
            {
                'id': n.id, 'title': n.title, 'message': n.message,
                'is_read': n.is_read, 'created_at': n.created_at.isoformat(),
            }
            for n in Notification.objects.filter(user=user).order_by('-created_at')[:200]
        ],
    }


def anonymize_account(user) -> dict:
    """Applica art. 17 GDPR. Strategia:

    - HARD-DELETE: avatar, bio, profili business (designer/print_node/assembly).
      Recensioni: contenuto azzerato (commento blanked) ma il record resta
      per non corrompere medie/rating dei progetti recensiti.
    - PSEUDONIMIZZAZIONE in-place: User mantiene id e FK ma diventa
      "Utente cancellato" con email randomizzata, password unusable,
      is_active=False. Cosi' ordini/royalty/recensioni restano integre per
      obblighi contabili (10 anni) ma non sono piu' attribuibili
      all'interessato originale.
    - Refresh tokens: blacklisted tutti.

    Ritorna un dict con il dettaglio dell'operazione (per log/risposta).
    """
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
    from apps.marketplace.models import ProjectReview
    from django.db import transaction

    summary = {
        'user_id': user.id,
        'tokens_blacklisted': 0,
        'reviews_anonymized': 0,
        'profiles_deleted': [],
        'avatar_deleted': False,
    }

    with transaction.atomic():
        # 1. Blacklist tutti i refresh tokens dell'utente
        for outstanding in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=outstanding)
            summary['tokens_blacklisted'] += 1

        # 2. Cancella file avatar da S3
        if user.avatar:
            try:
                user.avatar.delete(save=False)
                summary['avatar_deleted'] = True
            except Exception as exc:
                logger.warning('anonymize: avatar delete fallita user=%s: %s', user.id, exc)

        # 3. Cancella profili business (contengono PII commerciale)
        for attr, label in [
            ('designer_profile', 'designer'),
            ('print_node_profile', 'print_node'),
            ('assembly_profile', 'assembly_center'),
        ]:
            profile = getattr(user, attr, None)
            if profile is not None:
                profile.delete()
                summary['profiles_deleted'].append(label)

        # 4. Anonimizza recensioni: il record resta (per integrita' rating
        # del progetto), ma autore e contenuto vengono blanked.
        reviews = ProjectReview.objects.filter(reviewer=user)
        for review in reviews:
            review.comment = '[recensione del cancellato]'
            review.build_photos = []
            review.save(update_fields=['comment', 'build_photos'])
            summary['reviews_anonymized'] += 1

        # 5. Pseudonimizza User in-place
        anon_id = uuid.uuid4().hex[:12]
        user.email = f'deleted-{anon_id}@anon.opendrone.local'
        user.first_name = 'Utente'
        user.last_name = 'cancellato'
        user.bio = ''
        user.avatar = None
        user.is_active = False
        user.is_verified = False
        user.stripe_account_id = ''
        user.stripe_customer_id = ''
        user.set_unusable_password()
        user.save()

    logger.info('anonymize_account user_id=%s summary=%s', summary['user_id'], summary)
    return summary
