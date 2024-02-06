import datetime

import random

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Min, Max

from django.shortcuts import redirect

from temruk.models import *
from .forms import Otchet
from pyModbusTCP.client import ModbusClient
from django.shortcuts import render
from django.http import HttpResponse

from django.db.models import Avg, F
from django.db.models.functions import Round

from .views2 import get_shift_number
from .views5 import get_shift_times, get_plan_quantity, calculate_production_percentage, get_total_prostoy, \
    get_average_speed, get_total_product, get_boom_out

vid_prostoev = {
    "Аварийные простои": ["Настройка после переналадки", "Поломка аппарата",
                          "Отсутствие азота",
                          "Отсутствие углекислоты",
                          "Отсутствие сжатого воздуха",
                          "Настройка налива",
                          "Настройка",
                          "Настройка принтера даты",
                          "Поломка транспортера подачи на СГП",
                          "Отсутствие комплектующих",
                          "Скрытый брак",
                          "Неправильное хранение комплектующих",
                          "Тестирование новых комплектующих",
                          "Согласованное использование комплектующих с отклонением",
                          "Не выявленный брак комплектующих после приемки",
                          "Разбилась бутылка в аппарате",
                          "Отсутствие в/м",
                          "Отсутствие анализа по в/м",
                          "Доработка в/м",
                          "Вспенивание в/м",
                          "Доработка в процессе розлива",
                          "Замена винных фильтров (к)",
                          "Отсутствие персонала",
                          "Сбой в работе помарочн. учета",
                          "Некачественная мойка термотоннеля",
                          "Замена винных фильтров",
                          "Ручное оформление",

                          "Переупаковка",
                          "Ошибка сотрудников ЦР",
                          "Замена баллона с углекислотой",
                          "Замена водяных фильтров",
                          "Отсутсвие места для готовой продукции",
                          "Отсутствие электроэнергии",
                          "Отсутствие воды",
                          "Форс-мажор",
                          "Отключение газа",
                          "Сбой работы программного обеспечения"],
    "Технологические простои": ["Ротация персонала",
                                "Обед",
                                "Замена контрэтикетки, этикетки, марки",
                                "Замена QR",
                                "Замена скотча",
                                "Закрытие партии суточное",
                                "Открытие партии суточное",
                                "Замена рибона, коробочного стикера",
                                "Порвалась к.этик, этикетка",
                                "Переход на новый акратофор,емкость",
                                "Наполнение термотоннеля",
                                "Техническое обслуживание линии"],
    "Переналадки": ["Переход по этикетке",
                    "Переход по партии",
                    "Переход по этикетке и в/м",
                    "Переход по этикетке, в/м и бутылке без мойки",
                    "Переход по этикетке, пробке, мюзле",
                    "Мойка (сан. час)",
                    "Переход по этикетке, в/м и бутылке с мойкой (2 ч)",
                    "Переход на кольеретку",
                    "Переход по этикетке, в/м и бутылке с мойкой (4 ч)",
                    "Переход по в/м, этикетке, бутылке с мойкой (Линия 31)",
                    "Переход по этикетке, в/м и бутылке (переход с изменением объема бутылки)"]
}


def mod_bus(reg, bit_temp):
    slave_address = '192.168.88.230'
    port = 502
    unit_id = 1
    modbus_client = ModbusClient(host=slave_address, port=port, unit_id=unit_id, auto_open=True)
    test = modbus_client.write_single_register(reg, bit_temp)


start1 = datetime.time(8, 00, 0)
start2 = datetime.time(16, 30, 0)
start3 = datetime.time(23, 59, 0)

if start1 <= datetime.datetime.now().time() <= start2:
    startSmena = datetime.time(8, 00, 0)
    spotSmena = datetime.time(16, 30, 0)
elif start2 <= datetime.datetime.now().time() <= start3:
    startSmena = datetime.time(16, 30, 0)
    spotSmena = datetime.time(23, 59, 0)
else:
    startSmena = datetime.time(00, 00, 00)
    spotSmena = datetime.time(8, 00, 00)


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


# стартовая страница
def index(request):
    if request.method == 'GET':
        user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if user_ip:
            ip = user_ip.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    ipMask = ip.split('.')
    if ipMask[2] == "97":
        return redirect('temruk')
    else:
        return redirect('titorovka')


def TV5(request):
    start_time, stop_time = get_shift_times()

    today = datetime.date.today().isoformat()

    plan_quantity = get_plan_quantity()

    table5_queryset = Table5.objects.filter(startdata=today, starttime__range=(start_time, stop_time))
    speed5_queryset = Speed5.objects.filter(data=today, time__range=(start_time, stop_time))
    production_output5_queryset = ProductionOutput5.objects.filter(data=today, time__range=(start_time, stop_time))
    boom = bottleExplosion5.objects.filter(data=datetime.date.today(), time__range=(start_time, stop_time))

    all_proc = calculate_production_percentage(plan_quantity, get_total_product(production_output5_queryset),
                                               start_time, stop_time)
    sum_prostoy = get_total_prostoy(table5_queryset)
    avg_speed = '{0:,}'.format(int(get_average_speed(speed5_queryset))).replace(',', ' ')
    sum_product = '{0:,}'.format(get_total_product(production_output5_queryset)).replace(',', ' ')

    lable_chart = [str(sp.time) for sp in speed5_queryset]
    data_chart = [sp.triblok for sp in speed5_queryset]
    boomOut = get_boom_out(boom)
    temp_chart = [str(sp.time) for sp in boom]
    indicators = Line5Indicators.objects.filter(time__gte=start_time,
                                                time__lte=stop_time,
                                                data=today)
    indicators_chart = indicators

    data = {
        'labels': [obj.time.strftime('%H:%M:%S') for obj in indicators_chart if obj.time is not None],
        'naptemp': [round(obj.naptemp, 1) for obj in indicators_chart if obj.naptemp is not None],
        'nappress': [round(obj.nappress, 1) for obj in indicators_chart if obj.nappress is not None],
        'mintemp': [-1.6 for obj in indicators_chart if obj.nappress is not None],
        'maxtemp': [0 for obj in indicators_chart if obj.nappress is not None],
        'minpress': [4.9 for obj in indicators_chart if obj.nappress is not None],
        'maxpress': [5.3 for obj in indicators_chart if obj.nappress is not None],
        'mintemp_chart': "-1.6",
        'maxtemp_chart': "0",
        'minpress_chart': "4.9",
        'maxpress_chart': "5.3"

    }

    intervals_by_numbacr = []
    try:
        indicators_with_times = indicators.values(
            'numbacr',
            'data',
        ).annotate(
            start_time=Min('time'),
            end_time=Max('time')
        ).order_by('data', 'start_time')

        # Создаем список для сгруппированных записей
        date_time_numbacr_list = []

        for indicator in indicators_with_times:
            numbacr = indicator['numbacr']
            first_time = indicator['start_time']
            last_time = indicator['end_time']
            first_data = indicator['data']

            record = {
                'numbacr': numbacr,
                'first_data': first_data,
                'first_time': first_time,
                'last_time': last_time,

            }
            date_time_numbacr_list.append(record)

        sorted_date_time_numbacr_list = sorted(date_time_numbacr_list, key=lambda x: (x['first_data'], x['first_time']))

        # Преобразование времени в объекты datetime для более удобной работы

        for record in sorted_date_time_numbacr_list:
            start_time = datetime.time.strftime(record['first_time'], '%H:%M:%S')

            end_time = datetime.time.strftime(record['last_time'], '%H:%M:%S')

            # Добавление интервала для данного акратофора в словарь с найденными ближайшими значениями времени
            interval = {'start_time': start_time, 'end_time': end_time}
            intervals_by_numbacr.append(interval)

    except:
        print("alarme")

    return render(request, "tv/tv5.html", {

        "indicators": sorted_date_time_numbacr_list,
        "intervals_by_numbacr": intervals_by_numbacr,

        "data": data,
        "allProc": all_proc,
        'sumProstoy': sum_prostoy,
        'avgSpeed': avg_speed,
        'sumProduct': sum_product,
        'lableChart': lable_chart,
        'dataChart_triblok': data_chart,
        "boomOut": boomOut,
        "temp_chart": temp_chart,
    })


