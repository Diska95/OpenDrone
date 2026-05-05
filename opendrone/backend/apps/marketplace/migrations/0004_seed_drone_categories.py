from django.db import migrations
from django.utils.text import slugify


SEED_CATEGORIES = [
    {'name': 'Racing FPV', 'icon': '🏁',
     'description': 'Quad da gara FPV, leggeri e veloci, tipicamente 5".'},
    {'name': 'Freestyle', 'icon': '🎮',
     'description': 'Quad acrobatici per voli freestyle FPV.'},
    {'name': 'Cinematic', 'icon': '🎬',
     'description': 'Quad per riprese cinematografiche fluide e stabili.'},
    {'name': 'Tinywhoop / Micro', 'icon': '🐝',
     'description': 'Microquad indoor con protezioni eliche, sub-65 mm.'},
    {'name': 'Toothpick / Sub-250g', 'icon': '🪥',
     'description': 'Quad ultraleggeri sub-250g (esenti da molte regole EASA).'},
    {'name': 'Long Range', 'icon': '🛰️',
     'description': 'Quad per voli a lunga distanza, autonomia estesa.'},
    {'name': 'Cinelifter', 'icon': '🎥',
     'description': 'Heavy lift per camere cinema professionali (RED, BMPCC).'},
    {'name': 'Wing / Plane', 'icon': '✈️',
     'description': 'Ala fissa, autonomia estesa per mappatura e ricognizione.'},
    {'name': 'VTOL', 'icon': '🚀',
     'description': 'Vertical Take-Off and Landing — ibrido elicottero/ala.'},
    {'name': 'Hexacopter', 'icon': '⬢',
     'description': 'Sei motori, ridondanza e maggiore portata.'},
    {'name': 'Industrial / Inspection', 'icon': '🏭',
     'description': 'Ispezioni industriali, infrastrutture, termografia.'},
    {'name': 'Agricultural', 'icon': '🌾',
     'description': 'Agricoltura di precisione, mappatura colture, irrorazione.'},
    {'name': 'Educational', 'icon': '🎓',
     'description': 'Progetti didattici, makerspace, università.'},
    {'name': 'Other', 'icon': '📦',
     'description': 'Categoria aperta per progetti che non rientrano altrove.'},
]


def seed_categories(apps, schema_editor):
    DroneCategory = apps.get_model('marketplace', 'DroneCategory')
    for cat in SEED_CATEGORIES:
        DroneCategory.objects.get_or_create(
            slug=slugify(cat['name']),
            defaults={
                'name': cat['name'],
                'icon': cat['icon'],
                'description': cat['description'],
            },
        )


def remove_seed_categories(apps, schema_editor):
    DroneCategory = apps.get_model('marketplace', 'DroneCategory')
    slugs = [slugify(c['name']) for c in SEED_CATEGORIES]
    DroneCategory.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0003_brand_bomitem_brand'),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_seed_categories),
    ]
