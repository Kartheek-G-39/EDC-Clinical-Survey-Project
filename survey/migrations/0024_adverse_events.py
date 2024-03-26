# Generated by Django 4.2.11 on 2024-03-18 15:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0023_participant_enrollment_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Adverse_events',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('severity', models.CharField(choices=[('Unknown', '-------'), ('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], max_length=20)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('action_taken', models.CharField(choices=[('Monitored', 'Monitored'), ('No Action', 'No Action'), ('Treatment Adjusted', 'Treatment Adjusted')], default='No Action', max_length=20)),
                ('outcome', models.CharField(choices=[('Ongoing', 'Ongoing'), ('Escalated', 'Escalated'), ('Resolved', 'Resolved')], default='Ongoing', max_length=20)),
                ('event_type', models.CharField(choices=[('Unknown', '-------'), ('Mild', 'Mild'), ('Moderate', 'Moderate'), ('Severe', 'Severe')], default='Unknown', max_length=20)),
                ('participant_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adverse_evnents', to='survey.participant')),
                ('protocol_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adverse_events', to='survey.protocol')),
            ],
        ),
    ]