def get_plan_quantity2():
    try:
        today = datetime.datetime.today()
        shift_number = get_shift_number()
        plan = bottling_plan.objects.filter(Data=today, GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77',
                                            ShiftNumber=shift_number)
        plan_quantity = plan.aggregate(Sum('Quantity'))['Quantity__sum'] or 31000
        return plan_quantity
    except Exception as e:
        return 31000


def TV2(request):
    start_time, stop_time = get_shift_times()

    today = datetime.date.today().isoformat()

    plan_quantity = get_plan_quantity2()

    table2_queryset = Table2.objects.filter(startdata=today, starttime__range=(start_time, stop_time))
    speed2_queryset = Speed2.objects.filter(data=today, time__range=(start_time, stop_time))

    production_output2_queryset = ProductionOutput2.objects.filter(data=today, time__range=(start_time, stop_time))

    all_proc = calculate_production_percentage(plan_quantity, get_total_product(production_output2_queryset),
                                               start_time, stop_time)
    sum_prostoy = get_total_prostoy(table2_queryset)
    avg_speed = get_average_speed(speed2_queryset)
    sum_product = get_total_product(production_output2_queryset)

    lable_chart = [str(sp.time) for sp in speed2_queryset]
    data_chart = [sp.triblok for sp in speed2_queryset]

    indicators = Line2Indicators.objects.filter(time__gte=start_time,
                                                time__lte=stop_time,
                                                data=today)
    indicators_chart = indicators

    data = {
        'labels': [obj.time.strftime('%H:%M:%S') for obj in indicators_chart if obj.time is not None],
        'naptemp': [round(obj.naptemp, 1) for obj in indicators_chart if obj.naptemp is not None],
        'nappress': [round(obj.nappress, 1) for obj in indicators_chart if obj.nappress is not None],
        'mintemp': [-1.6 for obj in indicators_chart if obj.nappress is not None],
        'maxtemp': [0 for obj in indicators_chart if obj.nappress is not None],
        'minpress': [4.9 for obj in indicators_chart if obj.nappress is not None],
        'maxpress': [5.3 for obj in indicators_chart if obj.nappress is not None],
        'mintemp_chart': "-1.6",
        'maxtemp_chart': "0",
        'minpress_chart': "4.9",
        'maxpress_chart': "5.3"
    }

    intervals_by_numbacr = []
    try:
        indicators_with_times = indicators.values(
            'numbacr',
            'data',
        ).annotate(
            start_time=Min('time'),
            end_time=Max('time')
        ).order_by('data', 'start_time')

        # Создаем список для сгруппированных записей
        date_time_numbacr_list = []

        for indicator in indicators_with_times:
            numbacr = indicator['numbacr']
            first_time = indicator['start_time']
            last_time = indicator['end_time']
            first_data = indicator['data']

            record = {
                'numbacr': numbacr,
                'first_data': first_data,
                'first_time': first_time,
                'last_time': last_time,

            }
            date_time_numbacr_list.append(record)

        sorted_date_time_numbacr_list = sorted(date_time_numbacr_list, key=lambda x: (x['first_data'], x['first_time']))

        # Преобразование времени в объекты datetime для более удобной работы

        for record in sorted_date_time_numbacr_list:
            start_time = datetime.time.strftime(record['first_time'], '%H:%M:%S')

            end_time = datetime.time.strftime(record['last_time'], '%H:%M:%S')

            # Добавление интервала для данного акратофора в словарь с найденными ближайшими значениями времени
            interval = {'start_time': start_time, 'end_time': end_time}
            intervals_by_numbacr.append(interval)

    except:
        print("alarme")

    return render(request, "tv/tv2.html", {

        "indicators": sorted_date_time_numbacr_list,
        "intervals_by_numbacr": intervals_by_numbacr,

        "data": data,
        "allProc": all_proc,
        'sumProstoy': sum_prostoy,
        'avgSpeed': avg_speed,
        'sumProduct': sum_product,
        'lable_chart': lable_chart,
        'data_chart': data_chart,

    })


def get_plan_quantity4():
    try:
        today = datetime.datetime.today()
        shift_number = get_shift_number()
        plan = bottling_plan.objects.filter(Data=today, GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77',
                                            ShiftNumber=shift_number)
        plan_quantity = plan.aggregate(Sum('Quantity'))['Quantity__sum'] or 31000
        return plan_quantity
    except Exception as e:
        print("alarme")
        return 31000


def TV4(request):
    start_time, stop_time = get_shift_times()

    today = datetime.date.today().isoformat()

    plan_quantity = get_plan_quantity()

    table4_queryset = Table4.objects.filter(startdata=today, starttime__range=(start_time, stop_time))
    speed4_queryset = Speed4.objects.filter(data=today, time__range=(start_time, stop_time))
    production_output4_queryset = ProductionOutput4.objects.filter(data=today, time__range=(start_time, stop_time))

    all_proc = calculate_production_percentage(plan_quantity, get_total_product(production_output4_queryset),
                                               start_time, stop_time)
    sum_prostoy = get_total_prostoy(table4_queryset)
    avg_speed = get_average_speed(speed4_queryset)
    sum_product = get_total_product(production_output4_queryset)

    lable_chart = [str(sp.time) for sp in speed4_queryset]
    data_chart = [sp.triblok for sp in speed4_queryset]

    return render(request, "tv/tv4.html", {
        "allProc4": all_proc,
        'sumProstoy4': sum_prostoy,
        'avgSpeed4': avg_speed,
        'sumProduct4': sum_product,
        'lableChart4': lable_chart,
        'dataChart4_triblok': data_chart,
    })


