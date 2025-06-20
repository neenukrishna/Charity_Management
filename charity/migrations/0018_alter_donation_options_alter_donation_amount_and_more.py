# Generated by Django 5.1.4 on 2025-02-11 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charity', '0017_alter_volunteer_volunteering_in'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='donation',
            options={'ordering': ['-date_time']},
        ),
        migrations.AlterField(
            model_name='donation',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Enter the amount for monetary donations.', max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='donation',
            name='donation_details',
            field=models.TextField(help_text='Enter the donation details.'),
        ),
        migrations.AlterField(
            model_name='donation',
            name='donation_type',
            field=models.CharField(choices=[('monetary', 'Monetary'), ('goods', 'Goods')], help_text='Select the type of donation.', max_length=100),
        ),
        migrations.AlterField(
            model_name='donation',
            name='quantity',
            field=models.IntegerField(blank=True, help_text='Enter the quantity (for non-monetary donations).', null=True),
        ),
        migrations.AlterField(
            model_name='donation',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', help_text='Donation status.', max_length=50),
        ),
    ]
