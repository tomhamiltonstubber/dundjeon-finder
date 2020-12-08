# Generated by Django 3.1.4 on 2020-12-08 10:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.gamemaster'),
        ),
        migrations.AddField(
            model_name='game',
            name='players',
            field=models.ManyToManyField(blank=True, related_name='games', to=settings.AUTH_USER_MODEL),
        ),
    ]
