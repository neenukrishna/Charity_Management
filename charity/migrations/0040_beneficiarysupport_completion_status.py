# Generated by Django 5.1.4 on 2025-03-08 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charity', '0039_palliativepatient_volunteer'),
    ]

    operations = [
        migrations.AddField(
            model_name='beneficiarysupport',
            name='completion_status',
            field=models.CharField(default='Pending', max_length=20),
        ),
    ]
