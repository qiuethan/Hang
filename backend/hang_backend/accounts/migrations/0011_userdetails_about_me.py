# Generated by Django 4.1.3 on 2023-04-05 02:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_emailauthtoken_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdetails',
            name='about_me',
            field=models.TextField(default=''),
        ),
    ]