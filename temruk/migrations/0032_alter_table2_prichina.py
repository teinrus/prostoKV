# Generated by Django 4.2 on 2024-03-14 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('temruk', '0031_productiontime2_productiontime4'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table2',
            name='prichina',
            field=models.CharField(blank=True, default='', max_length=70, null=True, verbose_name='Причина'),
        ),
    ]
