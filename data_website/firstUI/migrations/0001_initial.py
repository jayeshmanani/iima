# Generated by Django 3.1.1 on 2020-10-12 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Countries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_name', models.CharField(max_length=100)),
                ('country_id', models.CharField(max_length=10)),
                ('country_code', models.CharField(max_length=10)),
                ('default_hist', models.IntegerField()),
                ('region', models.CharField(max_length=100)),
            ],
        ),
    ]
