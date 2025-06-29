# Generated by Django 5.1.4 on 2025-02-09 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charity', '0016_add_missing_volunteer_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volunteer',
            name='volunteering_in',
            field=models.CharField(choices=[('HWH', 'Hospital Without Hunger'), ('EGA', 'Essential Grocery Assistance'), ('CHC', 'Comprehensive Home Care'), ('BAS', 'Beneficiary Aid & Support'), ('PCP', 'Palliative Care Program'), ('GC', 'Guidance & Counseling')], default=True, max_length=20),
        ),
    ]
