# Generated by Django 4.2.dev20221230122847 on 2023-02-07 15:57

import connection.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('connection', '0002_userconnection'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userconnection',
            name='connection_id',
        ),
        migrations.AddField(
            model_name='userconnection',
            name='connection',
            field=models.ForeignKey(default=connection.models.Connection.get_default_pk, on_delete=django.db.models.deletion.CASCADE, to='connection.connection'),
        ),
    ]
