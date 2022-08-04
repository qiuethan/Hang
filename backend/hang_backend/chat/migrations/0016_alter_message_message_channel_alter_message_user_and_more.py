# Generated by Django 4.0.6 on 2022-07-26 02:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0015_messagechannel_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='message_channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.messagechannel'),
        ),
        migrations.AlterField(
            model_name='message',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_channels', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='messagechannel',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_channels_owned', to=settings.AUTH_USER_MODEL),
        ),
    ]