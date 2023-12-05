from django.db import models


# Общиие показатели
class prichina(models.Model):
    key = models.CharField('Подразделение', max_length=50, default='Не определено', blank=True, null=True)
    prichina = models.CharField('Причина', max_length=50, default='Не определена', blank=True, null=True)

    def __str__(self):
        return str(self.prichina)

    class Meta:
        verbose_name_plural = "Причина простоя"


class uchastok(models.Model):
    uchastok = models.CharField('Где произошол простой', max_length=50, default='Не определено', blank=True, null=True)

    def __str__(self):
        return str(self.uchastok)

    class Meta:
        verbose_name_plural = "Участок линии"


# 1С
class bottling_plan(models.Model):
    Registrar = models.CharField('Регистратор', max_length=50, default='', blank=True, null=True)
    GUIDDocument = models.CharField('GUIDDocument', max_length=36, default='', blank=True, null=True)

    Data = models.DateField('Дата')

    GIUDLine = models.CharField('GIUDLine', max_length=36, default='', blank=True, null=True)

    ShiftNumber = models.IntegerField('Номер смены')

    GUIDNomenсlature = models.CharField('GUIDNomenсlature', max_length=36, default=' ', blank=True, null=True)

    Quantity = models.IntegerField('Количество')

    def __str__(self):
        return str(self.Data) + '_' + str(self.GIUDLine)

    class Meta:
        verbose_name_plural = "План розлива"


class Nomenclature(models.Model):
    GUID = models.CharField('GUID', max_length=36)
    Nomenclature = models.CharField('Номенклатура', max_length=150)
    GroupProduction = models.CharField('Группа продуктов', max_length=150)

    def __str__(self):
        return str(self.Nomenclature)

    class Meta:
        verbose_name_plural = "Номенклатура"


class Line(models.Model):
    GUID = models.CharField('GUID', max_length=36)
    Line = models.CharField('Название линии', max_length=50)
    Podrazdelenie = models.CharField('Подразделение', max_length=150)
    PodrazdeleniePloshadka = models.CharField('ПодразделениеПлощадка', max_length=150)
    NomerLine = models.IntegerField('Номер линии')

    def __str__(self):
        return str(self.Line) + " " + str(self.GUID)

    class Meta:
        verbose_name_plural = "Линии"


# Таблицы по линиям

class Table5(models.Model):
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

    class Meta:
        verbose_name_plural = "Простои 5 линии"


class Table2(models.Model):
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

    class Meta:
        verbose_name_plural = "Простои 2 линии"


class Table4(models.Model):
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

    class Meta:
        verbose_name_plural = "Простои 4 линии"


