# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0003_game_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('code', models.CharField(max_length=4)),
                ('color', models.CharField(choices=[('red', 'Red'), ('blue', 'Blue'), ('teal', 'Teal'), ('purple', 'Purple'), ('yellow', 'Yellow'), ('orange', 'Orange'), ('green', 'Green'), ('pink', 'Pink')], max_length=6)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
