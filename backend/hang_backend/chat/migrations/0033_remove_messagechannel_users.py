# Generated by Django 4.1.3 on 2023-01-19 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0032_messagechannelusers_messagechannel_users_temp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='messagechannel',
            name='users',
        ),
    ]