class Speed5(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    depal = models.IntegerField('Скорость депалитизатор', default=0.0, blank=True, null=True)
    triblok = models.IntegerField('Скорость триблока', default=0.0, blank=True, null=True)
    muzle = models.IntegerField('Скорость мюзле', default=0.0, blank=True, null=True)
    termotunel = models.IntegerField('Скорость термотунеля', default=0.0, blank=True, null=True)
    kapsula = models.IntegerField('Скорость капсулятора', default=0.0, blank=True, null=True)
    eticetka = models.IntegerField('Скорость этикетки', default=0.0, blank=True, null=True)
    ukladchik = models.IntegerField('Скорость укладчика', default=0.0, blank=True, null=True)
    zakleichik = models.IntegerField('Скорость заклейщика', default=0.0, blank=True, null=True)

    def __str__(self):
        return str(self.time) + " " + str(self.id)

    class Meta:
        verbose_name_plural = "Производительность линии 5"


class CO2_Rozliv(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    volume = models.FloatField('Обьем', default=0.0, blank=True, null=True)

    def __str__(self):
        return str(self.time) + " " + str(self.id)

    class Meta:
        verbose_name_plural = "CO2 Розлив"


class CO2_Kupaj(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    volume = models.FloatField('Обьем', default=0.0, blank=True, null=True)

    def __str__(self):
        return str(self.time) + " " + str(self.id)

    class Meta:
        verbose_name_plural = "CO2 Купахный"


class Filter2(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    press1 = models.FloatField('Давление 1 ступени', default=0.0, blank=True, null=True)
    press2 = models.FloatField('Давление 2 ступени', default=0.0, blank=True, null=True)

    def __str__(self):
        return str(self.time) + " " + str(self.id)

    class Meta:
        verbose_name_plural = "Давление микрофилтрации линия 2"


class Filter4(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    press1 = models.FloatField('Давление 1 ступени', default=0.0, blank=True, null=True)
    press2 = models.FloatField('Давление 2 ступени', default=0.0, blank=True, null=True)

    def __str__(self):
        return str(self.time) + " " + str(self.id)

    class Meta:
        verbose_name_plural = "Давление микрофилтрации линия 4"


class Filter5(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    press1 = models.FloatField('Давление 1 ступени', default=0.0, blank=True, null=True)
    press2 = models.FloatField('Давление 2 ступени', default=0.0, blank=True, null=True)

    def __str__(self):
        return str(self.time) + " " + str(self.id)

    class Meta:
        verbose_name_plural = "Давление микрофилтрации линия 5"


class Speed2(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    depal = models.IntegerField('Скорость депалитизатор', default=0.0, blank=True, null=True)
    triblok = models.IntegerField('Скорость триблока', default=0.0, blank=True, null=True)
    muzle = models.IntegerField('Скорость мюзле', default=0.0, blank=True, null=True)
    termotunel = models.IntegerField('Скорость термотунеля', default=0.0, blank=True, null=True)
    kapsula = models.IntegerField('Скорость капсулятора', default=0.0, blank=True, null=True)
    eticetka = models.IntegerField('Скорость этикетки', default=0.0, blank=True, null=True)
    ukladchik = models.IntegerField('Скорость укладчика', default=0.0, blank=True, null=True)
    zakleichik = models.IntegerField('Скорость заклейщика', default=0.0, blank=True, null=True)

    def __str__(self):
        return str(self.time) + " " + str(self.id)

    class Meta:
        verbose_name_plural = "Производительность линии 2"


class Speed4(models.Model):
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
        verbose_name_plural = "Производительность линии 4"


class bottleExplosion5(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    bottle = models.IntegerField('Взрыв')

    def __str__(self):
        return str(self.data) + '_' + str(self.time)

    class Meta:
        verbose_name_plural = "Взрывы бутылок"


class ProductionOutput2(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    production = models.IntegerField('Продукция линии')

    def __str__(self):
        return str(self.time) + " " + str(self.production)

    class Meta:
        verbose_name_plural = "Выпуск продукции линии 2"


class ProductionOutput4(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    production = models.IntegerField('Продукция линии')

    def __str__(self):
        return str(self.time) + " "+str(self.production)

    class Meta:
        verbose_name_plural = "Выпуск продукции линии 4"


class ProductionOutput1(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    production = models.IntegerField('Продукция линии')

    def __str__(self):
        return str(self.time)

    class Meta:
        verbose_name_plural = "Выпуск продукции линии 1"


class ProductionOutput5(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')
    production = models.IntegerField('Продукция линии')

    def __str__(self):
        return str(self.production)

    class Meta:
        verbose_name_plural = "Выпуск продукции линии 5"


class NapAcratofori(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')

    acr62_temp = models.FloatField('Температура 62', default=0.0, blank=True, null=True)
    acr62_press = models.FloatField('Давление 62', default=0.0, blank=True, null=True)
    acr62_volume = models.FloatField('Обьем 62', default=0.0, blank=True, null=True)

    acr63_temp = models.FloatField('Температура 63', default=0.0, blank=True, null=True)
    acr63_press = models.FloatField('Давление 63', default=0.0, blank=True, null=True)
    acr63_volume = models.FloatField('Обьем 63', default=0.0, blank=True, null=True)

    acr64_temp = models.FloatField('Температура 64', default=0.0, blank=True, null=True)
    acr64_press = models.FloatField('Давление 64', default=0.0, blank=True, null=True)
    acr64_volume = models.FloatField('Обьем 64', default=0.0, blank=True, null=True)

    acr65_temp = models.FloatField('Температура 65', default=0.0, blank=True, null=True)
    acr65_press = models.FloatField('Давление 65', default=0.0, blank=True, null=True)
    acr65_volume = models.FloatField('Обьем 65', default=0.0, blank=True, null=True)

    acr66_temp = models.FloatField('Температура 66', default=0.0, blank=True, null=True)
    acr66_press = models.FloatField('Давление 66', default=0.0, blank=True, null=True)
    acr66_volume = models.FloatField('Обьем 66', default=0.0, blank=True, null=True)

    acr67_temp = models.FloatField('Температура 67', default=0.0, blank=True, null=True)
    acr67_press = models.FloatField('Давление 67', default=0.0, blank=True, null=True)
    acr67_volume = models.FloatField('Обьем 67', default=0.0, blank=True, null=True)

    acr68_temp = models.FloatField('Температура 68', default=0.0, blank=True, null=True)
    acr68_press = models.FloatField('Давление 68', default=0.0, blank=True, null=True)
    acr68_volume = models.FloatField('Обьем 68', default=0.0, blank=True, null=True)

    acr69_temp = models.FloatField('Температура 69', default=0.0, blank=True, null=True)
    acr69_press = models.FloatField('Давление 69', default=0.0, blank=True, null=True)
    acr69_volume = models.FloatField('Обьем 69', default=0.0, blank=True, null=True)

    acr70_temp = models.FloatField('Температура 70', default=0.0, blank=True, null=True)
    acr70_press = models.FloatField('Давление 70', default=0.0, blank=True, null=True)
    acr70_volume = models.FloatField('Обьем 70', default=0.0, blank=True, null=True)

    acr82_temp = models.FloatField('Температура 82 верх', default=0.0, blank=True, null=True)
    acr82_press = models.FloatField('Давление 82', default=0.0, blank=True, null=True)
    acr82_volume = models.FloatField('Обьем 82', default=0.0, blank=True, null=True)

    acr83_temp = models.FloatField('Температура 83 верх', default=0.0, blank=True, null=True)
    acr83_press = models.FloatField('Давление 83', default=0.0, blank=True, null=True)
    acr83_volume = models.FloatField('Обьем 83', default=0.0, blank=True, null=True)

    def __str__(self):
        return str(self.data) + str(self.time)

    class Meta:
        verbose_name_plural = "Напорные акратофоры"


class Line5Indicators(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')

    numbacr = models.IntegerField('Номер акратофора', default=0.0, blank=True, null=True)
    naptemp = models.FloatField('Температура напорника', default=0.0, blank=True, null=True)
    nappress = models.FloatField('Давление напорника', default=0.0, blank=True, null=True)

    def __str__(self):
        return str(self.data) + str(self.time)

    class Meta:
        verbose_name_plural = "Показатели линии 5"


class Line2Indicators(models.Model):
    data = models.DateField('Дата')
    time = models.TimeField('Время')

    numbacr = models.IntegerField('Номер акратофора', default=0.0, blank=True, null=True)
    naptemp = models.FloatField('Температура напорника', default=0.0, blank=True, null=True)
    nappress = models.FloatField('Давление напорника', default=0.0, blank=True, null=True)

    def __str__(self):
        return str(self.data) + str(self.time)

    class Meta:
        verbose_name_plural = "Показатели линии 2"
