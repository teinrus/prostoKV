# Generated by Django 4.2 on 2023-06-15 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionOutput1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(verbose_name='Дата')),
                ('time', models.TimeField(verbose_name='Время')),
                ('production', models.IntegerField(verbose_name='Продукция линии')),
            ],
            options={
                'verbose_name_plural': 'Выпуск продукции линии 31',
            },
        ),
        migrations.CreateModel(
            name='ProductionOutput3',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(verbose_name='Дата')),
                ('time', models.TimeField(verbose_name='Время')),
                ('production', models.IntegerField(verbose_name='Продукция линии')),
            ],
            options={
                'verbose_name_plural': 'Выпуск продукции линии 31',
            },
        ),
        migrations.CreateModel(
            name='Table1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startdata', models.DateField(verbose_name='Дата начала простоя')),
                ('starttime', models.TimeField(verbose_name='Время начала простоя')),
                ('prostoy', models.TimeField(blank=True, null=True, verbose_name='Время простоя')),
                ('uchastok', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Где произошол простой')),
                ('prichina', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Причина')),
                ('otv_pod', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Ответственное подразделение')),
                ('comment', models.CharField(blank=True, default=' ', max_length=250, null=True, verbose_name='Комментарий')),
            ],
            options={
                'verbose_name_plural': 'Простои 31 линии',
            },
        ),
        migrations.CreateModel(
            name='Table3',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startdata', models.DateField(verbose_name='Дата начала простоя')),
                ('starttime', models.TimeField(verbose_name='Время начала простоя')),
                ('prostoy', models.TimeField(blank=True, null=True, verbose_name='Время простоя')),
                ('uchastok', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Где произошол простой')),
                ('prichina', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Причина')),
                ('otv_pod', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Ответственное подразделение')),
                ('comment', models.CharField(blank=True, default=' ', max_length=250, null=True, verbose_name='Комментарий')),
            ],
            options={
                'verbose_name_plural': 'Простои 31 линии',
            },
        ),
        migrations.CreateModel(
            name='Table33',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startdata', models.DateField(verbose_name='Дата начала простоя')),
                ('starttime', models.TimeField(verbose_name='Время начала простоя')),
                ('prostoy', models.TimeField(blank=True, null=True, verbose_name='Время простоя')),
                ('uchastok', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Где произошол простой')),
                ('prichina', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Причина')),
                ('otv_pod', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Ответственное подразделение')),
                ('comment', models.CharField(blank=True, default=' ', max_length=250, null=True, verbose_name='Комментарий')),
            ],
            options={
                'verbose_name_plural': 'Простои 33 линии',
            },
        ),
    ]
