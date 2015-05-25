# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crosslan', '0002_auto_20150521_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crosslanuser',
            name='host',
            field=models.CharField(default=b'127.0.0.1', max_length=20, verbose_name=b'Proxy Address'),
        ),
        migrations.AlterField(
            model_name='crosslanuser',
            name='port',
            field=models.IntegerField(default=10000, verbose_name=b'Proxy Port'),
        ),
        migrations.AlterField(
            model_name='redeemcode',
            name='code',
            field=models.CharField(unique=True, max_length=6, verbose_name=b'Redeem Code'),
        ),
    ]
