from django.db import models


class Table31(models.Model):
    startdata = models.DateField('Дата начала простоя')
    starttime = models.TimeField('Время начала простоя')
    prostoy = models.TimeField('Время простоя', blank=True, null=True)

    uchastok = models.CharField('Где произошол простой', max_length=100, default='', blank=True, null=True)
    prichina = models.CharField('Причина', max_length=70, default='', blank=True, null=True)
    otv_pod = models.CharField('Ответственное подразделение', max_length=50, default='', blank=True,
                               null=True)
    comment = models.CharField('Комментарий', max_length=250, default=' ', blank=True, null=True)

    Guid_Prichina = models.CharField('Guid причины', max_length=36, default='Не определено', blank=True, null=True)
    Guid_Uchastok = models.CharField('Guid участок', max_length=36, default='Не определено', blank=True, null=True)

    def __str__(self):
        return str(self.startdata) + '_' + str(self.starttime) + '_' + str(self.id)

    class Meta:
        verbose_name_plural = "Простои 31 линии"


class Table33(models.Model):
    startdata = models.DateField('Дата начала простоя')
    starttime = models.TimeField('Время начала простоя')
    prostoy = models.TimeField('Время простоя', blank=True, null=True)

    uchastok = models.CharField('Где произошол простой', max_length=100, default='', blank=True, null=True)
    prichina = models.CharField('Причина', max_length=50, default='', blank=True, null=True)
    otv_pod = models.CharField('Ответственное подразделение', max_length=50, default='', blank=True,
                               null=True)
    comment = models.CharField('Комментарий', max_length=250, default=' ', blank=True, null=True)

    Guid_Prichina = models.CharField('Guid причины', max_length=36, default='Не определено', blank=True, null=True)
    Guid_Uchastok = models.CharField('Guid участок', max_length=36, default='Не определено', blank=True, null=True)

    def __str__(self):
        return str(self.startdata) + '_' + str(self.starttime) + '_' + str(self.id)

    class Meta:
        verbose_name_plural = "Простои 33 линии"