def temruk(request):
    if request.method == 'GET':
        table5 = Table5.objects.filter(startdata=datetime.date.today(),
                                       starttime__gte=startSmena,
                                       starttime__lte=spotSmena)
        speed5 = Speed5.objects.filter(data=datetime.date.today(),
                                       time__gte=startSmena,
                                       time__lte=spotSmena)
        table4 = Table4.objects.filter(startdata=datetime.date.today(),
                                       starttime__gte=startSmena,
                                       starttime__lte=spotSmena)
        speed4 = Speed4.objects.filter(data=datetime.date.today(),
                                       time__gte=startSmena,
                                       time__lte=spotSmena)
        table2 = Table2.objects.filter(startdata=datetime.date.today(),
                                       starttime__gte=startSmena,
                                       starttime__lte=spotSmena)
        speed2 = Speed2.objects.filter(data=datetime.date.today(),
                                       time__gte=startSmena,
                                       time__lte=spotSmena)

    # prichAll = prichina.objects.all()
    prichAll = prichina.objects.all()
    podrazdeleniaEl = []
    for el in prichAll:
        # podrazdeleniaEl.append(el.key)
        podrazdeleniaEl.append(el.Key)
    otv_p = set(podrazdeleniaEl)

    prich = list(prichAll.values())

    uch = uchastok.objects.all().filter(Guid_Line="48f7e8d8-1114-11e6-b0ff-005056ac2c77")
    uch_vino = uchastok.objects.all().filter(Guid_Line="b84d1e71-1109-11e6-b0ff-005056ac2c77")
    uch5 = uchastok.objects.filter(Guid_Line="22b8afd6-110a-11e6-b0ff-005056ac2c77")
    return render(request, "temruk.html", {

        'otv_p': otv_p,
        'prich': prich,
        'uch': uch,
        "uch5": uch5,
        'uch_vino': uch_vino,

        'table5': table5,
        'speed5': speed5,

        'table4': table4,
        'speed4': speed4,

        'table2': table2,
        'speed2': speed2,

    })


