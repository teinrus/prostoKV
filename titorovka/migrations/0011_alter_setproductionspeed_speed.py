# Generated by Django 4.2 on 2023-11-28 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titorovka', '0010_alter_setproductionspeed_nameproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setproductionspeed',
            name='speed',
            field=models.IntegerField(null=True, verbose_name='Скорость'),
        ),
    ]