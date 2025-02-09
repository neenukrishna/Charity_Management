from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('charity', '0014_alter_volunteer_availability_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteer',
            name='availability_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='volunteer',
            name='volunteering_in',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('HWH', 'Hospital Without Hunger'),
                    ('EGA', 'Essential Grocery Assistance'),
                    ('CHC', 'Comprehensive Home Care'),
                    ('BAS', 'Beneficiary Aid & Support'),
                    ('PCP', 'Palliative Care Program'),
                    ('GC', 'Guidance & Counseling'),
                ],
                default='HWH'
            ),
        ),
    ]
