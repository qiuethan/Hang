# Generated by Django 4.1.3 on 2023-05-11 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_alter_profile_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.CharField(default='/static/media/logo.76ffd1144b342263116b472f0c0cff50.svg', max_length=2000),
        ),
    ]