def otchet(request):
    plan = 0
    table = []
    table_triblok = []
    temp_chart = []
    timeTemp = 0

    indicators = []
    filter = []

    form = Otchet(request.GET)
    if form.is_valid():

        # Сортировка по дате
        if form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 5'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    boom = bottleExplosion5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                           data__lte=form.cleaned_data["finish_data"],
                                                           time__range=(datetime.time(0), datetime.time(23, 59)))
                    temp_chart = [str(sp.time) for sp in boom]
                    table = Table5.objects.filter(starttime__gte=datetime.time(0),
                                                  starttime__lte=datetime.time(23, 59),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')

                    speed = Speed5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(0),
                                                  time__lte=datetime.time(23, 59))
                    boom = bottleExplosion5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                           data__lte=form.cleaned_data["finish_data"],
                                                           time__gte=datetime.time(0),
                                                           time__lte=datetime.time(23, 59))
                    prod = ProductionOutput5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                            data__lte=form.cleaned_data["finish_data"],
                                                            time__gte=datetime.time(0),
                                                            time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                                            )
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data[
                            "start_data"] + datetime.timedelta(days=1)



                    except:
                        timeTemp = 0

                    try:
                        indicators = Line5Indicators.objects.filter(time__gte=datetime.time(0),
                                                                    time__lte=datetime.time(23, 59),
                                                                    data__gte=form.cleaned_data["start_data"],
                                                                    data__lte=form.cleaned_data["finish_data"])
                        filter = Filter5.objects.filter(time__gte=datetime.time(0),
                                                        time__lte=datetime.time(23, 59),
                                                        data__gte=form.cleaned_data["start_data"],
                                                        data__lte=form.cleaned_data["finish_data"])


                    except:
                        print("alarme")

                if form.cleaned_data["SmenaF"] == 'Смена 1':
                    boom = bottleExplosion5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                           data__lte=form.cleaned_data["finish_data"],
                                                           time__range=(datetime.time(8), datetime.time(16, 30)))
                    temp_chart = [str(sp.time) for sp in boom]
                    table = Table5.objects.filter(starttime__gte=datetime.time(8),
                                                  starttime__lte=datetime.time(16, 30),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')
                    speed = Speed5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(8),
                                                  time__lte=datetime.time(16, 30))
                    boom = bottleExplosion5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                           data__lte=form.cleaned_data["finish_data"],
                                                           time__gte=datetime.time(8),
                                                           time__lte=datetime.time(16, 30))
                    prod = ProductionOutput5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                            data__lte=form.cleaned_data["finish_data"],
                                                            time__gte=datetime.time(8),
                                                            time__lte=datetime.time(16, 30))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                                            ShiftNumber=1)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count = 1 + timeTemp.total_seconds() / 3600 / 24
                        timeTemp = datetime.timedelta(hours=(8 * count), minutes=30 * count)
                    except:
                        timeTemp = 0

                    indicators = Line5Indicators.objects.filter(time__gte=datetime.time(8),
                                                                time__lte=datetime.time(16, 30),
                                                                data__gte=form.cleaned_data["start_data"],
                                                                data__lte=form.cleaned_data["finish_data"])
                    filter = Filter5.objects.filter(time__gte=datetime.time(8),
                                                    time__lte=datetime.time(16, 30),
                                                    data__gte=form.cleaned_data["start_data"],
                                                    data__lte=form.cleaned_data["finish_data"])
                if form.cleaned_data["SmenaF"] == 'Смена 2':
                    boom = bottleExplosion5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                           data__lte=form.cleaned_data["finish_data"],
                                                           time__range=(datetime.time(16, 30), datetime.time(23, 59)))
                    temp_chart = [str(sp.time) for sp in boom]

                    table = Table5.objects.filter(starttime__gte=datetime.time(16, 30),
                                                  starttime__lte=datetime.time(23, 59),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')
                    speed = Speed5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(16, 30),
                                                  time__lte=datetime.time(23, 59))
                    boom = bottleExplosion5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                           data__lte=form.cleaned_data["finish_data"],
                                                           time__gte=datetime.time(16, 30),
                                                           time__lte=datetime.time(23, 59))
                    prod = ProductionOutput5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                            data__lte=form.cleaned_data["finish_data"],
                                                            time__gte=datetime.time(16, 30),
                                                            time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                                            ShiftNumber=2)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count = timeTemp.total_seconds() / 3600 / 24 + 1

                        timeTemp = datetime.timedelta(hours=(7 * count), minutes=30 * count)
                    except:
                        timeTemp = 0
                    indicators = Line5Indicators.objects.filter(time__gte=datetime.time(16, 30),
                                                                time__lte=datetime.time(23, 59),
                                                                data__gte=form.cleaned_data["start_data"],
                                                                data__lte=form.cleaned_data["finish_data"])
                    filter = Filter5.objects.filter(time__gte=datetime.time(16, 30),
                                                    time__lte=datetime.time(23, 59),
                                                    data__gte=form.cleaned_data["start_data"],
                                                    data__lte=form.cleaned_data["finish_data"])
                if form.cleaned_data["SmenaF"] == 'Смена 3':
                    boom = bottleExplosion5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                           data__lte=form.cleaned_data["finish_data"],
                                                           time__range=(datetime.time(00, 00), datetime.time(8, 00)))
                    temp_chart = [str(sp.time) for sp in boom]
                    table = Table5.objects.filter(starttime__gte=datetime.time(00, 00),
                                                  starttime__lte=datetime.time(8, 00),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')
                    speed = Speed5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(00, 00),
                                                  time__lte=datetime.time(8, 00))
                    boom = bottleExplosion5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                           data__lte=form.cleaned_data["finish_data"],
                                                           time__gte=datetime.time(00, 00),
                                                           time__lte=datetime.time(8, 00))
                    prod = ProductionOutput5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                            data__lte=form.cleaned_data["finish_data"],
                                                            time__gte=datetime.time(00, 00),
                                                            time__lte=datetime.time(8, 00))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                                            ShiftNumber=3)
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                        count = timeTemp.total_seconds() / 3600 / 24 + 1

                        timeTemp = datetime.timedelta(hours=(8 * count))
                    except:
                        timeTemp = 0
                    try:
                        indicators = Line5Indicators.objects.filter(time__gte=datetime.time(00, 00),
                                                                    time__lte=datetime.time(8, 00),
                                                                    data__gte=form.cleaned_data["start_data"],
                                                                    data__lte=form.cleaned_data["finish_data"])
                        filter = Filter5.objects.filter(time__gte=datetime.time(00, 00),
                                                        time__lte=datetime.time(8, 00),
                                                        data__gte=form.cleaned_data["start_data"],
                                                        data__lte=form.cleaned_data["finish_data"])
                    except:
                        print("alarme")
            try:

                table_triblok = table.filter(uchastok="Триблок розлива")
                table = table.exclude(uchastok="Триблок розлива")

            except:
                pass
        # Сортировка по сменам линии 2:
        if form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 2'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    table2 = Table2.objects.filter(starttime__gte=datetime.time(0),
                                                   starttime__lte=datetime.time(23, 59),
                                                   startdata__gte=form.cleaned_data["start_data"],
                                                   startdata__lte=form.cleaned_data["finish_data"]
                                                   ).order_by('startdata', 'starttime')

                    speed2 = Speed2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(0),
                                                   time__lte=datetime.time(23, 59))
                    productionOutput2 = ProductionOutput2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                                         data__lte=form.cleaned_data["finish_data"],
                                                                         time__gte=datetime.time(0),
                                                                         time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77')
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data[
                            "start_data"] + datetime.timedelta(days=1)
                    except:
                        timeTemp = 0
                    try:
                        indicators = Line2Indicators.objects.filter(time__gte=datetime.time(0),
                                                                    time__lte=datetime.time(23, 59),
                                                                    data__gte=form.cleaned_data["start_data"],
                                                                    data__lte=form.cleaned_data["finish_data"])
                        filter = Filter2.objects.filter(time__gte=datetime.time(0),
                                                        time__lte=datetime.time(23, 59),
                                                        data__gte=form.cleaned_data["start_data"],
                                                        data__lte=form.cleaned_data["finish_data"])
                    except:
                        print("alarme")
            if form.cleaned_data["SmenaF"] == 'Смена 1':
                table2 = Table2.objects.filter(starttime__gte=datetime.time(8),
                                               starttime__lte=datetime.time(16, 30),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed2 = Speed2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(8),
                                               time__lte=datetime.time(16, 30))
                productionOutput2 = ProductionOutput2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                                     data__lte=form.cleaned_data["finish_data"],
                                                                     time__gte=datetime.time(8),
                                                                     time__lte=datetime.time(16, 30))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=1)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0
                try:

                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(8 * count), minutes=30 * count)
                except:
                    timeTemp = 0
                try:
                    indicators = Line2Indicators.objects.filter(time__gte=datetime.time(8, 30),
                                                                time__lte=datetime.time(16, 30),
                                                                data__gte=form.cleaned_data["start_data"],
                                                                data__lte=form.cleaned_data["finish_data"])
                    filter = Filter2.objects.filter(time__gte=datetime.time(8, 30),
                                                    time__lte=datetime.time(16, 30),
                                                    data__gte=form.cleaned_data["start_data"],
                                                    data__lte=form.cleaned_data["finish_data"])
                except:
                    print("alarme")
            if form.cleaned_data["SmenaF"] == 'Смена 2':

                indicators = Line2Indicators.objects.filter(time__gte=datetime.time(16, 30),
                                                            time__lte=datetime.time(23, 59),
                                                            data__gte=form.cleaned_data["start_data"],
                                                            data__lte=form.cleaned_data["finish_data"])
                filter = Filter2.objects.filter(time__gte=datetime.time(16, 30),
                                                time__lte=datetime.time(23, 59),
                                                data__gte=form.cleaned_data["start_data"],
                                                data__lte=form.cleaned_data["finish_data"])
                table2 = Table2.objects.filter(starttime__gte=datetime.time(16, 30),
                                               starttime__lte=datetime.time(23, 59),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed2 = Speed2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(16, 30),
                                               time__lte=datetime.time(23, 59))
                productionOutput2 = ProductionOutput2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                                     data__lte=form.cleaned_data["finish_data"],
                                                                     time__gte=datetime.time(16, 30),
                                                                     time__lte=datetime.time(23, 59))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=2)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0

                try:

                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(7 * count), minutes=30 * count)
                except:
                    timeTemp = 0

            if form.cleaned_data["SmenaF"] == 'Смена 3':
                indicators = Line2Indicators.objects.filter(time__gte=datetime.time(00, 00),
                                                            time__lte=datetime.time(8, 00),
                                                            data__gte=form.cleaned_data["start_data"],
                                                            data__lte=form.cleaned_data["finish_data"])
                filter = Filter2.objects.filter(time__gte=datetime.time(00, 00),
                                                time__lte=datetime.time(8, 00),
                                                data__gte=form.cleaned_data["start_data"],
                                                data__lte=form.cleaned_data["finish_data"])
                table2 = Table2.objects.filter(starttime__gte=datetime.time(00, 00),
                                               starttime__lte=datetime.time(8, 00),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed2 = Speed2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(00, 00),
                                               time__lte=datetime.time(8, 00))
                productionOutput2 = ProductionOutput2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                                     data__lte=form.cleaned_data["finish_data"],
                                                                     time__gte=datetime.time(00, 00),
                                                                     time__lte=datetime.time(8, 00))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=3)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0
                try:
                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(8 * count))
                except:
                    timeTemp = 0

            table = table2
            try:

                table_triblok = table.filter(uchastok="Триблок")
                table = table.exclude(uchastok="Триблок")

            except:
                pass
            speed = speed2
            prod = productionOutput2
            boom = 0
        if form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 4'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    table4 = Table4.objects.filter(starttime__gte=datetime.time(0),
                                                   starttime__lte=datetime.time(23, 59),
                                                   startdata__gte=form.cleaned_data["start_data"],
                                                   startdata__lte=form.cleaned_data["finish_data"]
                                                   ).order_by('startdata', 'starttime')

                    speed4 = Speed4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(0),
                                                   time__lte=datetime.time(23, 59))
                    productionOutput4 = ProductionOutput4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                                         data__lte=form.cleaned_data["finish_data"])
                    filter = Filter4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                    data__lte=form.cleaned_data["finish_data"],
                                                    time__gte=datetime.time(0),
                                                    time__lte=datetime.time(23, 59))

                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77')
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0
                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data[
                            "start_data"] + datetime.timedelta(days=1)


                    except:
                        timeTemp = 0
            if form.cleaned_data["SmenaF"] == 'Смена 1':
                table4 = Table4.objects.filter(starttime__gte=datetime.time(8),
                                               starttime__lte=datetime.time(16, 30),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed4 = Speed4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(8),
                                               time__lte=datetime.time(16, 30))
                productionOutput4 = ProductionOutput4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                                     data__lte=form.cleaned_data["finish_data"],
                                                                     time__gte=datetime.time(8),
                                                                     time__lte=datetime.time(16, 30))
                filter = Filter4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                data__lte=form.cleaned_data["finish_data"],
                                                time__gte=datetime.time(8),
                                                time__lte=datetime.time(16, 30))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=1)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0
                try:
                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(8 * count), minutes=30 * count)
                except:
                    timeTemp = 0
            if form.cleaned_data["SmenaF"] == 'Смена 2':
                table4 = Table4.objects.filter(starttime__gte=datetime.time(16, 30),
                                               starttime__lte=datetime.time(23, 59),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed4 = Speed4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(16, 30),
                                               time__lte=datetime.time(23, 59))
                productionOutput4 = ProductionOutput4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                                     data__lte=form.cleaned_data["finish_data"],
                                                                     time__gte=datetime.time(16, 30),
                                                                     time__lte=datetime.time(23, 59))
                filter = Filter4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                data__lte=form.cleaned_data["finish_data"],
                                                time__gte=datetime.time(16, 30),
                                                time__lte=datetime.time(23, 59))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=2)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0
                try:
                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(7 * count), minutes=30 * count)
                except:
                    timeTemp = 0

            if form.cleaned_data["SmenaF"] == 'Смена 3':
                table4 = Table4.objects.filter(starttime__gte=datetime.time(00, 00),
                                               starttime__lte=datetime.time(8, 00),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed4 = Speed4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(00, 00),
                                               time__lte=datetime.time(8, 00))
                productionOutput4 = ProductionOutput4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                                     data__lte=form.cleaned_data["finish_data"],
                                                                     time__gte=datetime.time(00, 00),
                                                                     time__lte=datetime.time(8, 00))
                filter = Filter4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                data__lte=form.cleaned_data["finish_data"],
                                                time__gte=datetime.time(00, 00),
                                                time__lte=datetime.time(8, 00))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=3)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0
                try:
                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(8 * count))
                except:
                    timeTemp = 0

            table = table4
            try:

                table_triblok = table.filter(uchastok="Триблок")
                table = table.exclude(uchastok="Триблок")

            except:
                pass
            speed = speed4
            prod = productionOutput4
            boom = 0
    lableChart = []
    dataChart = []

    # Общее количество  продукции
    try:
        allProd = prod.aggregate(Sum('production')).get('production__sum')
        if (allProd == None):
            allProd = 0



    except:
        allProd = 0

    if plan > 0 and allProd>0:
        completion_percentage=round((allProd/plan)*100)
    else:
        completion_percentage=0
    # Общее количество  врывов бутылок
    try:
        boomOut = boom.aggregate(Sum('bottle')).get('bottle__sum')
        if (boomOut == None):
            boomOut = 0
    except:
        boomOut = 0

    # Общее время простоя
    try:
        sumProstoy = table.aggregate(Sum('prostoy')).get('prostoy__sum')+table_triblok.aggregate(Sum('prostoy')).get('prostoy__sum')
        if sumProstoy == None:
            sumProstoy = datetime.timedelta(0)
    except:
        sumProstoy = 0
    # Средняя скорость
    try:
        if sumProstoy > timeTemp:
            sumProstoy = timeTemp
        timeWork = (timeTemp - sumProstoy)


    except:
        timeWork = 0
    try:
        avgSpeed = round((allProd / timeWork.total_seconds() * 3600))

    except:
        avgSpeed = 0

    # Данные для графика
    try:
        for sp in speed:
            lableChart.append(str(sp.time))
            if sp.triblok > 6800:
                dataChart.append(random.choice(dataChart))
            else:
                dataChart.append(sp.triblok)
    except:
        lableChart = []
        dataChart = []

    uch = uchastok.objects.all().filter(Guid_Line="48f7e8d8-1114-11e6-b0ff-005056ac2c77")
    uch_vino = uchastok.objects.all().filter(Guid_Line="b84d1e71-1109-11e6-b0ff-005056ac2c77")
    uch5 = uchastok.objects.filter(Guid_Line="22b8afd6-110a-11e6-b0ff-005056ac2c77")

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
    sorted_date_time_numbacr_list = []

    indicators_chart = indicators

    data = {
        'labels': [obj.time.strftime('%H:%M:%S') for obj in indicators_chart if obj.time is not None],
        'naptemp': [round(obj.naptemp, 1) for obj in indicators_chart if obj.naptemp is not None],
        'nappress': [round(obj.nappress, 1) for obj in indicators_chart if obj.nappress is not None],
        'mintemp': [-1.6 for obj in indicators_chart if obj.nappress is not None],
        'maxtemp': [0 for obj in indicators_chart if obj.nappress is not None],
        'minpress': [4.9 for obj in indicators_chart if obj.nappress is not None],
        'maxpress': [5.3 for obj in indicators_chart if obj.nappress is not None],
        'mintemp_chart': "-1.6",
        'maxtemp_chart': "0",
        'minpress_chart': "4.9",
        'maxpress_chart': "5.3"
    }

    intervals_by_numbacr = []

    try:
        indicators_with_times = indicators.values(
            'numbacr',
            'data',
        ).annotate(
            start_time=Min('time'),
            end_time=Max('time')
        ).order_by('data', 'start_time')
        # Создаем список для сгруппированных записей
        date_time_numbacr_list = []

        for indicator in indicators_with_times:
            numbacr = indicator['numbacr']
            first_time = indicator['start_time']
            last_time = indicator['end_time']
            first_data = indicator['data']

            average_triblok_speed = speed.filter(
                time__range=(first_time, last_time),
                triblok__gt=1000
            ).aggregate(average_triblok_speed=Avg('triblok'))['average_triblok_speed']
            average_press = indicators.filter(
                time__range=(first_time, last_time),
            ).aggregate(average_press=Avg('nappress'))
            average_temp = indicators.filter(
                time__range=(first_time, last_time),
            ).aggregate(average_temp=Avg('naptemp'))

            filter_data = filter.filter(
                time__range=(first_time, last_time)
            ).aggregate(
                press1_avg=Avg('press1'),
                press2_avg=Avg('press2')
            )

            record = {
                'numbacr': numbacr,
                'first_data': first_data,
                'first_time': first_time,
                'last_time': last_time,
                'average_press': average_press,
                'average_temp': average_temp,
                'average_triblok_speed': average_triblok_speed,
                'filter_data': filter_data,

            }
            date_time_numbacr_list.append(record)

        sorted_date_time_numbacr_list = sorted(date_time_numbacr_list, key=lambda x: (x['first_data'], x['first_time']))

        # Преобразование времени в объекты datetime для более удобной работы

        for i, record in enumerate(sorted_date_time_numbacr_list):
            start_time = datetime.time.strftime(record['first_time'], '%H:%M:%S')

            end_time = datetime.time.strftime(record['last_time'], '%H:%M:%S')

            # Добавление интервала для данного акратофора в словарь с найденными ближайшими значениями времени
            interval = {'start_time': start_time, 'end_time': end_time}
            intervals_by_numbacr.append(interval)

    except:
        pass
    try:
        plan = "{0:,}".format(plan).replace(",", " ")
    except:
        pass

    time_by_category = []

    for k in vid_prostoev:
        temp_time = datetime.timedelta(0)
        for el in table:
            if el.prichina in vid_prostoev[k]:
                temp_time += time_to_timedelta(el.prostoy)
        for el in table_triblok:
            if el.prichina in vid_prostoev[k]:
                temp_time += time_to_timedelta(el.prostoy)
        time_by_category.append(format_timedelta(temp_time))




    return render(request, "otchet.html", {
        'table': table,
        "table_triblok": table_triblok,
        'form': form,



        "tempChart": temp_chart,
        "indicators": sorted_date_time_numbacr_list,
        "intervals_by_numbacr": intervals_by_numbacr,
        "data": data,
        'lableChart': lableChart,
        'dataChart': dataChart,

        'line': line,
        'smena': smena,
        'nachaloOt': nachaloOt,
        'okonchanieOt': okonchanieOt,



        'plan': plan,
        "completion_percentage":completion_percentage,
        'allProd': "{0:,}".format(allProd).replace(",", " "),

        'sumProstoy': format_timedelta(sumProstoy),
        "time_by_category":time_by_category,
        'timeWork': format_timedelta(timeWork),

        'avgSpeed': "{0:,}".format(avgSpeed).replace(",", " "),

        'boomOut': boomOut,

        'otv_p': otv_p,
        'prich': prich,
        'uch': uch,
        'uch5': uch5,
        'uch_vino': uch_vino,



    })
