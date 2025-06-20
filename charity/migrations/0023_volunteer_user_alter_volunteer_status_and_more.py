# Generated by Django 5.1.4 on 2025-02-20 23:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charity', '0022_remove_donation_transaction_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteer',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='volunteer',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved')], default='Pending', max_length=50),
        ),
        migrations.AlterField(
            model_name='volunteer',
            name='volunteering_in',
            field=models.CharField(choices=[('HWH', 'Hospital Without Hunger'), ('EGA', 'Essential Grocery Assistance'), ('CHC', 'Comprehensive Home Care'), ('BAS', 'Beneficiary Aid & Support'), ('PCP', 'Palliative Care Program'), ('GC', 'Guidance & Counseling'), ('OTH', 'Others')], default='OTH', max_length=20),
        ),
    ]
