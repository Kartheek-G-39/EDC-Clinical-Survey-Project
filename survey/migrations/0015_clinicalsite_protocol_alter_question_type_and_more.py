# Generated by Django 4.2.10 on 2024-02-25 01:41

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0014_survey_redirect_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClinicalSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('location', models.TextField(verbose_name='Location')),
                ('site_code', models.CharField(max_length=100, unique=True, verbose_name='Site Code')),
            ],
            options={
                'verbose_name': 'clinical site',
                'verbose_name_plural': 'clinical sites',
            },
        ),
        migrations.CreateModel(
            name='Protocol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study_id', models.CharField(max_length=100, unique=True, verbose_name='Study ID')),
                ('title', models.CharField(max_length=400, verbose_name='Title')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('start_date', models.DateField(default=django.utils.timezone.now, verbose_name='Start Date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End Date')),
            ],
            options={
                'verbose_name': 'protocol',
                'verbose_name_plural': 'protocols',
            },
        ),
        migrations.AlterField(
            model_name='question',
            name='type',
            field=models.CharField(choices=[('text', 'text (multiple line)'), ('short-text', 'short text (one line)'), ('radio', 'radio'), ('select', 'select'), ('select-multiple', 'Select Multiple'), ('select_image', 'Select Image'), ('integer', 'integer'), ('float', 'float'), ('date', 'date'), ('time', 'time')], default='text', max_length=200, verbose_name='Type'),
        ),
        migrations.CreateModel(
            name='SurveyProtocolLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clinical_site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='survey_links', to='survey.clinicalsite')),
                ('protocol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='survey_links', to='survey.protocol')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='protocol_links', to='survey.survey')),
            ],
            options={
                'verbose_name': 'survey protocol link',
                'verbose_name_plural': 'survey protocol links',
                'unique_together': {('survey', 'protocol', 'clinical_site')},
            },
        ),
    ]