def time_to_timedelta(time_obj):
    try:
        return datetime.timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second)
    except:
        return  datetime.timedelta(hours=0, minutes=0)
def format_timedelta(td):
    try:
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return "{:02}:{:02}".format(int(hours), int(minutes))
    except:
        return  datetime.timedelta(hours=0, minutes=0)

def start_perenaladka5(request):
    mod_bus(0, 1)
    return HttpResponse('yes')


def start_donaladka5(request):
    mod_bus(0, 2)
    return HttpResponse('yes')


def rabota5(request):
    mod_bus(0, 4)
    return HttpResponse('yes')


def TO5(request):
    mod_bus(0, 8)
    return HttpResponse('yes')


def start_perenaladka4(request):
    mod_bus(1, 1)
    return HttpResponse('yes')


def start_donaladka4(request):
    mod_bus(1, 2)
    return HttpResponse('yes')


def rabota4(request):
    mod_bus(1, 4)
    return HttpResponse('yes')


def TO4(request):
    mod_bus(1, 8)
    return HttpResponse('yes')


def start_perenaladka2(request):
    mod_bus(2, 1)
    return HttpResponse('yes')


def start_donaladka2(request):
    mod_bus(2, 2)
    return HttpResponse('yes')


def rabota2(request):
    mod_bus(2, 4)
    return HttpResponse('yes')


