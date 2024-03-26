# Generated by Django 4.2.11 on 2024-03-21 18:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("survey", "0024_adverse_events"),
    ]

    operations = [
        migrations.CreateModel(
            name="MedicationRecord",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("dosage", models.CharField(blank=True, max_length=150, null=True)),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("duration", models.DurationField(blank=True, null=True)),
                ("record_number", models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name="Medications",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("medication", models.CharField(max_length=255)),
            ],
        ),
        migrations.DeleteModel(
            name="Surveyy",
        ),
        migrations.AlterModelOptions(
            name="adverse_events",
            options={
                "verbose_name": "Adverse Event",
                "verbose_name_plural": "Adverse Evnets",
            },
        ),
        migrations.AddField(
            model_name="medicationrecord",
            name="medication",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="survey.medications"
            ),
        ),
        migrations.AddField(
            model_name="medicationrecord",
            name="participant_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="survey.participant"
            ),
        ),
    ]