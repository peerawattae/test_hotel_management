# Generated by Django 5.1.3 on 2024-11-26 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_room_room_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_number',
            field=models.CharField(default='000', max_length=10, null=True, unique=True),
        ),
    ]
