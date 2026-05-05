from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0004_seed_drone_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='droneproject',
            name='archived_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
    ]
