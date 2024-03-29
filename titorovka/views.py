import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
from pyModbusTCP.client import ModbusClient

from temruk.models import bottling_plan, prichina, uchastok, SetProductionSpeed
from temruk.views import vid_prostoev, time_to_timedelta, format_timedelta
# Create your views here.
from titorovka.models import Table31, ProductionOutput31, Speed31, Table33, Speed33, ProductionOutput33, Table24, \
    Speed24, Table26, Speed26, ProductionOutput24, ProductionOutput26, Speed25, Table25, ProductionOutput25, \
    ProductionTime33, ProductionTime31, ProductionTime24, ProductionTime25, ProductionTime26
from .forms import Otchet, OtchetIgr

start1 = datetime.time(8, 00, 0)
start2 = datetime.time(16, 00, 0)
start3 = datetime.time(23, 59, 0)

if start1 <= datetime.datetime.now().time() <= start2:
    startSmena = datetime.time(8, 00, 0)
    spotSmena = datetime.time(16, 00, 0)
elif start2 <= datetime.datetime.now().time() <= start3:
    startSmena = datetime.time(16, 00, 0)
    spotSmena = datetime.time(23, 59, 0)
else:
    startSmena = datetime.time(00, 00, 00)
    spotSmena = datetime.time(8, 00, 00)


def mod_bus(reg, bit_temp):
    slave_address = '10.36.20.2'

    unit_id = 1
    modbus_client = ModbusClient(host=slave_address, unit_id=unit_id, auto_open=True)
    test = modbus_client.write_single_register(reg, bit_temp)


def mod_bus_igristoe(reg, bit_temp):
    slave_address = '10.36.20.4'

    unit_id = 1
    modbus_client = ModbusClient(host=slave_address, unit_id=unit_id, auto_open=True)
    test = modbus_client.write_single_register(reg, bit_temp)


# функция формирования процентов за текущию смену
def proc(startSmena, spotSmena, plan, colProduct):
    today = datetime.date.today()
    # количество продукции вып в сек
    d_start1 = datetime.datetime.combine(today, startSmena)
    d_end1 = datetime.datetime.combine(today, spotSmena)
    diff1 = d_end1 - d_start1
    planProdSec = int(plan / int(diff1.total_seconds()))

    # количество времени которое прошло
    d_start2 = datetime.datetime.combine(today, startSmena)
    d_end2 = datetime.datetime.combine(today, datetime.datetime.now().time())
    diff2 = d_end2 - d_start2

    # проц вып продукции
    return int(colProduct / ((int(diff2.total_seconds()) * planProdSec) / 100))


def index(request):
    if request.method == 'GET':
        table31 = Table31.objects.filter(startdata=datetime.date.today(),
                                         starttime__gte=startSmena,
                                         starttime__lte=spotSmena)
        speed31 = Speed31.objects.filter(data=datetime.date.today(),
                                         time__gte=startSmena,
                                         time__lte=spotSmena)
        table33 = Table33.objects.filter(startdata=datetime.date.today(),
                                         starttime__gte=startSmena,
                                         starttime__lte=spotSmena)
        speed33 = Speed33.objects.filter(data=datetime.date.today(),
                                         time__gte=startSmena,
                                         time__lte=spotSmena)
        table24 = Table24.objects.filter(startdata=datetime.date.today(),
                                         starttime__gte=startSmena,
                                         starttime__lte=spotSmena)
        speed24 = Speed24.objects.filter(data=datetime.date.today(),
                                         time__gte=startSmena,
                                         time__lte=spotSmena)
        table26 = Table26.objects.filter(startdata=datetime.date.today(),
                                         starttime__gte=startSmena,
                                         starttime__lte=spotSmena)
        speed26 = Speed26.objects.filter(data=datetime.date.today(),
                                         time__gte=startSmena,
                                         time__lte=spotSmena)
        table25 = Table25.objects.filter(startdata=datetime.date.today(),
                                         starttime__gte=startSmena,
                                         starttime__lte=spotSmena)
        speed25 = Speed25.objects.filter(data=datetime.date.today(),
                                         time__gte=startSmena,
                                         time__lte=spotSmena)

    prichAll = prichina.objects.all()
    podrazdeleniaEl = []
    for el in prichAll:
        podrazdeleniaEl.append(el.Key)

    otv_p = set(podrazdeleniaEl)
    prich = list(prichAll.values())

    uch = uchastok.objects.all()
    uch_vino = uchastok.objects.all()
    uch_vino33 = uchastok.objects.all()

    select33 = SetProductionSpeed.objects.all().filter(line="33")
    select33 = ['Выберите тип бутылки'] + [obj.name_bottle for obj in select33]

    try:
        select_valve_33 = ProductionTime33.objects.last().type_bottle
    except:
        select_valve_33 = None

    select31 = SetProductionSpeed.objects.all().filter(line="31")
    select31 = ['Выберите тип бутылки'] + [obj.name_bottle for obj in select31]
    try:
        select_valve_31 = ProductionTime31.objects.last().type_bottle
    except:
        select_valve_31 = None
    select24 = SetProductionSpeed.objects.all().filter(line="24")
    select24 = ['Выберите тип бутылки'] + [obj.name_bottle for obj in select24]
    try:
        select_valve_24 = ProductionTime24.objects.last().type_bottle
    except:
        select_valve_24 = None

    select25 = SetProductionSpeed.objects.all().filter(line="25")
    select25 = ['Выберите тип бутылки'] + [obj.name_bottle for obj in select25]
    try:
        select_valve_25 = ProductionTime25.objects.last().type_bottle
    except:
        select_valve_25 = None

    select26 = SetProductionSpeed.objects.all().filter(line="26")
    select26 = ['Выберите тип бутылки'] + [obj.name_bottle for obj in select26]
    try:
        select_valve_26 = ProductionTime26.objects.last().type_bottle
    except:
        select_valve_26 = None

    return render(request, "titorovka.html", {

        'otv_p': otv_p,
        'prich': prich,
        'uch': uch,
        'uch_vino': uch_vino,
        'uch_vino33': uch_vino33,

        'table31': table31,
        'speed31': speed31,

        'table33': table33,
        'speed33': speed33,

        'table24': table24,
        'speed24': speed24,

        'table25': table25,
        'speed25': speed25,

        'table26': table26,
        'speed26': speed26,

        'select33': select33,
        'select_valve_33': select_valve_33,

        'select31': select31,
        'select_valve_31': select_valve_31,

        'select24': select24,
        'select_valve_24': select_valve_24,

        'select25': select25,
        'select_valve_25': select_valve_25,

        'select26': select26,
        'select_valve_26': select_valve_26,

    })


