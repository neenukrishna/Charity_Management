# Generated by Django 5.1.4 on 2025-03-28 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charity', '0061_alter_notification_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='group',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
