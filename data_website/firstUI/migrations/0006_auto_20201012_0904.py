# Generated by Django 3.1.1 on 2020-10-12 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firstUI', '0005_auto_20201012_0853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='default_hist',
            field=models.BooleanField(default=0),
        ),
    ]
