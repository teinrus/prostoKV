# Generated by Django 4.2 on 2024-02-21 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titorovka', '0016_alter_table31_uchastok_alter_table33_uchastok'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table31',
            name='prichina',
            field=models.CharField(blank=True, default='', max_length=70, null=True, verbose_name='Причина'),
        ),
    ]
