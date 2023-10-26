# Generated by Django 4.2 on 2023-10-16 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('temruk', '0018_co2_kupaj'),
    ]

    operations = [
        migrations.CreateModel(
            name='Filter2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(verbose_name='Дата')),
                ('time', models.TimeField(verbose_name='Время')),
                ('press1', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Давление 1 ступени')),
                ('press2', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Давление 2 ступени')),
            ],
            options={
                'verbose_name_plural': 'Давление микрофилтрации линия 2',
            },
        ),
        migrations.CreateModel(
            name='Filter4',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(verbose_name='Дата')),
                ('time', models.TimeField(verbose_name='Время')),
                ('press1', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Давление 1 ступени')),
                ('press2', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Давление 2 ступени')),
            ],
            options={
                'verbose_name_plural': 'Давление микрофилтрации линия 4',
            },
        ),
        migrations.CreateModel(
            name='Filter5',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(verbose_name='Дата')),
                ('time', models.TimeField(verbose_name='Время')),
                ('press1', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Давление 1 ступени')),
                ('press2', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Давление 2 ступени')),
            ],
            options={
                'verbose_name_plural': 'Давление микрофилтрации линия 5',
            },
        ),
    ]
