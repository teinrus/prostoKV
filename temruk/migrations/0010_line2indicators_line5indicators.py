# Generated by Django 4.2 on 2023-09-05 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('temruk', '0009_delete_bottleexplosion'),
    ]

    operations = [
        migrations.CreateModel(
            name='Line2Indicators',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(verbose_name='Дата')),
                ('time', models.TimeField(verbose_name='Время')),
                ('napTemp', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Температура напорника')),
                ('napPress', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Давление напорника')),
            ],
            options={
                'verbose_name_plural': 'Показатели линии 2',
            },
        ),
        migrations.CreateModel(
            name='Line5Indicators',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(verbose_name='Дата')),
                ('time', models.TimeField(verbose_name='Время')),
                ('napTemp', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Температура напорника')),
                ('napPress', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Давление напорника')),
            ],
            options={
                'verbose_name_plural': 'Показатели линии 5',
            },
        ),
    ]
