# Generated by Django 4.1.3 on 2023-04-16 14:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hang_events', '0015_delete_archivedhangevent_archivedhangevent'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ArchivedHangEvent',
        ),
    ]