def Sotchet(request):
    plan = 0
    timeAll = 0

    table = []
    table_other = []

    data_chartneed_speed = []
    end_bottle = []

    form = Otchet(request.GET)
    if form.is_valid():
        # Сортировка по дате
        if form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 31'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    table = (Table31.objects.filter(starttime__gte=datetime.time(0),
                                                    starttime__lte=datetime.time(23, 59),
                                                    startdata__gte=form.cleaned_data["start_data"],
                                                    startdata__lte=form.cleaned_data["finish_data"]
                                                    ).filter(uchastok="Триблок MBF") | Table31.objects.filter(
                        starttime__gte=datetime.time(0),
                        starttime__lte=datetime.time(23, 59),
                        startdata__gte=form.cleaned_data["start_data"],
                        startdata__lte=form.cleaned_data["finish_data"]).filter(
                        uchastok="Автомат этикетировочный PE")).order_by('startdata',
                                                                         'starttime')
                    table_other = Table31.objects.filter(starttime__gte=datetime.time(0),
                                                         starttime__lte=datetime.time(23, 59),
                                                         startdata__gte=form.cleaned_data["start_data"],
                                                         startdata__lte=form.cleaned_data["finish_data"]
                                                         ).exclude(uchastok="Триблок MBF").exclude(
                        uchastok="Автомат этикетировочный PE") \
                        .order_by('startdata', 'starttime')

                    speed = Speed31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(0),
                                                   time__lte=datetime.time(23, 59))

                    prod = ProductionOutput31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                             data__lte=form.cleaned_data["finish_data"],
                                                             time__gte=datetime.time(0),
                                                             time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='12ab36dc-0fb9-44d8-b14d-63230bf1c0cd',
                                                            )
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeAll = form.cleaned_data["finish_data"] - form.cleaned_data[
                            "start_data"] + datetime.timedelta(days=1)



                    except:
                        timeAll = 0
                        # Пустой список для хранения скоростей
                    try:
                        prod = ProductionOutput31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                                 data__lte=form.cleaned_data["finish_data"],
                                                                 time__gte=datetime.time(0),
                                                                 time__lte=datetime.time(23, 59))

                        prod_name = list(ProductionTime31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                                         data__lte=form.cleaned_data["finish_data"],
                                                                         time__gte=datetime.time(0),
                                                                         time__lte=datetime.time(23, 59)).order_by(
                            'data', 'time')

                        )

                        temp_bottle = ProductionTime31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                                      data__lte=form.cleaned_data["finish_data"],
                                                                      time__gte=datetime.time(0),
                                                                      time__lte=datetime.time(23, 59)).order_by(
                            'data', 'time').values('type_bottle')
                        list_bottle = []
                        for el in temp_bottle:
                            list_bottle.append(el['type_bottle'])
                        list_bottle = list(set(list_bottle))
                        for el in list_bottle:
                            production_speed = SetProductionSpeed.objects.filter(
                                name_bottle=el).filter(
                                line="31").first()
                            try:
                                end_bottle.append(
                                    [el, production_speed.speed,
                                     int(round(production_speed.speed * 1.18 / 0.8, 0))])
                            except:
                                pass
                        speeds = []

                        # # Получение скорости для каждого продукта из списка
                        for product in prod_name:
                            # Получение объекта SetProductionSpeed31 по названию продукта
                            production_speed = SetProductionSpeed.objects.filter(
                                name_bottle=product.type_bottle).filter(
                                line="31").first()

                            if production_speed:
                                # Добавление скорости продукта в список
                                speeds.append(production_speed.speed)
                            else:
                                speeds.append(0)

                        # Получение первого времени из объектов speed
                        first_speed_time = (speed.first().data, speed.first().time)

                        # Создание списка start_times с первым значением first_speed_time
                        start_times = [first_speed_time]

                        # Добавление оставшихся элементов из prod_name
                        start_times += [(elem.data, elem.time) for elem in prod_name[1:]]

                        end_times = [(elem.data, elem.time) for elem in prod_name[1:]]
                        end_times.append(
                            (speed.last().data, speed.last().time))

                        start_times = [(time) for time in start_times]
                        end_times = [(time) for time in end_times]

                        # Парное объединение элементов двух списков
                        merged_list = [(elem1, elem2, elem3) for elem1, elem2, elem3 in
                                       zip(start_times, end_times, speeds)]

                        # Перебираем все интервалы времени в merged_list

                        # print(*merged_list, sep="\n")

                        for el_speed in speed:
                            speed_datetime = datetime.datetime.combine(el_speed.data, el_speed.time)
                            speed_in_range = False
                            for start_datetime, end_datetime, speed_value in merged_list:
                                start_datetime = datetime.datetime.combine(start_datetime[0], start_datetime[1])
                                end_datetime = datetime.datetime.combine(end_datetime[0], end_datetime[1])
                                if start_datetime <= speed_datetime <= end_datetime:
                                    data_chartneed_speed.append(round(speed_value * 1.18 / 0.8, 0))
                                    speed_in_range = True
                                    break
                            if not speed_in_range:
                                data_chartneed_speed.append(0)
                    except   Exception as e:
                        # Вывод ошибки в консоль
                        print("Произошла ошибка:", e)

            if form.cleaned_data["SmenaF"] == 'Смена 1':
                table = (Table31.objects.filter(starttime__gte=datetime.time(8),
                                                starttime__lte=datetime.time(16, 00),
                                                startdata__gte=form.cleaned_data["start_data"],
                                                startdata__lte=form.cleaned_data["finish_data"]
                                                ).filter(uchastok="Триблок MBF") | Table31.objects.filter(
                    starttime__gte=datetime.time(8),
                    starttime__lte=datetime.time(16, 00),
                    startdata__gte=form.cleaned_data["start_data"],
                    startdata__lte=form.cleaned_data["finish_data"]).filter(
                    uchastok="Автомат этикетировочный PE")).order_by('startdata',
                                                                     'starttime')
                table_other = Table31.objects.filter(starttime__gte=datetime.time(8),
                                                     starttime__lte=datetime.time(16, 00),
                                                     startdata__gte=form.cleaned_data["start_data"],
                                                     startdata__lte=form.cleaned_data["finish_data"]
                                                     ).exclude(uchastok="Триблок MBF").exclude(
                    uchastok="Автомат этикетировочный PE") \
                    .order_by('startdata', 'starttime')

                speed = Speed31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(8),
                                               time__lte=datetime.time(16, 00))

                prod = ProductionOutput31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                         data__lte=form.cleaned_data["finish_data"],
                                                         time__gte=datetime.time(8),
                                                         time__lte=datetime.time(16, 00))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='12ab36dc-0fb9-44d8-b14d-63230bf1c0cd',
                                                        ShiftNumber=1)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0

                try:
                    timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = 1 + timeAll.total_seconds() / 3600 / 24
                    timeAll = datetime.timedelta(hours=(8 * count), minutes=00 * count)
                except:
                    timeAll = 0
            if form.cleaned_data["SmenaF"] == 'Смена 2':
                table = (Table31.objects.filter(starttime__gte=datetime.time(16, 00),
                                                starttime__lte=datetime.time(23, 59),
                                                startdata__gte=form.cleaned_data["start_data"],
                                                startdata__lte=form.cleaned_data["finish_data"]
                                                ).filter(uchastok="Триблок MBF") | Table31.objects.filter(
                    startdata__gte=form.cleaned_data["start_data"],
                    startdata__lte=form.cleaned_data["finish_data"],
                    starttime__gte=datetime.time(16, 00),
                    starttime__lte=datetime.time(23, 59)).filter(uchastok="Автомат этикетировочный PE")).order_by(
                    'startdata',
                    'starttime') \
                    .order_by('startdata', 'starttime')
                table_other = Table31.objects.filter(starttime__gte=datetime.time(16, 00),
                                                     starttime__lte=datetime.time(23, 59),
                                                     startdata__gte=form.cleaned_data["start_data"],
                                                     startdata__lte=form.cleaned_data["finish_data"]
                                                     ).exclude(uchastok="Триблок MBF").exclude(
                    uchastok="Этикетировка")

                speed = Speed31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(16, 00),
                                               time__lte=datetime.time(23, 59))

                prod = ProductionOutput31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                         data__lte=form.cleaned_data["finish_data"],
                                                         time__gte=datetime.time(16, 00),
                                                         time__lte=datetime.time(23, 59))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='12ab36dc-0fb9-44d8-b14d-63230bf1c0cd',
                                                        ShiftNumber=2)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0

                try:
                    timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeAll.total_seconds() / 3600 / 24 + 1

                    timeAll = datetime.timedelta(hours=(7 * count), minutes=00 * count)
                except:
                    timeAll = 0
            if form.cleaned_data["SmenaF"] == 'Смена 3':
                table = (Table31.objects.filter(starttime__gte=datetime.time(00, 00),
                                                starttime__lte=datetime.time(8, 00),
                                                startdata__gte=form.cleaned_data["start_data"],
                                                startdata__lte=form.cleaned_data["finish_data"]
                                                ).filter(uchastok="Триблок MBF") | Table31.objects.filter(
                    startdata__gte=form.cleaned_data["start_data"],
                    startdata__lte=form.cleaned_data["finish_data"],
                    starttime__gte=datetime.time(00, 00),
                    starttime__lte=datetime.time(8, 00)).filter(uchastok="Автомат этикетировочный PE")).order_by(
                    'startdata',
                    'starttime')
                table_other = Table31.objects.filter(starttime__gte=datetime.time(00, 00),
                                                     starttime__lte=datetime.time(8, 00),
                                                     startdata__gte=form.cleaned_data["start_data"],
                                                     startdata__lte=form.cleaned_data["finish_data"]
                                                     ).exclude(uchastok="Триблок MBF").exclude(
                    uchastok="Автомат этикетировочный PE") \
                    .order_by('startdata', 'starttime')

                speed = Speed31.objects.using('titorovka_db').filter(data__gte=form.cleaned_data["start_data"],
                                                                     data__lte=form.cleaned_data["finish_data"],
                                                                     time__gte=datetime.time(00, 00),
                                                                     time__lte=datetime.time(8, 00))

                prod = ProductionOutput31.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                         data__lte=form.cleaned_data["finish_data"],
                                                         time__gte=datetime.time(00, 00),
                                                         time__lte=datetime.time(8, 00))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='12ab36dc-0fb9-44d8-b14d-63230bf1c0cd',
                                                        ShiftNumber=3)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0

                try:
                    timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeAll.total_seconds() / 3600 / 24 + 1

                    timeAll = datetime.timedelta(hours=(8 * count))
                except:
                    timeAll = 0
        elif form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 33'):
            uchastok_rozliv = "Автомат розлива BORELLI"
            if form.cleaned_data["SmenaF"] == 'Смена 0':
                table = (Table33.objects.filter(starttime__gte=datetime.time(0),
                                                starttime__lte=datetime.time(23, 59),
                                                startdata__gte=form.cleaned_data["start_data"],
                                                startdata__lte=form.cleaned_data["finish_data"]
                                                ).filter(
                    uchastok__icontains=uchastok_rozliv) | Table33.objects.filter(
                    startdata__gte=form.cleaned_data["start_data"],
                    startdata__lte=form.cleaned_data["finish_data"],
                    starttime__gte=datetime.time(0),
                    starttime__lte=datetime.time(23, 59)).filter(uchastok="Автомат этикетировочный PE")).order_by(
                    'startdata',
                    'starttime')
                table_other = Table33.objects.filter(starttime__gte=datetime.time(0),
                                                     starttime__lte=datetime.time(23, 59),
                                                     startdata__gte=form.cleaned_data["start_data"],
                                                     startdata__lte=form.cleaned_data["finish_data"]
                                                     ).exclude(uchastok__icontains=uchastok_rozliv).exclude(
                    uchastok="Автомат этикетировочный PE") \
                    .order_by('startdata', 'starttime')

                speed = Speed33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(0),
                                               time__lte=datetime.time(23, 59))

                prod = ProductionOutput33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                         data__lte=form.cleaned_data["finish_data"],
                                                         time__gte=datetime.time(0),
                                                         time__lte=datetime.time(23, 59))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='d65654f8-2e89-4044-bb10-4342a9d1b722',
                                                        )
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0

                try:
                    timeAll = form.cleaned_data["finish_data"] - form.cleaned_data[
                        "start_data"] + datetime.timedelta(days=1)



                except:
                    timeAll = 0
                try:
                    prod = ProductionOutput33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                             data__lte=form.cleaned_data["finish_data"],
                                                             time__gte=datetime.time(0),
                                                             time__lte=datetime.time(23, 59))

                    prod_name = list(ProductionTime33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                                     data__lte=form.cleaned_data["finish_data"],
                                                                     time__gte=datetime.time(0),
                                                                     time__lte=datetime.time(23, 59)).order_by(
                        'data', 'time')

                    )

                    temp_bottle = ProductionTime33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                                  data__lte=form.cleaned_data["finish_data"],
                                                                  time__gte=datetime.time(0),
                                                                  time__lte=datetime.time(23, 59)).order_by(
                        'data', 'time').values('type_bottle')
                    list_bottle = []
                    for el in temp_bottle:
                        list_bottle.append(el['type_bottle'])
                    list_bottle = list(set(list_bottle))
                    for el in list_bottle:
                        production_speed = SetProductionSpeed.objects.filter(
                            name_bottle=el).filter(
                            line="33").first()
                        try:
                            end_bottle.append(
                                [el, production_speed.speed,
                                 int(round(production_speed.speed * 1.18 / 0.8, 0))])
                        except:
                            pass
                    speeds = []

                    # # Получение скорости для каждого продукта из списка
                    for product in prod_name:
                        # Получение объекта SetProductionSpeed31 по названию продукта
                        production_speed = SetProductionSpeed.objects.filter(
                            name_bottle=product.type_bottle).filter(
                            line="33").first()

                        if production_speed:
                            # Добавление скорости продукта в список
                            speeds.append(production_speed.speed)
                        else:
                            speeds.append(0)

                    # Получение первого времени из объектов speed
                    first_speed_time = (speed.first().data, speed.first().time)

                    # Создание списка start_times с первым значением first_speed_time
                    start_times = [first_speed_time]

                    # Добавление оставшихся элементов из prod_name
                    start_times += [(elem.data, elem.time) for elem in prod_name[1:]]

                    end_times = [(elem.data, elem.time) for elem in prod_name[1:]]
                    end_times.append(
                        (speed.last().data, speed.last().time))

                    start_times = [(time) for time in start_times]
                    end_times = [(time) for time in end_times]

                    # Парное объединение элементов двух списков
                    merged_list = [(elem1, elem2, elem3) for elem1, elem2, elem3 in
                                   zip(start_times, end_times, speeds)]

                    # Перебираем все интервалы времени в merged_list

                    # print(*merged_list, sep="\n")

                    for el_speed in speed:
                        speed_datetime = datetime.datetime.combine(el_speed.data, el_speed.time)
                        speed_in_range = False
                        for start_datetime, end_datetime, speed_value in merged_list:
                            start_datetime = datetime.datetime.combine(start_datetime[0], start_datetime[1])
                            end_datetime = datetime.datetime.combine(end_datetime[0], end_datetime[1])
                            if start_datetime <= speed_datetime <= end_datetime:
                                data_chartneed_speed.append(round(speed_value * 1.18 / 0.8, 0))
                                speed_in_range = True
                                break
                        if not speed_in_range:
                            data_chartneed_speed.append(0)
                except   Exception as e:
                    # Вывод ошибки в консоль
                    print("Произошла ошибка:", e)

            if form.cleaned_data["SmenaF"] == 'Смена 1':
                table = (Table33.objects.filter(starttime__gte=datetime.time(8),
                                                starttime__lte=datetime.time(16, 00),
                                                startdata__gte=form.cleaned_data["start_data"],
                                                startdata__lte=form.cleaned_data["finish_data"]
                                                ).filter(
                    uchastok__icontains=uchastok_rozliv) | Table33.objects.filter(
                    startdata__gte=form.cleaned_data["start_data"],
                    startdata__lte=form.cleaned_data["finish_data"],
                    starttime__gte=datetime.time(8),
                    starttime__lte=datetime.time(16, 00)).filter(uchastok="Автомат этикетировочный PE")).order_by(
                    'startdata',
                    'starttime')
                table_other = Table33.objects.filter(starttime__gte=datetime.time(8),
                                                     starttime__lte=datetime.time(16, 00),
                                                     startdata__gte=form.cleaned_data["start_data"],
                                                     startdata__lte=form.cleaned_data["finish_data"]
                                                     ).exclude(uchastok__icontains=uchastok_rozliv).exclude(
                    uchastok="Автомат этикетировочный PE") \
                    .order_by('startdata', 'starttime')

                speed = Speed33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(8),
                                               time__lte=datetime.time(16, 00))

                prod = ProductionOutput33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                         data__lte=form.cleaned_data["finish_data"],
                                                         time__gte=datetime.time(8),
                                                         time__lte=datetime.time(16, 00))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='d65654f8-2e89-4044-bb10-4342a9d1b722',
                                                        ShiftNumber=1)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0

                try:
                    timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = 1 + timeAll.total_seconds() / 3600 / 24
                    timeAll = datetime.timedelta(hours=(8 * count))
                except:
                    timeAll = 0
            if form.cleaned_data["SmenaF"] == 'Смена 2':
                table = (Table33.objects.filter(starttime__gte=datetime.time(16, 00),
                                                starttime__lte=datetime.time(23, 59),
                                                startdata__gte=form.cleaned_data["start_data"],
                                                startdata__lte=form.cleaned_data["finish_data"]
                                                ).filter(
                    uchastok__icontains=uchastok_rozliv) | Table33.objects.filter(
                    startdata__gte=form.cleaned_data["start_data"],
                    startdata__lte=form.cleaned_data["finish_data"],
                    starttime__gte=datetime.time(16, 00),
                    starttime__lte=datetime.time(23, 59)).filter(uchastok="Автомат этикетировочный PE")).order_by(
                    'startdata',
                    'starttime')
                table_other = Table33.objects.filter(starttime__gte=datetime.time(16, 00),
                                                     starttime__lte=datetime.time(23, 59),
                                                     startdata__gte=form.cleaned_data["start_data"],
                                                     startdata__lte=form.cleaned_data["finish_data"]
                                                     ).exclude(uchastok__icontains=uchastok_rozliv).exclude(
                    uchastok="Автомат этикетировочный PE") \
                    .order_by('startdata', 'starttime')
                speed = Speed33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(16, 00),
                                               time__lte=datetime.time(23, 59))

                prod = ProductionOutput33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                         data__lte=form.cleaned_data["finish_data"],
                                                         time__gte=datetime.time(16, 00),
                                                         time__lte=datetime.time(23, 59))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='d65654f8-2e89-4044-bb10-4342a9d1b722',
                                                        ShiftNumber=2)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0

                try:
                    timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeAll.total_seconds() / 3600 / 24 + 1

                    timeAll = datetime.timedelta(hours=(8 * count))
                except:
                    timeAll = 0
            if form.cleaned_data["SmenaF"] == 'Смена 3':
                table = (Table33.objects.filter(starttime__gte=datetime.time(00, 00),
                                                starttime__lte=datetime.time(8, 00),
                                                startdata__gte=form.cleaned_data["start_data"],
                                                startdata__lte=form.cleaned_data["finish_data"]
                                                ).filter(
                    uchastok__icontains=uchastok_rozliv) | Table33.objects.filter(
                    startdata__gte=form.cleaned_data["start_data"],
                    startdata__lte=form.cleaned_data["finish_data"],
                    starttime__gte=datetime.time(00, 00),
                    starttime__lte=datetime.time(8, 00)).filter(uchastok="Автомат этикетировочный PE")).order_by(
                    'startdata',
                    'starttime')
                table_other = Table33.objects.filter(starttime__gte=datetime.time(00, 00),
                                                     starttime__lte=datetime.time(8, 00),
                                                     startdata__gte=form.cleaned_data["start_data"],
                                                     startdata__lte=form.cleaned_data["finish_data"]
                                                     ).exclude(uchastok__icontains=uchastok_rozliv).exclude(
                    uchastok="Автомат этикетировочный PE") \
                    .order_by('startdata', 'starttime')
                speed = Speed33.objects.using('titorovka_db').filter(data__gte=form.cleaned_data["start_data"],
                                                                     data__lte=form.cleaned_data["finish_data"],
                                                                     time__gte=datetime.time(00, 00),
                                                                     time__lte=datetime.time(8, 00))

                prod = ProductionOutput33.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                         data__lte=form.cleaned_data["finish_data"],
                                                         time__gte=datetime.time(00, 00),
                                                         time__lte=datetime.time(8, 00))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='d65654f8-2e89-4044-bb10-4342a9d1b722',
                                                        ShiftNumber=3)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0

                try:
                    timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeAll.total_seconds() / 3600 / 24 + 1

                    timeAll = datetime.timedelta(hours=(8 * count))
                except:
                    timeAll = 0

    lableChart = []
    dataChart = []

    #  Общее количество продукции
    try:
        allProd = prod.aggregate(Sum('production')).get('production__sum')
        if (allProd == None):
            allProd = 0
    except:
        allProd = 0

    # Данные для графика

    try:
        for sp in speed:
            lableChart.append(str(sp.time))
            dataChart.append(sp.triblok)
    except:
        lableChart = []
        dataChart = []

    uch = uchastok.objects.all()
    uch_v = uchastok.objects.all()

    prichAll = prichina.objects.all()
    podrazdeleniaEl = []
    for el in prichAll:
        podrazdeleniaEl.append(el.Key)
    otv_p = set(podrazdeleniaEl)

    prich = list(prichAll.values())

    line = form.cleaned_data["LineF"]
    smena = form.cleaned_data["SmenaF"]
    nachaloOt = form.cleaned_data["start_data"]
    okonchanieOt = form.cleaned_data["finish_data"]

    time_by_category = []
    time_by_category_time = []

    for k in vid_prostoev:
        temp_time = datetime.timedelta(0)
        if k == "ТО и Переналадки АСУП":
            for el in table:
                if el.uchastok in vid_prostoev[k]:
                    temp_time += time_to_timedelta(el.prostoy)
            for el in table_other:
                if el.uchastok in vid_prostoev[k]:
                    temp_time += time_to_timedelta(el.prostoy)
        else:
            for el in table:
                if el.prichina in vid_prostoev[k]:
                    temp_time += time_to_timedelta(el.prostoy)
            for el in table_other:
                if el.prichina in vid_prostoev[k]:
                    temp_time += time_to_timedelta(el.prostoy)
        time_by_category.append(format_timedelta(temp_time))
        time_by_category_time.append(temp_time)

    try:
        if plan > 0 and allProd > 0:
            completion_percentage = round((allProd / plan) * 100)
        else:
            completion_percentage = 0
    except:
        completion_percentage = 0
    # Общее время простоя
    try:
        other = table_other.exclude(prichina="Закрытие партии суточное").exclude(prichina="Открытие партии суточное") \
            .exclude(prichina='Обед').aggregate(Sum('prostoy')).get('prostoy__sum')

        if not other:
            other = datetime.timedelta(0)

        osnova = table.exclude(prichina="Закрытие партии суточное").exclude(prichina="Открытие партии суточное") \
            .exclude(prichina='Обед').aggregate(Sum('prostoy')).get('prostoy__sum')

        if not osnova:
            osnova = datetime.timedelta(0)

        sumProstoy = osnova + other

        if not sumProstoy:
            sumProstoy = datetime.timedelta(0)

    except:
        sumProstoy = 0

    # Средняя скорость
    try:
        if sumProstoy > timeAll:
            sumProstoy = timeAll
        timeWork = (timeAll - sumProstoy - time_by_category_time[4] - time_by_category_time[5])

    except:
        timeWork = 0

    try:

        avgSpeed = round((allProd / timeWork.total_seconds() * 3600))
        excludeSpeed = round((allProd / (timeWork + time_by_category_time[1]).total_seconds() * 3600))
        allSpeed = round(allProd / (timeWork + sumProstoy).total_seconds() * 3600)
    except:
        avgSpeed = 0
        excludeSpeed = 0
        allSpeed = 0
    try:
        if plan > 0 and allProd > 0:
            completion_percentage = round((allProd / plan) * 100)
        else:
            completion_percentage = 0
    except:
        completion_percentage = 0

    return render(request, "Sotchet.html", {
        'table': table,
        'table_other': table_other,
        'form': form,

        'line': line,
        'smena': smena,
        'nachaloOt': nachaloOt,
        'okonchanieOt': okonchanieOt,

        'plan': plan,
        "completion_percentage": completion_percentage,
        'allProd': "{0:,}".format(allProd).replace(",", " "),

        'sumProstoy': format_timedelta(sumProstoy),
        "time_by_category": time_by_category,
        'timeWork': format_timedelta(timeWork),

        'avgSpeed': "{0:,}".format(avgSpeed).replace(",", " "),
        'excludeSpeed': "{0:,}".format(excludeSpeed).replace(",", " "),
        'allSpeed': "{0:,}".format(allSpeed).replace(",", " "),

        'lableChart': lableChart,
        'dataChart': dataChart,
        'data_chartneed_speed': data_chartneed_speed,

        'otv_p': otv_p,
        'prich': prich,
        'uch': uch,
        'uch_v': uch_v,

        'end_bottle': end_bottle

    })


