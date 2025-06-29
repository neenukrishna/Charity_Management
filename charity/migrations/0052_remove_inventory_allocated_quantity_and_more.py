# Generated by Django 5.1.4 on 2025-03-23 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charity', '0051_remove_inventory_allocated_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventory',
            name='allocated_quantity',
        ),
        migrations.AddField(
            model_name='inventory',
            name='allocated',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
    ]
