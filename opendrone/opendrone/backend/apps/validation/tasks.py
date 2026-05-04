from celery import shared_task
import logging
import os

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def validate_stl_file(self, project_id, file_id):
    try:
        import trimesh
        import numpy as np
        from .models import ValidationReport
        from apps.marketplace.models import DroneProject, ProjectFile

        project = DroneProject.objects.get(id=project_id)
        stl_file = ProjectFile.objects.get(id=file_id)
        report = ValidationReport(project=project)
        issues = []
        warnings = []

        file_path = stl_file.file.path if hasattr(stl_file.file, 'path') else None
        if not file_path or not os.path.exists(file_path):
            report.status = ValidationReport.Status.FAILED
            report.issues = ['File STL non accessibile']
            report.save()
            return {'status': 'failed'}

        mesh = trimesh.load(file_path)

        report.has_open_surfaces = not mesh.is_watertight
        if not mesh.is_watertight:
            issues.append('La mesh ha superfici aperte — potrebbe causare problemi di stampa')

        report.has_non_manifold = not mesh.is_volume
        if not mesh.is_volume:
            issues.append('Geometria non-manifold rilevata')

        bounds = mesh.bounds
        size = bounds[1] - bounds[0]
        min_dim = float(min(size))
        report.min_wall_thickness_mm = round(min_dim, 2)
        if min_dim < 1.2:
            issues.append(f'Dimensione minima {min_dim:.2f}mm sotto la soglia critica di 1.2mm')
        elif min_dim < 2.0:
            warnings.append(f'Dimensione minima {min_dim:.2f}mm potrebbe causare fragilità')

        face_normals = mesh.face_normals
        z_component = face_normals[:, 2]
        max_overhang = float(np.degrees(np.arccos(np.clip(-float(z_component.min()), -1, 1))))
        report.overhang_angle_max = round(max_overhang, 2)
        if max_overhang > 50:
            warnings.append(f'Overhang massimo {max_overhang:.1f}° — potrebbero servire supporti')

        volume_cm3 = float(mesh.volume) / 1000 if mesh.volume else 50
        filament_grams = volume_cm3 * 1.24
        print_time_hours = filament_grams / 15

        report.estimated_filament_grams = round(filament_grams, 2)
        report.estimated_print_time_hours = round(print_time_hours, 2)
        report.issues = issues
        report.warnings = warnings
        report.is_printable = len(issues) == 0
        report.status = ValidationReport.Status.PASSED if report.is_printable else (
            ValidationReport.Status.WARNING if not issues and warnings else ValidationReport.Status.FAILED
        )
        report.raw_report = {
            'volume_cm3': volume_cm3,
            'face_count': len(mesh.faces),
            'vertex_count': len(mesh.vertices),
        }
        report.save()

        DroneProject.objects.filter(pk=project_id).update(
            estimated_print_time_hours=report.estimated_print_time_hours
        )

        if report.is_printable and project.status == DroneProject.Status.PENDING_VALIDATION:
            DroneProject.objects.filter(pk=project_id).update(
                status=DroneProject.Status.PENDING_REVIEW
            )

        return {'status': report.status, 'report_id': report.id}

    except ImportError:
        from .models import ValidationReport
        from apps.marketplace.models import DroneProject
        project = DroneProject.objects.get(id=project_id)
        report = ValidationReport.objects.create(
            project=project,
            status=ValidationReport.Status.WARNING,
            is_printable=True,
            warnings=['Validazione geometrica non disponibile — trimesh non installato'],
            estimated_filament_grams=200,
            estimated_print_time_hours=13,
        )
        if project.status == DroneProject.Status.PENDING_VALIDATION:
            DroneProject.objects.filter(pk=project_id).update(status=DroneProject.Status.PENDING_REVIEW)
        return {'status': 'warning', 'report_id': report.id}

    except Exception as exc:
        logger.error(f"Errore validazione STL: {exc}")
        raise self.retry(exc=exc, countdown=60)
