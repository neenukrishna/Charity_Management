# Generated by Django 5.1.4 on 2025-03-30 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charity', '0069_staff_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fielddata',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Solved', 'Solved')], default='Pending', max_length=50),
        ),
    ]
