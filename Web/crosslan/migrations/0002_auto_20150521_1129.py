# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('crosslan', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RedeemCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=6, verbose_name=b'Redeem Code')),
                ('status', models.CharField(default=b'IN', max_length=2, choices=[(b'IN', b'Inactive'), (b'AC', b'Active'), (b'US', b'Code Used')])),
            ],
        ),
        migrations.AddField(
            model_name='crosslanuser',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 21, 3, 29, 8, 156000, tzinfo=utc), verbose_name=b'Last Update Time', auto_now=True),
            preserve_default=False,
        ),
    ]