def SotchetIgr(request):
    plan = 0
    table = []
    table_other = []
    timeAll = 0
    form = OtchetIgr(request.GET)
    if form.is_valid():
        # Сортировка по дате
        if form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 24'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    table = (Table24.objects.filter(starttime__gte=datetime.time(0),
                                                    starttime__lte=datetime.time(23, 59),
                                                    startdata__gte=form.cleaned_data["start_data"],
                                                    startdata__lte=form.cleaned_data["finish_data"]
                                                    ).filter(
                        uchastok="Моноблок Изобарического розлива") | Table24.objects.filter(
                        startdata__gte=form.cleaned_data["start_data"],
                        startdata__lte=form.cleaned_data["finish_data"],
                        starttime__gte=datetime.time(0),
                        starttime__lte=datetime.time(23, 59)).filter(uchastok="Этикетировочный аппарат")).order_by(
                        'startdata',
                        'starttime')
                    table_other = Table24.objects.filter(starttime__gte=datetime.time(0),
                                                         starttime__lte=datetime.time(23, 59),
                                                         startdata__gte=form.cleaned_data["start_data"],
                                                         startdata__lte=form.cleaned_data["finish_data"]
                                                         ).exclude(uchastok="Моноблок Изобарического розлива").exclude(
                        uchastok="Этикетировочный аппарат") \
                        .order_by('startdata', 'starttime')

                    speed = Speed24.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(0),
                                                   time__lte=datetime.time(23, 59))

                    prod = ProductionOutput24.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                             data__lte=form.cleaned_data["finish_data"],
                                                             time__gte=datetime.time(0),
                                                             time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='90aef8a3-8edd-4904-b22b-8f53d903f90d',
                                                            )
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeAll = form.cleaned_data["finish_data"] - form.cleaned_data[
                            "start_data"] + datetime.timedelta(days=1)



                    except:
                        timeAll = 0

                if form.cleaned_data["SmenaF"] == 'Смена 1':
                    table = (Table24.objects.filter(starttime__gte=datetime.time(8),
                                                    starttime__lte=datetime.time(16, 00),
                                                    startdata__gte=form.cleaned_data["start_data"],
                                                    startdata__lte=form.cleaned_data["finish_data"]
                                                    ).filter(
                        uchastok="Моноблок Изобарического розлива") | Table24.objects.filter(
                        startdata__gte=form.cleaned_data["start_data"],
                        startdata__lte=form.cleaned_data["finish_data"],
                        starttime__gte=datetime.time(8),
                        starttime__lte=datetime.time(16, 00)).filter(uchastok="Этикетировочный аппарат")).order_by(
                        'startdata',
                        'starttime')
                    table_other = Table24.objects.filter(starttime__gte=datetime.time(8),
                                                         starttime__lte=datetime.time(16, 00),
                                                         startdata__gte=form.cleaned_data["start_data"],
                                                         startdata__lte=form.cleaned_data["finish_data"]
                                                         ).exclude(uchastok="Моноблок Изобарического розлива").exclude(
                        uchastok="Этикетировочный аппарат") \
                        .order_by('startdata', 'starttime')
                    speed = Speed24.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(8),
                                                   time__lte=datetime.time(16, 00))

                    prod = ProductionOutput24.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                             data__lte=form.cleaned_data["finish_data"],
                                                             time__gte=datetime.time(8),
                                                             time__lte=datetime.time(16, 00))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='90aef8a3-8edd-4904-b22b-8f53d903f90d',
                                                            ShiftNumber=1)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count = 1 + timeAll.total_seconds() / 3600 / 24
                        timeAll = datetime.timedelta(hours=(8 * count))
                    except:
                        timeAll = 0
                if form.cleaned_data["SmenaF"] == 'Смена 2':
                    table = (Table24.objects.filter(starttime__gte=datetime.time(16, 00),
                                                    starttime__lte=datetime.time(23, 59),
                                                    startdata__gte=form.cleaned_data["start_data"],
                                                    startdata__lte=form.cleaned_data["finish_data"]
                                                    ).filter(
                        uchastok="Моноблок Изобарического розлива") | Table24.objects.filter(
                        startdata__gte=form.cleaned_data["start_data"],
                        startdata__lte=form.cleaned_data["finish_data"],
                        starttime__gte=datetime.time(16, 00),
                        starttime__lte=datetime.time(23, 59)).filter(uchastok="Этикетировочный аппарат")).order_by(
                        'startdata',
                        'starttime')
                    table_other = Table24.objects.filter(starttime__gte=datetime.time(16, 00),
                                                         starttime__lte=datetime.time(23, 59),
                                                         startdata__gte=form.cleaned_data["start_data"],
                                                         startdata__lte=form.cleaned_data["finish_data"]
                                                         ).exclude(uchastok="Моноблок Изобарического розлива").exclude(
                        uchastok="Этикетировочный аппарат") \
                        .order_by('startdata', 'starttime')
                    speed = Speed24.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(16, 00),
                                                   time__lte=datetime.time(23, 59))

                    prod = ProductionOutput24.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                             data__lte=form.cleaned_data["finish_data"],
                                                             time__gte=datetime.time(16, 00),
                                                             time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='90aef8a3-8edd-4904-b22b-8f53d903f90d',
                                                            ShiftNumber=2)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count = timeAll.total_seconds() / 3600 / 24 + 1

                        timeAll = datetime.timedelta(hours=(8 * count))
                    except:
                        timeAll = 0
                if form.cleaned_data["SmenaF"] == 'Смена 3':
                    table = (Table24.objects.filter(starttime__gte=datetime.time(00, 00),
                                                    starttime__lte=datetime.time(8, 00),
                                                    startdata__gte=form.cleaned_data["start_data"],
                                                    startdata__lte=form.cleaned_data["finish_data"]
                                                    ).filter(
                        uchastok="Моноблок Изобарического розлива") | Table24.objects.filter(
                        startdata__gte=form.cleaned_data["start_data"],
                        startdata__lte=form.cleaned_data["finish_data"],
                        starttime__gte=startSmena,
                        starttime__lte=spotSmena).filter(uchastok="Этикетировочный аппарат")).order_by('startdata',
                                                                                                       'starttime')
                    table_other = Table24.objects.filter(starttime__gte=datetime.time(00, 00),
                                                         starttime__lte=datetime.time(8, 00),
                                                         startdata__gte=form.cleaned_data["start_data"],
                                                         startdata__lte=form.cleaned_data["finish_data"]
                                                         ).exclude(uchastok="Моноблок Изобарического розлива").exclude(
                        uchastok="Этикетировочный аппарат") \
                        .order_by('startdata', 'starttime')
                    speed = Speed24.objects.using('titorovka_db').filter(data__gte=form.cleaned_data["start_data"],
                                                                         data__lte=form.cleaned_data["finish_data"],
                                                                         time__gte=datetime.time(00, 00),
                                                                         time__lte=datetime.time(8, 00))

                    prod = ProductionOutput24.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                             data__lte=form.cleaned_data["finish_data"],
                                                             time__gte=datetime.time(00, 00),
                                                             time__lte=datetime.time(8, 00))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='90aef8a3-8edd-4904-b22b-8f53d903f90d',
                                                            ShiftNumber=3)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count = timeAll.total_seconds() / 3600 / 24 + 1

                        timeAll = datetime.timedelta(hours=(8 * count))
                    except:
                        timeAll = 0
        elif form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 26'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    table = (Table26.objects.filter(starttime__gte=datetime.time(0, 00),
                                                    starttime__lte=datetime.time(23, 59),
                                                    startdata__gte=form.cleaned_data["start_data"],
                                                    startdata__lte=form.cleaned_data["finish_data"]
                                                    ).filter(
                        uchastok="Триблок CLIFOM") | Table26.objects.filter(
                        startdata__gte=form.cleaned_data["start_data"],
                        startdata__lte=form.cleaned_data["finish_data"],
                        starttime__gte=datetime.time(0, 00),
                        starttime__lte=datetime.time(23, 59)).filter(
                        uchastok__icontains="Этикетировочный аппарат S2T6/Ri")).order_by(
                        'startdata',
                        'starttime')
                    table_other = Table26.objects.filter(starttime__gte=datetime.time(0, 00),
                                                         starttime__lte=datetime.time(23, 59),
                                                         startdata__gte=form.cleaned_data["start_data"],
                                                         startdata__lte=form.cleaned_data["finish_data"]
                                                         ).exclude(uchastok__icontains="Триблок CLIFOM").exclude(
                        uchastok__icontains="Этикетировочный аппарат S2T6/Ri") \
                        .order_by('startdata', 'starttime')

                    speed = Speed26.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(0),
                                                   time__lte=datetime.time(23, 59))

                    prod = ProductionOutput26.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                             data__lte=form.cleaned_data["finish_data"],
                                                             time__gte=datetime.time(0),
                                                             time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='75709045-11b7-11e6-b0ff-005056ac2c77',
                                                            )
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeAll = form.cleaned_data["finish_data"] - form.cleaned_data[
                            "start_data"] + datetime.timedelta(days=1)



                    except:
                        timeAll = 0

                if form.cleaned_data["SmenaF"] == 'Смена 1':
                    table = (Table26.objects.filter(starttime__gte=datetime.time(8),
                                                    starttime__lte=datetime.time(16, 00),
                                                    startdata__gte=form.cleaned_data["start_data"],
                                                    startdata__lte=form.cleaned_data["finish_data"]
                                                    ).filter(
                        uchastok="Триблок CLIFOM") | Table26.objects.filter(
                        startdata__gte=form.cleaned_data["start_data"],
                        startdata__lte=form.cleaned_data["finish_data"],
                        starttime__gte=datetime.time(8),
                        starttime__lte=datetime.time(16, 00), ).filter(
                        uchastok__icontains="Этикетировочный аппарат S2T6/Ri")).order_by(
                        'startdata',
                        'starttime')

                    table_other = Table26.objects.filter(starttime__gte=datetime.time(8, 00),
                                                         starttime__lte=datetime.time(16, 00),
                                                         startdata__gte=form.cleaned_data["start_data"],
                                                         startdata__lte=form.cleaned_data["finish_data"]
                                                         ).exclude(uchastok="Триблок CLIFOM").exclude(
                        uchastok__icontains="Этикетировочный аппарат S2T6/Ri") \
                        .order_by('startdata', 'starttime')
                    speed = Speed26.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(8),
                                                   time__lte=datetime.time(16, 00))

                    prod = ProductionOutput26.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                             data__lte=form.cleaned_data["finish_data"],
                                                             time__gte=datetime.time(8),
                                                             time__lte=datetime.time(16, 00))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='75709045-11b7-11e6-b0ff-005056ac2c77',
                                                            ShiftNumber=1)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count = 1 + timeAll.total_seconds() / 3600 / 24
                        timeAll = datetime.timedelta(hours=(8 * count))
                    except:
                        timeAll = 0
                if form.cleaned_data["SmenaF"] == 'Смена 2':
                    table = (Table26.objects.filter(starttime__gte=datetime.time(16, 00),
                                                    starttime__lte=datetime.time(23, 59),
                                                    startdata__gte=form.cleaned_data["start_data"],
                                                    startdata__lte=form.cleaned_data["finish_data"]
                                                    ).filter(
                        uchastok="Триблок CLIFOM") | Table26.objects.filter(
                        startdata__gte=form.cleaned_data["start_data"],
                        startdata__lte=form.cleaned_data["finish_data"],
                        starttime__gte=datetime.time(16, 00),
                        starttime__lte=datetime.time(23, 59)
                    ).filter(uchastok__icontains="Этикетировочный аппарат S2T6/Ri")).order_by(
                        'startdata',
                        'starttime')
                    table_other = Table26.objects.filter(starttime__gte=datetime.time(16, 00),
                                                         starttime__lte=datetime.time(23, 59),
                                                         startdata__gte=form.cleaned_data["start_data"],
                                                         startdata__lte=form.cleaned_data["finish_data"]
                                                         ).exclude(uchastok="Триблок CLIFOM").exclude(
                        uchastok__icontains="Этикетировочный аппарат S2T6/Ri") \
                        .order_by('startdata', 'starttime')
                    speed = Speed26.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(16, 00),
                                                   time__lte=datetime.time(23, 59))

                    prod = ProductionOutput26.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                             data__lte=form.cleaned_data["finish_data"],
                                                             time__gte=datetime.time(16, 00),
                                                             time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='75709045-11b7-11e6-b0ff-005056ac2c77',
                                                            ShiftNumber=2)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count = timeAll.total_seconds() / 3600 / 24 + 1

                        timeAll = datetime.timedelta(hours=(8 * count))
                    except:
                        timeAll = 0
                if form.cleaned_data["SmenaF"] == 'Смена 3':
                    table = (Table26.objects.filter(starttime__gte=datetime.time(00, 00),
                                                    starttime__lte=datetime.time(8, 00),
                                                    startdata__gte=form.cleaned_data["start_data"],
                                                    startdata__lte=form.cleaned_data["finish_data"]
                                                    ).filter(
                        uchastok="Триблок CLIFOM") | Table26.objects.filter(
                        startdata__gte=form.cleaned_data["start_data"],
                        startdata__lte=form.cleaned_data["finish_data"],
                        starttime__gte=datetime.time(00, 00),
                        starttime__lte=datetime.time(8, 00)).filter(
                        uchastok__icontains="Этикетировочный аппарат S2T6/Ri")).order_by(
                        'startdata',
                        'starttime')
                    table_other = Table26.objects.filter(starttime__gte=datetime.time(00, 00),
                                                         starttime__lte=datetime.time(8, 00),
                                                         startdata__gte=form.cleaned_data["start_data"],
                                                         startdata__lte=form.cleaned_data["finish_data"]
                                                         ).exclude(uchastok="Триблок CLIFOM").exclude(
                        uchastok__icontains="Этикетировочный аппарат S2T6/Ri") \
                        .order_by('startdata', 'starttime')
                    speed = Speed26.objects.using('titorovka_db').filter(data__gte=form.cleaned_data["start_data"],
                                                                         data__lte=form.cleaned_data["finish_data"],
                                                                         time__gte=datetime.time(00, 00),
                                                                         time__lte=datetime.time(8, 00))

                    prod = ProductionOutput26.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                             data__lte=form.cleaned_data["finish_data"],
                                                             time__gte=datetime.time(00, 00),
                                                             time__lte=datetime.time(8, 00))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='75709045-11b7-11e6-b0ff-005056ac2c77',
                                                            ShiftNumber=3)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count = timeAll.total_seconds() / 3600 / 24 + 1

                        timeAll = datetime.timedelta(hours=(8 * count))
                    except:
                        timeAll = 0
        elif form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 25'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    table = (Table25.objects.filter(starttime__gte=datetime.time(00, 00),
                                                    starttime__lte=datetime.time(23, 59),
                                                    startdata__gte=form.cleaned_data["start_data"],
                                                    startdata__lte=form.cleaned_data["finish_data"]
                                                    ).filter(
                        uchastok__icontains="Блок розлива") | Table25.objects.filter(
                        startdata__gte=form.cleaned_data["start_data"],
                        startdata__lte=form.cleaned_data["finish_data"],
                        starttime__gte=datetime.time(00, 00),
                        starttime__lte=datetime.time(23, 59)).filter(uchastok="Этикетировочный аппарат")).order_by(
                        'startdata',
                        'starttime')
                    table_other = Table25.objects.filter(starttime__gte=datetime.time(00, 00),
                                                         starttime__lte=datetime.time(23, 59),
                                                         startdata__gte=form.cleaned_data["start_data"],
                                                         startdata__lte=form.cleaned_data["finish_data"]
                                                         ).exclude(
                        uchastok__icontains="Блок розлива и укупорки модель ASTRO").exclude(
                        uchastok="Этикетировочный аппарат") \
                        .order_by('startdata', 'starttime')
                    speed = Speed25.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(0),
                                                   time__lte=datetime.time(23, 59))

                    prod = ProductionOutput25.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                             data__lte=form.cleaned_data["finish_data"],
                                                             time__gte=datetime.time(0),
                                                             time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='33b39bdb-a94a-4baf-bf9c-31ab906efb9e',
                                                            )
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeAll = form.cleaned_data["finish_data"] - form.cleaned_data[
                            "start_data"] + datetime.timedelta(days=1)



                    except:
                        timeAll = 0

                if form.cleaned_data["SmenaF"] == 'Смена 1':
                    table = (Table25.objects.filter(starttime__gte=datetime.time(8, 00),
                                                    starttime__lte=datetime.time(16, 00),
                                                    startdata__gte=form.cleaned_data["start_data"],
                                                    startdata__lte=form.cleaned_data["finish_data"]
                                                    ).filter(
                        uchastok__icontains="Блок розлива") | Table25.objects.filter(
                        startdata__gte=form.cleaned_data["start_data"],
                        startdata__lte=form.cleaned_data["finish_data"],
                        starttime__gte=datetime.time(8, 00),
                        starttime__lte=datetime.time(16, 00)).filter(uchastok="Этикетировочный аппарат")).order_by(
                        'startdata',
                        'starttime')
                    table_other = Table25.objects.filter(starttime__gte=datetime.time(8, 00),
                                                         starttime__lte=datetime.time(16, 00),
                                                         startdata__gte=form.cleaned_data["start_data"],
                                                         startdata__lte=form.cleaned_data["finish_data"]
                                                         ).exclude(
                        uchastok__icontains="Блок розлива и укупорки модель ASTRO").exclude(
                        uchastok="Этикетировочный аппарат") \
                        .order_by('startdata', 'starttime')
                    speed = Speed25.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(8),
                                                   time__lte=datetime.time(16, 00))

                    prod = ProductionOutput25.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                             data__lte=form.cleaned_data["finish_data"],
                                                             time__gte=datetime.time(8),
                                                             time__lte=datetime.time(16, 00))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='33b39bdb-a94a-4baf-bf9c-31ab906efb9e',
                                                            ShiftNumber=1)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count = 1 + timeAll.total_seconds() / 3600 / 24
                        timeAll = datetime.timedelta(hours=(8 * count))
                    except:
                        timeAll = 0
                if form.cleaned_data["SmenaF"] == 'Смена 2':
                    table = (Table25.objects.filter(starttime__gte=datetime.time(16, 00),
                                                    starttime__lte=datetime.time(23, 59),
                                                    startdata__gte=form.cleaned_data["start_data"],
                                                    startdata__lte=form.cleaned_data["finish_data"]
                                                    ).filter(
                        uchastok__icontains="Блок розлива") | Table25.objects.filter(
                        startdata__gte=form.cleaned_data["start_data"],
                        startdata__lte=form.cleaned_data["finish_data"],
                        starttime__gte=datetime.time(16, 00),
                        starttime__lte=datetime.time(23, 59)).filter(uchastok="Этикетировочный аппарат")).order_by(
                        'startdata',
                        'starttime')
                    table_other = Table25.objects.filter(starttime__gte=datetime.time(16, 00),
                                                         starttime__lte=datetime.time(23, 59),
                                                         startdata__gte=form.cleaned_data["start_data"],
                                                         startdata__lte=form.cleaned_data["finish_data"]
                                                         ).exclude(
                        uchastok__icontains="Блок розлива и укупорки модель ASTRO").exclude(
                        uchastok="Этикетировочный аппарат") \
                        .order_by('startdata', 'starttime')
                    speed = Speed25.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(16, 00),
                                                   time__lte=datetime.time(23, 59))

                    prod = ProductionOutput25.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                             data__lte=form.cleaned_data["finish_data"],
                                                             time__gte=datetime.time(16, 00),
                                                             time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='33b39bdb-a94a-4baf-bf9c-31ab906efb9e',
                                                            ShiftNumber=2)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count = timeAll.total_seconds() / 3600 / 24 + 1

                        timeAll = datetime.timedelta(hours=(8 * count))
                    except:
                        timeAll = 0
                if form.cleaned_data["SmenaF"] == 'Смена 3':
                    table = (Table25.objects.filter(starttime__gte=datetime.time(00, 00),
                                                    starttime__lte=datetime.time(8, 00),
                                                    startdata__gte=form.cleaned_data["start_data"],
                                                    startdata__lte=form.cleaned_data["finish_data"]
                                                    ).filter(
                        uchastok__icontains="Блок розлива") | Table25.objects.filter(
                        startdata__gte=form.cleaned_data["start_data"],
                        startdata__lte=form.cleaned_data["finish_data"],
                        starttime__gte=datetime.time(00, 00),
                        starttime__lte=datetime.time(8, 00)).filter(uchastok="Этикетировочный аппарат")).order_by(
                        'startdata',
                        'starttime')
                    table_other = Table25.objects.filter(starttime__gte=datetime.time(00, 00),
                                                         starttime__lte=datetime.time(8, 00),
                                                         startdata__gte=form.cleaned_data["start_data"],
                                                         startdata__lte=form.cleaned_data["finish_data"]
                                                         ).exclude(
                        uchastok__icontains="Блок розлива и укупорки модель ASTRO").exclude(
                        uchastok="Этикетировочный аппарат") \
                        .order_by('startdata', 'starttime')
                    speed = Speed25.objects.using('titorovka_db').filter(data__gte=form.cleaned_data["start_data"],
                                                                         data__lte=form.cleaned_data["finish_data"],
                                                                         time__gte=datetime.time(00, 00),
                                                                         time__lte=datetime.time(8, 00))

                    prod = ProductionOutput25.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                             data__lte=form.cleaned_data["finish_data"],
                                                             time__gte=datetime.time(00, 00),
                                                             time__lte=datetime.time(8, 00))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='33b39bdb-a94a-4baf-bf9c-31ab906efb9e',
                                                            ShiftNumber=3)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeAll = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count = timeAll.total_seconds() / 3600 / 24 + 1

                        timeAll = datetime.timedelta(hours=(8 * count))
                    except:
                        timeAll = 0

    lableChart = []
    dataChart = []

    # Общее количество  продукции
    try:
        allProd = prod.aggregate(Sum('production')).get('production__sum')
        if (allProd == None):
            allProd = 0
    except:
        allProd = 0

    # Данные для графика

    try:
        for sp in speed:
            lableChart.append(str(sp.time))
            dataChart.append(sp.triblok)
    except:
        lableChart = []
        dataChart = []

    uch = uchastok.objects.all()
    uch_v = uchastok.objects.all()

    prichAll = prichina.objects.all()
    podrazdeleniaEl = []
    for el in prichAll:
        podrazdeleniaEl.append(el.Key)
    otv_p = set(podrazdeleniaEl)

    prich = list(prichAll.values())

    line = form.cleaned_data["LineF"]
    smena = form.cleaned_data["SmenaF"]
    nachaloOt = form.cleaned_data["start_data"]
    okonchanieOt = form.cleaned_data["finish_data"]

    time_by_category = []
    time_by_category_time = []

    for k in vid_prostoev:
        temp_time = datetime.timedelta(0)
        if k == "ТО и Переналадки АСУП":
            for el in table:
                if el.uchastok in vid_prostoev[k]:
                    temp_time += time_to_timedelta(el.prostoy)
            for el in table_other:
                if el.uchastok in vid_prostoev[k]:
                    temp_time += time_to_timedelta(el.prostoy)
        else:
            for el in table:
                if el.prichina in vid_prostoev[k]:
                    temp_time += time_to_timedelta(el.prostoy)
            for el in table_other:
                if el.prichina in vid_prostoev[k]:
                    temp_time += time_to_timedelta(el.prostoy)
        time_by_category.append(format_timedelta(temp_time))
        time_by_category_time.append(temp_time)
        # Общее время простоя
    # try:
    #     sumProstoy = table.aggregate(Sum('prostoy')).get('prostoy__sum') + table_other.aggregate(Sum('prostoy')).get(
    #         'prostoy__sum')
    #     if sumProstoy == None:
    #         sumProstoy = datetime.timedelta(0)
    # except:
    #     sumProstoy = 0
    #     # Средняя скорость
    # try:
    #     if sumProstoy > timeAll:
    #         sumProstoy = timeAll
    #     timeWork = (timeAll - sumProstoy)
    #
    #
    # except:
    #     timeWork = 0
    # try:
    #     avgSpeed = round((allProd / timeWork.total_seconds() * 3600))
    #
    # except:
    #     avgSpeed = 0
    #
    # try:
    #     avgSpeed = round((allProd / timeWork.total_seconds() * 3600))
    #     excludeSpeed = round((allProd / (timeWork + time_by_category_time[0] +
    #                                      time_by_category_time[2] + time_by_category_time[3] - time_by_category_time[
    #                                          4]).total_seconds() * 3600))
    #     allSpeed = round((allProd / (timeAll.total_seconds() - (
    #             time_by_category_time[4] + time_by_category_time[5]).total_seconds()) * 3600))
    # except:
    #     avgSpeed = 0
    #     excludeSpeed = 0
    #     allSpeed = 0
    try:
        if plan > 0 and allProd > 0:
            completion_percentage = round((allProd / plan) * 100)
        else:
            completion_percentage = 0
    except:
        completion_percentage = 0
    # Общее время простоя
    try:
        other = table_other.exclude(prichina="Закрытие партии суточное").exclude(prichina="Открытие партии суточное") \
            .exclude(prichina='Обед').aggregate(Sum('prostoy')).get('prostoy__sum')

        if not other:
            other = datetime.timedelta(0)

        osnova = table.exclude(prichina="Закрытие партии суточное").exclude(prichina="Открытие партии суточное") \
            .exclude(prichina='Обед').aggregate(Sum('prostoy')).get('prostoy__sum')

        if not osnova:
            osnova = datetime.timedelta(0)

        sumProstoy = osnova + other

        if not sumProstoy:
            sumProstoy = datetime.timedelta(0)

    except:
        sumProstoy = 0

    # Средняя скорость
    try:
        if sumProstoy > timeAll:
            sumProstoy = timeAll
        timeWork = (timeAll - sumProstoy - time_by_category_time[4] - time_by_category_time[5])

    except:
        timeWork = 0

    try:

        avgSpeed = round((allProd / timeWork.total_seconds() * 3600))
        excludeSpeed = round((allProd / (timeWork + time_by_category_time[1]).total_seconds() * 3600))
        allSpeed = round(allProd / (timeWork + sumProstoy).total_seconds() * 3600)
    except:
        avgSpeed = 0
        excludeSpeed = 0
        allSpeed = 0
    return render(request, "SotchetIgr.html", {
        'table': table,
        'table_other': table_other,
        'form': form,

        'line': line,
        'smena': smena,
        'nachaloOt': nachaloOt,
        'okonchanieOt': okonchanieOt,

        'plan': plan,
        "completion_percentage": completion_percentage,
        'allProd': "{0:,}".format(allProd).replace(",", " "),

        'sumProstoy': format_timedelta(sumProstoy),
        "time_by_category": time_by_category,
        'timeWork': format_timedelta(timeWork),

        'avgSpeed': "{0:,}".format(avgSpeed).replace(",", " "),
        'excludeSpeed': "{0:,}".format(excludeSpeed).replace(",", " "),
        'allSpeed': "{0:,}".format(allSpeed).replace(",", " "),

        'lableChart': lableChart,
        'dataChart': dataChart,

        'otv_p': otv_p,
        'prich': prich,
        'uch': uch,
        'uch_v': uch_v,

    })


