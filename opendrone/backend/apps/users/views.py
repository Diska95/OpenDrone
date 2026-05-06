import logging
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle, AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction

from .models import User, PrintNodeProfile, AssemblyCenterProfile, DesignerProfile
from .serializers import (
    RegisterSerializer, UserSerializer, ChangePasswordSerializer,
    PrintNodeProfileSerializer, AssemblyCenterProfileSerializer, DesignerProfileSerializer,
    DeleteAccountSerializer,
)
from .services import export_user_data, anonymize_account

logger = logging.getLogger(__name__)


# Throttle classi per scope nominati. Estendono SimpleRateThrottle (NON
# ScopedRateThrottle: quest'ultima ignora self.scope e legge view.throttle_scope,
# che su function-based @api_view non viene letto correttamente). Le classi
# qui sotto leggono il rate da REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] usando
# il proprio attributo `scope`.
class LoginThrottle(SimpleRateThrottle):
    scope = 'login'

    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': self.scope, 'ident': self.get_ident(request)}


class RegisterThrottle(SimpleRateThrottle):
    scope = 'register'

    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': self.scope, 'ident': self.get_ident(request)}


class GoogleAuthThrottle(SimpleRateThrottle):
    scope = 'google_auth'

    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': self.scope, 'ident': self.get_ident(request)}


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle, AnonRateThrottle]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle, AnonRateThrottle])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, username=email, password=password)
    if not user:
        return Response({'detail': 'Credenziali non valide.'}, status=status.HTTP_401_UNAUTHORIZED)
    refresh = RefreshToken.for_user(user)
    return Response({
        'user': UserSerializer(user).data,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })


VALID_SIGNUP_ROLES = {'designer', 'print_node', 'assembly_center', 'customer'}


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([GoogleAuthThrottle, AnonRateThrottle])
def google_auth_view(request):
    """Login/registrazione con Google Identity Services.

    Riceve un `credential` (id_token JWT firmato da Google), lo verifica con
    GOOGLE_OAUTH_CLIENT_ID, poi:
    - se l'utente esiste: rilascia JWT
    - se non esiste: crea l'utente (password non utilizzabile) col `role`
      indicato dal client e rilascia JWT
    """
    if not settings.GOOGLE_OAUTH_CLIENT_ID:
        return Response(
            {'detail': 'Login Google non configurato.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    credential = request.data.get('credential')
    if not credential:
        return Response({'detail': 'Token Google mancante.'}, status=400)

    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
        idinfo = google_id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.GOOGLE_OAUTH_CLIENT_ID,
        )
    except ValueError as exc:
        logger.warning('Google id_token non valido: %s', exc)
        return Response({'detail': 'Token Google non valido.'}, status=401)

    email = (idinfo.get('email') or '').lower().strip()
    if not email or not idinfo.get('email_verified'):
        return Response({'detail': 'Email Google non verificata.'}, status=400)

    first_name = (idinfo.get('given_name') or '')[:100]
    last_name = (idinfo.get('family_name') or '')[:100]

    user = User.objects.filter(email__iexact=email).first()
    created = False
    if user is None:
        role = (request.data.get('role') or 'customer').strip()
        if role not in VALID_SIGNUP_ROLES:
            return Response({'detail': 'Ruolo non valido.'}, status=400)
        with transaction.atomic():
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_verified=True,
            )
            user.set_unusable_password()
            roles = [role]
            if 'customer' not in roles:
                roles.append('customer')
            user.roles = roles
            user.save()
            if role == 'designer':
                DesignerProfile.objects.create(user=user)
            elif role == 'print_node':
                PrintNodeProfile.objects.create(
                    user=user, business_name='', address='', city='', province='IT'
                )
            elif role == 'assembly_center':
                AssemblyCenterProfile.objects.create(
                    user=user, business_name='', address='', city='', province='IT'
                )
        created = True
    else:
        # Utente esistente registrato con password: completa i nomi se vuoti
        dirty = False
        if not user.first_name and first_name:
            user.first_name = first_name
            dirty = True
        if not user.last_name and last_name:
            user.last_name = last_name
            dirty = True
        if not user.is_verified:
            user.is_verified = True
            dirty = True
        if dirty:
            user.save()

    if not user.is_active:
        return Response({'detail': 'Account disattivato.'}, status=403)

    refresh = RefreshToken.for_user(user)
    return Response({
        'user': UserSerializer(user).data,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'created': created,
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    refresh_value = request.data.get('refresh')
    if not refresh_value:
        return Response(
            {'detail': 'Refresh token mancante.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        RefreshToken(refresh_value).blacklist()
    except Exception as exc:
        # Token gia' blacklisted o malformato: loggalo, ma rispondi 200 cosi'
        # il client puo' completare la pulizia locale (idempotente).
        logger.warning('logout: blacklist fallita per user %s: %s', request.user.id, exc)
    return Response({'detail': 'Logout effettuato.'})


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = request.user
    if not user.check_password(serializer.validated_data['old_password']):
        return Response({'old_password': 'Password errata.'}, status=400)
    user.set_password(serializer.validated_data['new_password'])
    user.save()

    # Invalida tutti i refresh token attivi dell'utente: il device corrente
    # riceve i nuovi token nel payload di risposta; gli altri device vengono
    # disconnessi al prossimo refresh (entro ACCESS_TOKEN_LIFETIME = 60 min).
    try:
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
        for outstanding in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=outstanding)
    except Exception as exc:
        logger.warning('change_password: blacklist refresh tokens fallito per %s: %s', user.id, exc)

    refresh = RefreshToken.for_user(user)
    return Response({
        'detail': 'Password aggiornata. Le altre sessioni sono state disconnesse.',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })


# ─── GDPR — diritti dell'interessato ──────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def data_export_view(request):
    """Art. 15 GDPR (accesso) + art. 20 (portabilita').

    Ritorna in JSON tutti i dati personali riferibili all'utente.
    Il frontend lo offre come download.
    """
    data = export_user_data(request.user)
    response = Response(data)
    response['Content-Disposition'] = (
        f'attachment; filename="opendrone-data-export-{request.user.id}.json"'
    )
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account_view(request):
    """Art. 17 GDPR (oblio). Richiede:

    - password corrente per conferma identita'
    - confirmation = "ELIMINA" (anti click-accidentale)

    Esegue anonimizzazione in-place (vedi services.anonymize_account):
    profili business cancellati, recensioni blanked, User pseudonimizzato,
    refresh tokens blacklisted. Ordini/royalty restano per obblighi contabili.
    """
    serializer = DeleteAccountSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user
    if not user.check_password(serializer.validated_data['password']):
        logger.warning('delete_account: password errata user=%s', user.id)
        return Response({'password': 'Password errata.'}, status=400)

    summary = anonymize_account(user)
    return Response({
        'detail': (
            'Account cancellato. I tuoi dati personali sono stati rimossi o '
            'pseudonimizzati. Per obblighi contabili manteniamo gli ordini '
            'storici in forma non attribuibile.'
        ),
        'summary': summary,
    })


class PrintNodeProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = PrintNodeProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = PrintNodeProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'business_name': '', 'address': '', 'city': '', 'province': 'BO'}
        )
        return profile


class AssemblyCenterProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = AssemblyCenterProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = AssemblyCenterProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'business_name': '', 'address': '', 'city': '', 'province': 'BO'}
        )
        return profile


class DesignerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = DesignerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = DesignerProfile.objects.get_or_create(user=self.request.user)
        return profile


# ─── ADMIN ENDPOINTS ──────────────────────────────────────────────

class AdminUsersListView(generics.ListAPIView):
    """Lista utenti per admin con filtro per ruolo."""
    serializer_class = UserSerializer
    pagination_class = None

    def get_permissions(self):
        from .permissions import IsAdminUser
        return [IsAuthenticated(), IsAdminUser()]

    def get_queryset(self):
        qs = User.objects.all().order_by('-created_at')
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(roles__contains=[role])
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=(is_active == 'true'))
        return qs


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def admin_update_user(request, pk):
    """Admin può attivare/disattivare, verificare e certificare profili."""
    user = request.user
    if not (user.is_staff or user.has_role('admin')):
        return Response({'detail': 'Solo gli admin.'}, status=403)
    try:
        target = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'detail': 'Utente non trovato.'}, status=404)

    # Guard: non puoi disattivare te stesso (lock-out prevention)
    if 'is_active' in request.data:
        new_active = bool(request.data['is_active'])
        if target.id == user.id and not new_active:
            return Response(
                {'detail': 'Non puoi disattivare il tuo stesso account admin.'},
                status=400
            )
        target.is_active = new_active
    if 'is_verified' in request.data:
        target.is_verified = bool(request.data['is_verified'])
    target.save()

    # Certifica profile (per print_node, assembly_center, designer)
    certify = request.data.get('certify_profile')  # 'print_node' | 'assembly_center' | 'designer'
    if certify == 'print_node' and hasattr(target, 'print_node_profile'):
        target.print_node_profile.is_certified = bool(request.data.get('is_certified', True))
        target.print_node_profile.save()
    elif certify == 'assembly_center' and hasattr(target, 'assembly_profile'):
        target.assembly_profile.is_certified = bool(request.data.get('is_certified', True))
        target.assembly_profile.save()
    elif certify == 'designer' and hasattr(target, 'designer_profile'):
        target.designer_profile.is_certified = bool(request.data.get('is_certified', True))
        target.designer_profile.save()

    return Response(UserSerializer(target).data)