class Table24(models.Model):
    startdata = models.DateField('Дата начала простоя')
    starttime = models.TimeField('Время начала простоя')
    prostoy = models.TimeField('Время простоя', blank=True, null=True)

    uchastok = models.CharField('Где произошол простой', max_length=50, default='', blank=True, null=True)
    prichina = models.CharField('Причина', max_length=50, default='', blank=True, null=True)
    otv_pod = models.CharField('Ответственное подразделение', max_length=50, default='', blank=True,
                               null=True)
    comment = models.CharField('Комментарий', max_length=250, default=' ', blank=True, null=True)

    def __str__(self):
        return str(self.startdata) + '_' + str(self.starttime) + '_' + str(self.id)

    Guid_Prichina = models.CharField('Guid причины', max_length=36, default='Не определено', blank=True, null=True)
    Guid_Uchastok = models.CharField('Guid участок', max_length=36, default='Не определено', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Простои 24 линии"


class Table25(models.Model):
    startdata = models.DateField('Дата начала простоя')
    starttime = models.TimeField('Время начала простоя')
    prostoy = models.TimeField('Время простоя', blank=True, null=True)

    uchastok = models.CharField('Где произошол простой', max_length=50, default='', blank=True, null=True)
    prichina = models.CharField('Причина', max_length=50, default='', blank=True, null=True)
    otv_pod = models.CharField('Ответственное подразделение', max_length=50, default='', blank=True,
                               null=True)
    comment = models.CharField('Комментарий', max_length=250, default=' ', blank=True, null=True)

    Guid_Prichina = models.CharField('Guid причины', max_length=36, default='Не определено', blank=True, null=True)
    Guid_Uchastok = models.CharField('Guid участок', max_length=36, default='Не определено', blank=True, null=True)
    def __str__(self):
        return str(self.startdata) + '_' + str(self.starttime) + '_' + str(self.id)

    class Meta:
        verbose_name_plural = "Простои 25 линии"


class Table26(models.Model):
    startdata = models.DateField('Дата начала простоя')
    starttime = models.TimeField('Время начала простоя')
    prostoy = models.TimeField('Время простоя', blank=True, null=True)

    uchastok = models.CharField('Где произошол простой', max_length=50, default='', blank=True, null=True)
    prichina = models.CharField('Причина', max_length=50, default='', blank=True, null=True)
    otv_pod = models.CharField('Ответственное подразделение', max_length=50, default='', blank=True,
                               null=True)
    comment = models.CharField('Комментарий', max_length=250, default=' ', blank=True, null=True)

    Guid_Prichina = models.CharField('Guid причины', max_length=36, default='Не определено', blank=True, null=True)
    Guid_Uchastok = models.CharField('Guid участок', max_length=36, default='Не определено', blank=True, null=True)

    def __str__(self):
        return str(self.startdata) + '_' + str(self.starttime) + '_' + str(self.id)

    class Meta:
        verbose_name_plural = "Простои 26 линии"


class Speed31(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    depal = models.IntegerField('Скорость депалитизатор', default=0.0, blank=True, null=True)
    triblok = models.IntegerField('Скорость триблок', default=0.0, blank=True, null=True)
    kapsula = models.IntegerField('Скорость капсулятора', default=0.0, blank=True, null=True)
    eticetka = models.IntegerField('Скорость этикетки', default=0.0, blank=True, null=True)
    ukladchik = models.IntegerField('Скорость укладчика', default=0.0, blank=True, null=True)
    zakleichik = models.IntegerField('Скорость заклейщика', default=0.0, blank=True, null=True)


    def __str__(self):
        return str(self.data) + " " + str(self.time)

    class Meta:
        verbose_name_plural = "Производительность линии 31"


class Speed33(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    depal = models.IntegerField('Скорость депалитизатор', default=0.0, blank=True, null=True)
    triblok = models.IntegerField('Скорость триблок', default=0.0, blank=True, null=True)
    kapsula = models.IntegerField('Скорость капсулятора', default=0.0, blank=True, null=True)
    eticetka = models.IntegerField('Скорость этикетки', default=0.0, blank=True, null=True)
    ukladchik = models.IntegerField('Скорость укладчика', default=0.0, blank=True, null=True)
    zakleichik = models.IntegerField('Скорость заклейщика', default=0.0, blank=True, null=True)


    def __str__(self):
        return str(self.data) + " " + str(self.time)

    class Meta:
        verbose_name_plural = "Производительность линии 33"


class Speed24(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    depal = models.IntegerField('Скорость депалитизатор', default=0.0, blank=True, null=True)
    triblok = models.IntegerField('Скорость триблок', default=0.0, blank=True, null=True)
    kapsula = models.IntegerField('Скорость капсулятора', default=0.0, blank=True, null=True)
    eticetka = models.IntegerField('Скорость этикетки', default=0.0, blank=True, null=True)
    ukladchik = models.IntegerField('Скорость укладчика', default=0.0, blank=True, null=True)
    zakleichik = models.IntegerField('Скорость заклейщика', default=0.0, blank=True, null=True)


    def __str__(self):
        return str(self.data) + " " + str(self.time)

    class Meta:
        verbose_name_plural = "Производительность линии 24"


class Speed25(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    depal = models.IntegerField('Скорость депалитизатор', default=0.0, blank=True, null=True)
    triblok = models.IntegerField('Скорость триблок', default=0.0, blank=True, null=True)
    kapsula = models.IntegerField('Скорость капсулятора', default=0.0, blank=True, null=True)
    eticetka = models.IntegerField('Скорость этикетки', default=0.0, blank=True, null=True)
    ukladchik = models.IntegerField('Скорость укладчика', default=0.0, blank=True, null=True)
    zakleichik = models.IntegerField('Скорость заклейщика', default=0.0, blank=True, null=True)


    def __str__(self):
        return str(self.data) + " " + str(self.time)

    class Meta:
        verbose_name_plural = "Производительность линии 25"


class Speed26(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    depal = models.IntegerField('Скорость депалитизатор', default=0.0, blank=True, null=True)
    triblok = models.IntegerField('Скорость триблок', default=0.0, blank=True, null=True)
    kapsula = models.IntegerField('Скорость капсулятора', default=0.0, blank=True, null=True)
    eticetka = models.IntegerField('Скорость этикетки', default=0.0, blank=True, null=True)
    ukladchik = models.IntegerField('Скорость укладчика', default=0.0, blank=True, null=True)
    zakleichik = models.IntegerField('Скорость заклейщика', default=0.0, blank=True, null=True)


    def __str__(self):
        return str(self.data) + " " + str(self.time)

    class Meta:
        verbose_name_plural = "Производительность линии 26"


class ProductionOutput31(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    production = models.IntegerField('Продукция линии')

    def __str__(self):
        return str(self.time)

    class Meta:
        verbose_name_plural = "Выпуск продукции линии 31"


class ProductionOutput33(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    production = models.IntegerField('Продукция линии')

    def __str__(self):
        return str(self.time)

    class Meta:
        verbose_name_plural = "Выпуск продукции линии 33"


class ProductionOutput24(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    production = models.IntegerField('Продукция линии')

    def __str__(self):
        return str(self.time)

    class Meta:
        verbose_name_plural = "Выпуск продукции линии 24"


class ProductionOutput25(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    production = models.IntegerField('Продукция линии')

    def __str__(self):
        return str(self.time)

    class Meta:
        verbose_name_plural = "Выпуск продукции линии 25"


class ProductionOutput26(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    production = models.IntegerField('Продукция линии')

    def __str__(self):
        return str(self.time)

    class Meta:
        verbose_name_plural = "Выпуск продукции линии 26"


class ProductionTime31(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    type_bottle = models.CharField('Тип бутылки', max_length=150, default='', blank=True, null=True)

    def __str__(self):
        return str(self.time)

    class Meta:
        verbose_name_plural = "Время работы на бутылке 31"



class ProductionTime33(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    type_bottle = models.CharField('Тип бутылки', max_length=150, default='', blank=True, null=True)

    def __str__(self):
        return str(self.time)

    class Meta:
        verbose_name_plural = "Время работы на бутылке 33"
class ProductionTime24(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    type_bottle = models.CharField('Тип бутылки', max_length=150, default='', blank=True, null=True)

    def __str__(self):
        return str(self.time)

    class Meta:
        verbose_name_plural = "Время работы на бутылке 24"
class ProductionTime25(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    type_bottle = models.CharField('Тип бутылки', max_length=150, default='', blank=True, null=True)

    def __str__(self):
        return str(self.time)

    class Meta:
        verbose_name_plural = "Время работы на бутылке 25"

class ProductionTime26(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    type_bottle = models.CharField('Тип бутылки', max_length=150, default='', blank=True, null=True)

    def __str__(self):
        return str(self.time)

    class Meta:
        verbose_name_plural = "Время работы на бутылке 26"