def start_perenaladka31(request):
    mod_bus(0, 1)
    return HttpResponse('yes')


def start_adaptacia31(request):
    mod_bus(0, 2)
    return HttpResponse('yes')


def rabota31(request):
    mod_bus(0, 4)
    return HttpResponse('yes')


def TO31(request):
    mod_bus(0, 8)
    return HttpResponse('yes')


def Oformlenie31(request):
    mod_bus(0, 16)
    return HttpResponse('yes')


def start_perenaladka33(request):
    mod_bus(1, 1)
    return HttpResponse('yes')


def start_adaptation33(request):
    mod_bus(1, 2)
    return HttpResponse('yes')


def rabota33(request):
    mod_bus(1, 4)
    return HttpResponse('yes')


def TO33(request):
    mod_bus(1, 8)
    return HttpResponse('yes')


def start_oformlenie33(request):
    mod_bus(1, 16)
    return HttpResponse('yes')


def start_perenaladka24(request):
    mod_bus_igristoe(0, 1)
    return HttpResponse('yes')


def start_donaladka24(request):
    mod_bus_igristoe(0, 2)
    return HttpResponse('yes')


def rabota24(request):
    mod_bus_igristoe(0, 4)
    return HttpResponse('yes')


def TO24(request):
    mod_bus_igristoe(0, 8)
    return HttpResponse('yes')


def start_perenaladka26(request):
    mod_bus_igristoe(2, 1)
    return HttpResponse('yes')


def start_donaladka26(request):
    mod_bus_igristoe(2, 2)
    return HttpResponse('yes')


def rabota26(request):
    mod_bus_igristoe(2, 4)
    return HttpResponse('yes')


def TO26(request):
    mod_bus_igristoe(2, 8)
    return HttpResponse('yes')


def vid26(request):
    mod_bus_igristoe(2, 16)
    return HttpResponse('yes')


def start_perenaladka25(request):
    mod_bus_igristoe(1, 1)
    return HttpResponse('yes')


def start_donaladka25(request):
    mod_bus_igristoe(1, 2)
    return HttpResponse('yes')


def rabota25(request):
    mod_bus_igristoe(1, 4)
    return HttpResponse('yes')


def TO25(request):
    mod_bus_igristoe(1, 8)
    return HttpResponse('yes')


def vid25(request):
    mod_bus_igristoe(1, 16)
    return HttpResponse('yes')