def TO2(request):
    mod_bus(2, 8)
    return HttpResponse('yes')


# блок формирования отчета


def otchetSmena(request):
    nomenklatura = []
    nomenklatura1 = []
    nomenklatura4 = []
    nomenklatura2 = []
    indicators2 = []
    indicators5 = []
    co2_rozliv = []
    co2_kupaj = []

    if datetime.time(hour=8) < datetime.datetime.now().time() < datetime.time(hour=16, minute=30):

        smena = 3
        start_data = datetime.datetime.today()
        finish_data = datetime.datetime.today()
        start_time = str(datetime.timedelta(hours=0))
        finish_time = str(datetime.timedelta(hours=8))
        timeTemp = datetime.timedelta(hours=8)
        dataTemp = datetime.datetime.today()


    elif datetime.datetime.now().time() > datetime.time(hour=16, minute=29):

        smena = 1
        start_data = datetime.datetime.today()
        finish_data = datetime.datetime.today()
        start_time = str(datetime.timedelta(hours=8))
        finish_time = str(datetime.timedelta(hours=16, minutes=30))
        timeTemp = datetime.timedelta(hours=8, minutes=30)
        dataTemp = datetime.datetime.today()
    else:

        smena = 2
        start_data = datetime.datetime.today() - datetime.timedelta(days=1)
        finish_data = datetime.datetime.today() - datetime.timedelta(days=1)
        start_time = str(datetime.timedelta(hours=16, minutes=30))
        finish_time = str(datetime.timedelta(hours=23, minutes=59))
        timeTemp = datetime.timedelta(hours=7, minutes=30)
        dataTemp = datetime.datetime.today() - datetime.timedelta(days=1)

    try:
        co2_rozliv = CO2_Rozliv.objects.filter(time__gte=start_time,
                                               time__lte=finish_time,
                                               data__gte=start_data,
                                               data__lte=finish_data
                                               ).order_by('data', 'time').aggregate(sum_volume=Sum('volume'))[
            'sum_volume']

        co2_rozliv = round(co2_rozliv * 1.96, 2)
    except:
        co2_rozliv = 0
    try:
        filter5 = Filter5.objects.filter(time__gte=start_time,
                                         time__lte=finish_time,
                                         data__gte=start_data,
                                         data__lte=finish_data
                                         ).order_by('data', 'time').aggregate(
            press1_avg=Avg('press1'),
            press2_avg=Avg('press2')
        )
    except:
        filter5 = 0
    try:
        filter4 = Filter4.objects.filter(time__gte=start_time,
                                         time__lte=finish_time,
                                         data__gte=start_data,
                                         data__lte=finish_data
                                         ).order_by('data', 'time').aggregate(
            press1_avg=Avg('press1'),
            press2_avg=Avg('press2')
        )
    except:
        filter4 = 0
    try:
        filter2 = Filter2.objects.filter(time__gte=start_time,
                                         time__lte=finish_time,
                                         data__gte=start_data,
                                         data__lte=finish_data
                                         ).order_by('data', 'time').aggregate(
            press1_avg=Avg('press1'),
            press2_avg=Avg('press2')
        )
    except:
        filter2 = 0
    try:
        co2_kupaj = CO2_Kupaj.objects.filter(time__gte=start_time,
                                             time__lte=finish_time,
                                             data__gte=start_data,
                                             data__lte=finish_data
                                             ).order_by('data', 'time').aggregate(sum_volume=Sum('volume'))[
            'sum_volume']
        co2_kupaj = round(co2_kupaj * 1.96, 2)
    except:
        co2_kupaj = 0

    table5 = Table5.objects.filter(starttime__gte=start_time,
                                   starttime__lte=finish_time,
                                   startdata__gte=start_data,
                                   startdata__lte=finish_data
                                   ).order_by('startdata', 'starttime')

    table4 = Table4.objects.filter(starttime__gte=start_time,
                                   starttime__lte=finish_time,
                                   startdata__gte=start_data,
                                   startdata__lte=finish_data
                                   ).order_by('startdata', 'starttime')

    table2 = Table2.objects.filter(starttime__gte=start_time,
                                   starttime__lte=finish_time,
                                   startdata__gte=start_data,
                                   startdata__lte=finish_data
                                   ).order_by('startdata', 'starttime')

    boom5 = bottleExplosion5.objects.filter(data__gte=start_data,
                                            data__lte=finish_data,
                                            time__gte=start_time,
                                            time__lte=finish_time)
    boom5 = boom5 if boom5 != None else 0

    prod5 = ProductionOutput5.objects.filter(data__gte=start_data,
                                             data__lte=finish_data,
                                             time__gte=start_time,
                                             time__lte=finish_time)
    prod4 = ProductionOutput4.objects.filter(data__gte=start_data,
                                             data__lte=finish_data,
                                             time__gte=start_time,
                                             time__lte=finish_time)
    prod2 = ProductionOutput2.objects.filter(data__gte=start_data,
                                             data__lte=finish_data,
                                             time__gte=start_time,
                                             time__lte=finish_time)
    prod1 = ProductionOutput1.objects.filter(data__gte=start_data,
                                             data__lte=finish_data,
                                             time__gte=start_time,
                                             time__lte=finish_time)

    speed = Speed5.objects.filter(data__gte=start_data,
                                  data__lte=finish_data,
                                  time__gte=start_time,
                                  time__lte=finish_time)
    speed4 = Speed4.objects.filter(data__gte=start_data,
                                   data__lte=finish_data,
                                   time__gte=start_time,
                                   time__lte=finish_time)
    speed2 = Speed2.objects.filter(data__gte=start_data,
                                   data__lte=finish_data,
                                   time__gte=start_time,
                                   time__lte=finish_time)
    try:
        speed_triblok5 = round(speed.filter(triblok__gt=100).aggregate(Avg('triblok'))['triblok__avg'])
    except:
        speed_triblok5 = 0
    try:
        speed_triblok4 = round(speed4.filter(triblok__gt=100).aggregate(Avg('triblok'))['triblok__avg'])
    except:
        speed_triblok4 = 0
    try:
        speed_triblok2 = round(speed2.filter(triblok__gt=100).aggregate(Avg('triblok'))['triblok__avg'])
    except:
        speed_triblok2 = 0
    try:
        plan1 = bottling_plan.objects.filter(Data__gte=start_data,
                                             Data__lte=finish_data,
                                             GIUDLine='d5cda256-1113-11e6-b0ff-005056ac2c77',
                                             ShiftNumber=smena)

    except:
        plan1 = 0

    try:
        for el in plan1:
            nomenklatura1 += Nomenclature.objects.filter(GUID=el.GUIDNomenсlature)

        len1 = len(nomenklatura1)

    except:
        nomenklatura1 = "План отсутствует"
        len1 = 0

    try:
        plan = bottling_plan.objects.filter(Data__gte=start_data,
                                            Data__lte=finish_data,
                                            GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                            ShiftNumber=smena)

    except:
        plan = 0

    try:
        for el in plan:
            nomenklatura += Nomenclature.objects.filter(GUID=el.GUIDNomenсlature)

        len5 = len(nomenklatura)
    except:
        nomenklatura = "План отсутствует"
        len5 = 0

    try:
        plan4 = bottling_plan.objects.filter(Data__gte=start_data,
                                             Data__lte=finish_data,
                                             GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77',
                                             ShiftNumber=smena)
    except:
        plan4 = 0

    try:
        for el in plan4:
            nomenklatura4 += Nomenclature.objects.filter(GUID=el.GUIDNomenсlature)
        len4 = len(nomenklatura4)
    except:
        nomenklatura4 = "План отсутствует"
        len4 = 0

    try:
        plan2 = bottling_plan.objects.filter(Data__gte=start_data,
                                             Data__lte=finish_data,
                                             GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77',
                                             ShiftNumber=smena)
    except:
        plan2 = 0

    try:
        for el in plan2:
            nomenklatura2 += Nomenclature.objects.filter(GUID=el.GUIDNomenсlature)
        len2 = len(nomenklatura2)
    except:
        nomenklatura2 = "План отсутствует"
        len4 = 0

    # Общее количество  продукции
    try:
        allProd = prod5.aggregate(Sum('production')).get('production__sum')
        if (allProd == None):
            allProd = 0
        procent = int(allProd / plan.aggregate(Sum('Quantity')).get('Quantity__sum') * 100)
    except:
        procent = 0
        allProd = 0

    try:
        otklonenie = int(allProd) - int(plan.aggregate(Sum('Quantity')).get('Quantity__sum'))
    except:
        otklonenie = 0

    try:
        allProd4 = prod4.aggregate(Sum('production')).get('production__sum')
        if (allProd4 == None):
            allProd4 = 0
        procent4 = int(allProd4 / plan4.aggregate(Sum('Quantity')).get('Quantity__sum') * 100)

    except:
        allProd4 = 0
        procent4 = 0
    try:
        otklonenie4 = int(allProd4) - int(plan4.aggregate(Sum('Quantity')).get('Quantity__sum'))
    except:
        otklonenie4 = 0
    try:
        allProd2 = prod2.aggregate(Sum('production')).get('production__sum')
        if (allProd2 == None):
            allProd2 = 0
        procent2 = int(allProd2 / plan2.aggregate(Sum('Quantity')).get('Quantity__sum') * 100)

    except:
        allProd2 = 0
        procent2 = 0
    try:
        allProd1 = prod1.aggregate(Sum('production')).get('production__sum')
        if (allProd1 == None):
            allProd1 = 0
        procent2 = int(allProd1 / plan1.aggregate(Sum('Quantity')).get('Quantity__sum') * 100)

    except:
        allProd1 = 0
        procent1 = 0
    try:
        otklonenie2 = int(allProd2) - int(plan2.aggregate(Sum('Quantity')).get('Quantity__sum'))
    except:
        otklonenie2 = 0
    try:
        otklonenie1 = int(allProd1) - int(plan1.aggregate(Sum('Quantity')).get('Quantity__sum'))
    except:
        otklonenie1 = 0
    # Общее количество  врывов бутылок
    try:
        boomOut = boom5.aggregate(Sum('bottle')).get('bottle__sum')
        if (boomOut == None):
            boomOut = 0
    except:
        boomOut = 0

    # Общее время простоя
    try:
        sumProstoy = table5.aggregate(Sum('prostoy')).get('prostoy__sum')
        if sumProstoy == None:
            sumProstoy = datetime.timedelta(0)
    except:
        sumProstoy = 0
    try:
        sumProstoy4 = table4.aggregate(Sum('prostoy')).get('prostoy__sum')
        if sumProstoy4 == None:
            sumProstoy4 = datetime.timedelta(0)
    except:
        sumProstoy4 = 0
    try:
        sumProstoy2 = table2.aggregate(Sum('prostoy')).get('prostoy__sum')
        if sumProstoy2 == None:
            sumProstoy2 = datetime.timedelta(0)
    except:
        sumProstoy2 = 0

    # Средняя скорость
    try:
        if sumProstoy > timeTemp:
            sumProstoy = timeTemp
        timeWork = (timeTemp - sumProstoy)

    except:
        timeWork = 0
    try:
        if sumProstoy4 > timeTemp:
            sumProstoy4 = timeTemp
        timeWork4 = (timeTemp - sumProstoy4)

    except:
        timeWork4 = 0
    try:
        if sumProstoy2 > timeTemp:
            sumProstoy2 = timeTemp
        timeWork2 = (timeTemp - sumProstoy2)

    except:
        timeWork2 = 0

    try:

        avgSpeed = round((allProd / timeWork.total_seconds() * 3600))

    except:
        avgSpeed = 0

    try:

        avgSpeed4 = round((allProd4 / timeWork4.total_seconds() * 3600))

    except:
        avgSpeed4 = 0
    try:

        avgSpeed2 = round((allProd2 / timeWork2.total_seconds() * 3600))
    except:
        avgSpeed2 = 0
    try:
        plan_t5 = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan_t5 == None:
            plan_t5 = 0
    except:
        plan_t5 = 0
    try:
        plan_t4 = plan4.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan_t4 == None:
            plan_t4 = 0
    except:
        plan_t4 = 0
    try:
        plan_t2 = plan2.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan_t2 == None:
            plan_t2 = 0
    except:
        plan_t2 = 0
    try:
        plan_t1 = plan1.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan_t1 == None:
            plan_t1 = 0
    except:
        plan_t1 = 0

    try:
        itog_plan = plan_t5 + plan_t4 + plan_t2 + plan_t1


    except:
        itog_plan = 0

    try:
        itog_fact5 = prod5.aggregate(Sum('production')).get('production__sum')
        if itog_fact5 == None:
            itog_fact5 = 0
    except:
        itog_fact5 = 0
    try:
        itog_fact4 = prod4.aggregate(Sum('production')).get('production__sum')
        if itog_fact4 == None:
            itog_fact4 = 0
    except:
        itog_fact4 = 0
    try:
        itog_fact2 = prod2.aggregate(Sum('production')).get('production__sum')
        if itog_fact2 == None:
            itog_fact2 = 0
    except:
        itog_fact2 = 0

    try:
        itog_fact1 = prod1.aggregate(Sum('production')).get('production__sum')
        if itog_fact1 == None:
            itog_fact1 = 0
    except:
        itog_fact1 = 0
    try:
        itog_fact = itog_fact1 + itog_fact2 + itog_fact4 + itog_fact5

    except:
        itog_fact = 0

    itog_otcl = otklonenie + otklonenie4 + otklonenie2 + otklonenie1
    itog_proc = int(itog_fact / itog_plan * 100)

    try:
        indicators2 = Line2Indicators.objects.filter(time__gte=start_time,
                                                     time__lte=finish_time,
                                                     data__gte=start_data,
                                                     data__lte=finish_data).values('numbacr') \
            .annotate(avg_naptemp=Avg('naptemp'), avg_nappress=Avg('nappress')) \
            .annotate(avg_naptemp_rounded=Round(F('avg_naptemp'), 2)) \
            .annotate(avg_nappress_rounded=Round(F('avg_nappress'), 2))

    except:
        print("alarme2")
    try:
        indicators5 = Line5Indicators.objects.filter(time__gte=start_time,
                                                     time__lte=finish_time,
                                                     data__gte=start_data,
                                                     data__lte=finish_data).values('numbacr') \
            .annotate(avg_naptemp=Avg('naptemp'), avg_nappress=Avg('nappress')) \
            .annotate(avg_naptemp_rounded=Round(F('avg_naptemp'), 2)) \
            .annotate(avg_nappress_rounded=Round(F('avg_nappress'), 2))

    except:
        print("alarme")

    return render(request, "otchetSmena.html", {

        "co2_rozliv": co2_rozliv,
        "co2_kupaj": co2_kupaj,

        "filter5": filter5,
        "filter4": filter4,
        "filter2": filter2,

        "indicators2": indicators2,
        "indicators5": indicators5,
        "speed_triblok5": speed_triblok5,
        "speed_triblok4": speed_triblok4,
        "speed_triblok2": speed_triblok2,

        "itog_plan": itog_plan,
        "itog_fact": itog_fact,
        "itog_otcl": itog_otcl,
        "itog_proc": itog_proc,

        'otklonenie': otklonenie,
        'otklonenie4': otklonenie4,
        'otklonenie2': otklonenie2,

        'dataTemp': dataTemp.date(),
        'smena': smena,

        'procent': procent,
        'procent4': procent4,
        'procent2': procent2,

        'table5': table5,
        'table4': table4,
        'table2': table2,

        'timeWork': timeWork,
        'timeWork4': timeWork4,
        'timeWork2': timeWork2,

        'nomenklatura': nomenklatura,
        'nomenklatura1': nomenklatura1,
        'nomenklatura4': nomenklatura4,
        'nomenklatura2': nomenklatura2,

        "len5": len5,
        "len4": len4,
        "len2": len2,
        "len1": len1,

        'plan': plan,
        'plan1': plan1,
        'plan4': plan4,
        'plan2': plan2,

        'sumProstoy': sumProstoy,
        'sumProstoy4': sumProstoy4,
        'sumProstoy2': sumProstoy2,

        'avgSpeed': avgSpeed,
        'avgSpeed4': avgSpeed4,
        'avgSpeed2': avgSpeed2,

        'boomOut': boomOut,

        'allProd': allProd,
        'allProd4': allProd4,
        'allProd2': allProd2,

    })


# блок аунтефикации
@login_required
def profile_view(request):
    return render(request, 'registration/profile.html')


def profileOut_view(request):
    logout(request)
    if request.method == 'GET':
        user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if user_ip:
            ip = user_ip.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    ipMask = ip.split('.')
    if ipMask[2] == "97":
        return redirect('temruk')
    else:
        return redirect('titorovka')
