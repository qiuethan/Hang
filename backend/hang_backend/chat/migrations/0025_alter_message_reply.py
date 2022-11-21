# Generated by Django 4.1.3 on 2022-11-12 17:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0024_message_reply'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='reply',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='chat.message'),
        ),
    ]