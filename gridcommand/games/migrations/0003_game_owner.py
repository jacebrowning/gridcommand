# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('games', '0002_game_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='owner',
            field=models.ForeignKey(default='admin', to=settings.AUTH_USER_MODEL, related_name='games'),
            preserve_default=False,
        ),
    ]
