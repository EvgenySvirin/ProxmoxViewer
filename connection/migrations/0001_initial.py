# Generated by Django 4.2.dev20221230122847 on 2023-01-12 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(max_length=200)),
                ('backend', models.CharField(max_length=200)),
                ('service', models.CharField(max_length=200)),
                ('user', models.CharField(max_length=200)),
                ('password', models.CharField(max_length=200)),
                ('verify_ssl', models.BooleanField(max_length=200)),
                ('port', models.IntegerField()),
                ('date', models.DateField()),
            ],
        ),
    ]
