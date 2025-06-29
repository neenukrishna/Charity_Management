# Generated by Django 5.1.4 on 2025-03-02 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charity', '0034_alter_donation_status_alter_payment_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed')], default='Pending', help_text='Donation status.', max_length=50),
        ),
    ]
