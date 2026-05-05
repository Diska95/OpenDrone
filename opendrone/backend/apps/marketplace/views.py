import logging
from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import DroneProject, ProjectFile, BOMItem, DroneCategory, ProjectReview, Brand
from .serializers import (
    DroneProjectListSerializer, DroneProjectDetailSerializer,
    DroneProjectWriteSerializer, ProjectFileSerializer,
    BOMItemSerializer, DroneCategorySerializer, ProjectReviewSerializer,
    BrandSerializer,
)
from apps.users.permissions import IsDesigner

logger = logging.getLogger(__name__)


class ProjectListView(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'difficulty', 'license_type', 'is_university_project', 'is_featured']
    search_fields = ['title', 'description', 'use_cases']
    ordering_fields = ['rating', 'order_count', 'created_at', 'estimated_total_cost_min']
    ordering = ['-created_at']

    def get_queryset(self):
        return DroneProject.objects.filter(status=DroneProject.Status.PUBLISHED).select_related(
            'designer', 'category'
        ).prefetch_related('files', 'bom_items')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DroneProjectWriteSerializer
        return DroneProjectListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsDesigner()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(designer=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'slug'

    def get_queryset(self):
        return DroneProject.objects.select_related('designer', 'category').prefetch_related(
            'files', 'bom_items', 'reviews__reviewer'
        )

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DroneProjectWriteSerializer
        return DroneProjectDetailSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsDesigner()]

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        DroneProject.objects.filter(pk=obj.pk).update(view_count=obj.view_count + 1)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def perform_update(self, serializer):
        obj = self.get_object()
        if obj.designer != self.request.user and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Non sei il proprietario di questo progetto.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.designer != self.request.user and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()
        if instance.status != DroneProject.Status.DRAFT:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Solo le bozze possono essere eliminate.')
        instance.delete()


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDesigner])
def publish_project(request, slug):
    project = generics.get_object_or_404(DroneProject, slug=slug, designer=request.user)
    if project.status not in [DroneProject.Status.DRAFT, DroneProject.Status.REJECTED]:
        return Response({'detail': 'Questo progetto non può essere pubblicato.'}, status=400)
    project.status = DroneProject.Status.PENDING_VALIDATION
    project.save()
    stl_file = project.files.filter(file_type='stl').first()
    if stl_file:
        try:
            from apps.validation.tasks import validate_stl_file
            validate_stl_file.delay(project.id, stl_file.id)
        except Exception as e:
            logger.warning(f"Validation task failed to enqueue: {e}")
    return Response({'detail': 'Progetto inviato per validazione.', 'status': project.status})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDesigner])
def fork_project(request, slug):
    original = generics.get_object_or_404(DroneProject, slug=slug, status=DroneProject.Status.PUBLISHED)
    forked = DroneProject.objects.create(
        designer=request.user,
        title=f"{original.title} (fork)",
        description=original.description,
        short_description=original.short_description,
        category=original.category,
        license_type=original.license_type,
        royalty_percentage=original.royalty_percentage,
        difficulty=original.difficulty,
        estimated_weight_grams=original.estimated_weight_grams,
        estimated_flight_time_minutes=original.estimated_flight_time_minutes,
        max_payload_grams=original.max_payload_grams,
        operating_range_km=original.operating_range_km,
        use_cases=original.use_cases,
        parent_project=original,
        status=DroneProject.Status.DRAFT,
    )
    DroneProject.objects.filter(pk=original.pk).update(fork_count=original.fork_count + 1)
    return Response(DroneProjectDetailSerializer(forked, context={'request': request}).data, status=201)


class ProjectFilesView(generics.ListCreateAPIView):
    serializer_class = ProjectFileSerializer

    def get_queryset(self):
        return ProjectFile.objects.filter(project__slug=self.kwargs['slug'])

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsDesigner()]

    def perform_create(self, serializer):
        project = generics.get_object_or_404(DroneProject, slug=self.kwargs['slug'], designer=self.request.user)
        file_obj = self.request.FILES.get('file')
        filename = file_obj.name if file_obj else serializer.validated_data.get('external_url', '')
        serializer.save(
            project=project,
            filename=filename,
            file_size_bytes=file_obj.size if file_obj else None
        )


