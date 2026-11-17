import uuid

import django.utils.timezone
from django.db import migrations, models

import apps.identity.models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Player",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("session_key", models.CharField(db_index=True, max_length=64, unique=True)),
                (
                    "display_name",
                    models.CharField(
                        default=apps.identity.models.generate_display_name,
                        max_length=40,
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        default=apps.identity.models.generate_color,
                        max_length=7,
                    ),
                ),
                ("last_claim_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["display_name"],
            },
        ),
    ]