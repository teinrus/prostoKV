# Generated by Django 4.2 on 2024-02-27 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('temruk', '0025_table2_guid_prichina_table2_guid_uchastok_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SetProductionSpeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_bottle', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Тип бутылки')),
                ('line', models.IntegerField(verbose_name='Скорость')),
                ('speed', models.IntegerField(verbose_name='Скорость')),
            ],
            options={
                'verbose_name_plural': 'Установленная скорость по типу бутылки',
            },
        ),
    ]
