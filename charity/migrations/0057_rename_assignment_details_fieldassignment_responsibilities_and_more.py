# Generated by Django 5.1.4 on 2025-03-27 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charity', '0056_task_patient'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fieldassignment',
            old_name='assignment_details',
            new_name='responsibilities',
        ),
        migrations.AddField(
            model_name='fieldassignment',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
