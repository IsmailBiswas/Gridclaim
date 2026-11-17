import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("identity", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Cell",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("x", models.PositiveSmallIntegerField()),
                ("y", models.PositiveSmallIntegerField()),
                ("version", models.PositiveIntegerField(default=0)),
                ("claimed_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="cells",
                        to="identity.player",
                    ),
                ),
            ],
            options={
                "ordering": ["y", "x"],
            },
        ),
        migrations.AddIndex(
            model_name="cell",
            index=models.Index(fields=["owner"], name="board_cell_owner_i_6d2c1f_idx"),
        ),
        migrations.AddConstraint(
            model_name="cell",
            constraint=models.UniqueConstraint(fields=("x", "y"), name="uniq_cell_coordinate"),
        ),
    ]