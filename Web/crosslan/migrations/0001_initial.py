# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='BindingIP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.CharField(max_length=20, verbose_name=b'Client IP binding to User')),
            ],
        ),
        migrations.CreateModel(
            name='CrossLanUser',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('host', models.CharField(max_length=20, verbose_name=b'Proxy Address')),
                ('port', models.IntegerField(default=0, verbose_name=b'Proxy Port')),
                ('data', models.IntegerField(default=0, verbose_name=b'Data Balance')),
                ('bind', models.BooleanField(default=False, verbose_name=b'Bind or Not')),
            ],
        ),
        migrations.AddField(
            model_name='bindingip',
            name='user',
            field=models.ForeignKey(verbose_name=b'The User binding to', to='crosslan.CrossLanUser'),
        ),
    ]
