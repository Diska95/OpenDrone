from rest_framework import generics
from rest_framework.permissions import AllowAny
from apps.users.models import PrintNodeProfile, AssemblyCenterProfile
from apps.users.serializers import PrintNodeProfileSerializer, AssemblyCenterProfileSerializer


class PrintNodeListView(generics.ListAPIView):
    queryset = PrintNodeProfile.objects.filter(is_certified=True, is_active=True).select_related('user')
    serializer_class = PrintNodeProfileSerializer
    permission_classes = [AllowAny]


class PrintNodeDetailView(generics.RetrieveAPIView):
    queryset = PrintNodeProfile.objects.filter(is_active=True).select_related('user')
    serializer_class = PrintNodeProfileSerializer
    permission_classes = [AllowAny]


class AssemblyCenterListView(generics.ListAPIView):
    queryset = AssemblyCenterProfile.objects.filter(is_certified=True, is_active=True).select_related('user')
    serializer_class = AssemblyCenterProfileSerializer
    permission_classes = [AllowAny]


class AssemblyCenterDetailView(generics.RetrieveAPIView):
    queryset = AssemblyCenterProfile.objects.filter(is_active=True).select_related('user')
    serializer_class = AssemblyCenterProfileSerializer
    permission_classes = [AllowAny]
