# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crosslan', '0004_auto_20150524_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crosslanuser',
            name='data',
            field=models.IntegerField(default=200000000, verbose_name=b'Data Balance'),
        ),
        migrations.AlterField(
            model_name='redeemcode',
            name='status',
            field=models.CharField(default=b'IN', max_length=2, choices=[(b'IN', b'Inactive'), (b'AC', b'Active'), (b'US', b'Code Used'), (b'SP', b'Special')]),
        ),
    ]