class BOMView(generics.ListCreateAPIView):
    serializer_class = BOMItemSerializer

    def get_queryset(self):
        return BOMItem.objects.filter(project__slug=self.kwargs['slug'])

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsDesigner()]

    def perform_create(self, serializer):
        project = generics.get_object_or_404(DroneProject, slug=self.kwargs['slug'], designer=self.request.user)
        serializer.save(project=project)


class BOMItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BOMItemSerializer
    permission_classes = [IsAuthenticated, IsDesigner]

    def get_queryset(self):
        return BOMItem.objects.filter(project__slug=self.kwargs['slug'], project__designer=self.request.user)


class ProjectReviewsView(generics.ListCreateAPIView):
    serializer_class = ProjectReviewSerializer

    def get_queryset(self):
        return ProjectReview.objects.filter(project__slug=self.kwargs['slug']).select_related('reviewer')

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        project = generics.get_object_or_404(DroneProject, slug=self.kwargs['slug'])
        serializer.save(reviewer=self.request.user, project=project)
        reviews = ProjectReview.objects.filter(project=project)
        if reviews.exists():
            avg = sum(
                (r.rating_documentation + r.rating_difficulty_accuracy + r.rating_performance) / 3
                for r in reviews
            ) / reviews.count()
            project.rating = round(avg, 2)
            project.total_reviews = reviews.count()
            project.save()


class CategoryListView(generics.ListCreateAPIView):
    queryset = DroneCategory.objects.all().order_by('name')
    serializer_class = DroneCategorySerializer
    pagination_class = None

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]


class BrandListView(generics.ListAPIView):
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = Brand.objects.filter(is_active=True)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(categories__contains=[category])
        return qs


class MyProjectsView(generics.ListAPIView):
    serializer_class = DroneProjectListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DroneProject.objects.filter(designer=self.request.user).select_related('category')


class AdminPendingProjectsView(generics.ListAPIView):
    """Progetti in attesa di review — solo admin."""
    serializer_class = DroneProjectListSerializer
    pagination_class = None

    def get_permissions(self):
        from apps.users.permissions import IsAdminUser
        return [IsAuthenticated(), IsAdminUser()]

    def get_queryset(self):
        return DroneProject.objects.filter(
            status__in=[DroneProject.Status.PENDING_VALIDATION, DroneProject.Status.PENDING_REVIEW]
        ).select_related('designer', 'category').prefetch_related('files', 'bom_items').order_by('-created_at')


class AdminAllProjectsView(generics.ListAPIView):
    """Tutti i progetti per admin con filtro per status."""
    serializer_class = DroneProjectListSerializer
    pagination_class = None

    def get_permissions(self):
        from apps.users.permissions import IsAdminUser
        return [IsAuthenticated(), IsAdminUser()]

    def get_queryset(self):
        qs = DroneProject.objects.all().select_related('designer', 'category').prefetch_related('files', 'bom_items')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.order_by('-created_at')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_project(request, slug):
    user = request.user
    if not (user.is_staff or user.has_role('admin')):
        return Response({'detail': 'Solo gli admin possono approvare progetti.'}, status=403)
    from django.utils import timezone
    project = generics.get_object_or_404(DroneProject, slug=slug)
    project.status = DroneProject.Status.PUBLISHED
    project.published_at = timezone.now()
    project.save()
    return Response({'detail': 'Progetto approvato e pubblicato.', 'status': project.status})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_project(request, slug):
    user = request.user
    if not (user.is_staff or user.has_role('admin')):
        return Response({'detail': 'Solo gli admin possono rifiutare progetti.'}, status=403)
    project = generics.get_object_or_404(DroneProject, slug=slug)
    reason = request.data.get('reason', '')
    project.status = DroneProject.Status.REJECTED
    if reason:
        project.compliance_notes = (project.compliance_notes or '') + f'\n[ADMIN REJECT] {reason}'
    project.save()
    return Response({'detail': 'Progetto rifiutato.', 'status': project.status})
