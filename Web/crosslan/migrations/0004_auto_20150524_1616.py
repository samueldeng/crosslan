# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crosslan', '0003_auto_20150524_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crosslanuser',
            name='host',
            field=models.CharField(default=b'202.117.15.79', max_length=20, verbose_name=b'Proxy Address'),
        ),
        migrations.AlterField(
            model_name='crosslanuser',
            name='port',
            field=models.IntegerField(unique=True, verbose_name=b'Proxy Port'),
        ),
    ]
