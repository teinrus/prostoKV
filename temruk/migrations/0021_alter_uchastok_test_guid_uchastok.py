# Generated by Django 4.2 on 2023-12-22 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('temruk', '0020_prichina_test_uchastok_test'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uchastok_test',
            name='Guid_Uchastok',
            field=models.CharField(blank=True, default='Не определено', max_length=36, null=True, verbose_name='Guid участок'),
        ),
    ]
