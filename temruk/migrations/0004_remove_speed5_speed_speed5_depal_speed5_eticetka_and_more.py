# Generated by Django 4.2 on 2023-05-11 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('temruk', '0003_remove_speed4_speed_speed4_depal_speed4_eticetka_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='speed5',
            name='speed',
        ),
        migrations.AddField(
            model_name='speed5',
            name='depal',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость депалитизатор'),
        ),
        migrations.AddField(
            model_name='speed5',
            name='eticetka',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость этикетки'),
        ),
        migrations.AddField(
            model_name='speed5',
            name='kapsula',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость капсулятора'),
        ),
        migrations.AddField(
            model_name='speed5',
            name='muzle',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость мюзле'),
        ),
        migrations.AddField(
            model_name='speed5',
            name='termotunel',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость термотунеля'),
        ),
        migrations.AddField(
            model_name='speed5',
            name='triblok',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость триблока'),
        ),
        migrations.AddField(
            model_name='speed5',
            name='ukladchik',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость укладчика'),
        ),
        migrations.AddField(
            model_name='speed5',
            name='zakleichik',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость заклейщика'),
        ),
    ]
