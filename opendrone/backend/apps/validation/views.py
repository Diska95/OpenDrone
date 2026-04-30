from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from .models import ValidationReport
from apps.marketplace.models import DroneProject


class STLUploadSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    file = serializers.FileField()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_and_validate_stl(request):
    from apps.marketplace.models import ProjectFile
    from .tasks import validate_stl_file

    project_id = request.data.get('project_id')
    file_obj = request.FILES.get('file')

    if not project_id or not file_obj:
        return Response({'detail': 'project_id e file sono richiesti.'}, status=400)

    try:
        project = DroneProject.objects.get(id=project_id, designer=request.user)
    except DroneProject.DoesNotExist:
        return Response({'detail': 'Progetto non trovato.'}, status=404)

    stl_file = ProjectFile.objects.create(
        project=project,
        file_type='stl',
        file=file_obj,
        filename=file_obj.name,
        file_size_bytes=file_obj.size,
    )

    try:
        task = validate_stl_file.delay(project.id, stl_file.id)
        task_id = task.id
    except Exception:
        task_id = None
    return Response({'task_id': task_id, 'file_id': stl_file.id, 'detail': 'Validazione avviata.'}, status=202)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validation_result(request, project_id):
    report = ValidationReport.objects.filter(project_id=project_id).first()
    if not report:
        return Response({'detail': 'Nessun report disponibile.'}, status=404)
    return Response({
        'status': report.status,
        'is_printable': report.is_printable,
        'issues': report.issues,
        'warnings': report.warnings,
        'estimated_filament_grams': str(report.estimated_filament_grams or ''),
        'estimated_print_time_hours': str(report.estimated_print_time_hours or ''),
        'min_wall_thickness_mm': str(report.min_wall_thickness_mm or ''),
        'overhang_angle_max': str(report.overhang_angle_max or ''),
        'validated_at': report.validated_at,
    })
