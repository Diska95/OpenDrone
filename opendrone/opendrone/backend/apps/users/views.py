import logging
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User, PrintNodeProfile, AssemblyCenterProfile, DesignerProfile
from .serializers import (
    RegisterSerializer, UserSerializer, ChangePasswordSerializer,
    PrintNodeProfileSerializer, AssemblyCenterProfileSerializer, DesignerProfileSerializer
)

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
    except Exception:
        pass
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
    return Response({'detail': 'Password aggiornata.'})


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
