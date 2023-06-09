# Generated by Django 4.2 on 2023-05-23 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('temruk', '0006_alter_tabletest_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='speed2',
            name='speed',
        ),
        migrations.AddField(
            model_name='speed2',
            name='depal',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость депалитизатор'),
        ),
        migrations.AddField(
            model_name='speed2',
            name='eticetka',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость этикетки'),
        ),
        migrations.AddField(
            model_name='speed2',
            name='kapsula',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость капсулятора'),
        ),
        migrations.AddField(
            model_name='speed2',
            name='muzle',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость мюзле'),
        ),
        migrations.AddField(
            model_name='speed2',
            name='termotunel',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость термотунеля'),
        ),
        migrations.AddField(
            model_name='speed2',
            name='triblok',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость триблока'),
        ),
        migrations.AddField(
            model_name='speed2',
            name='ukladchik',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость укладчика'),
        ),
        migrations.AddField(
            model_name='speed2',
            name='zakleichik',
            field=models.IntegerField(blank=True, default=0.0, null=True, verbose_name='Скорость заклейщика'),
        ),
    ]
