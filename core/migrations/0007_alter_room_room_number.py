# Generated by Django 5.1.3 on 2024-11-26 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_room_room_number_alter_payment_booking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_number',
            field=models.CharField(default='000', max_length=10, unique=True),
        ),
    ]
