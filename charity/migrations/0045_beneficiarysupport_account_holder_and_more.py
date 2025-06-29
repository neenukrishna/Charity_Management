# Generated by Django 5.1.4 on 2025-03-09 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charity', '0044_fielddata_additional_info_fielddata_age_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='beneficiarysupport',
            name='account_holder',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='beneficiarysupport',
            name='account_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='beneficiarysupport',
            name='bank_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='beneficiarysupport',
            name='disbursement_method',
            field=models.CharField(blank=True, choices=[('bank_transfer', 'Direct Bank Transfer'), ('cash_pickup', 'Cash Pickup')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='beneficiarysupport',
            name='ifsc_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
