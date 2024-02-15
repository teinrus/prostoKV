from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Min, Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from temruk.models import Table5, Speed5, ProductionOutput5, bottling_plan, bottleExplosion5, Line5Indicators, prichina, \
    uchastok
from pyModbusTCP.client import ModbusClient

slave_address = '192.168.88.230'
port = 502
unit_id = 1
modbus_client = ModbusClient(host=slave_address, port=port, unit_id=unit_id, auto_open=True)

import time
import datetime


def get_boom_out(boom):
    try:
        return boom.aggregate(Sum('bottle')).get('bottle__sum') or 0
    except ObjectDoesNotExist:
        return 0


def get_shift_times():
    now_time = time.localtime().tm_hour * 3600 + time.localtime().tm_min * 60 + time.localtime().tm_sec

    if 0 <= now_time < 8 * 3600:
        return datetime.time(0, 0), datetime.time(8, 0)
    elif 8 * 3600 <= now_time < 16 * 3600 + 30 * 60:
        return datetime.time(8, 0), datetime.time(16, 30)
    else:
        return datetime.time(16, 30), datetime.time(23, 59, 59)


def get_shift_number():
    if 0 <= time.localtime().tm_hour < 8:
        return 3
    elif 8 <= time.localtime().tm_hour < 16.5:
        return 1
    else:
        return 2


def get_plan_quantity():
    try:
        today = datetime.datetime.today()
        shift_number = get_shift_number()
        plan = bottling_plan.objects.filter(Data=today, GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                            ShiftNumber=shift_number)
        plan_quantity = plan.aggregate(Sum('Quantity'))['Quantity__sum']
        return plan_quantity

    except Exception as e:

        return 31000


def get_average_speed(speed5_queryset):
    count = 0
    total_speed = 0
    for el in speed5_queryset:
        if el.triblok != 0:
            count += 1
            total_speed += el.triblok

    return round(total_speed / count, 2) if count > 0 else 0


def get_total_prostoy(table5_queryset):
    sum_prostoy = table5_queryset.aggregate(Sum('prostoy'))['prostoy__sum']
    return str(sum_prostoy) if sum_prostoy else '00:00'


def get_total_product(production_output5_queryset):
    sum_product = production_output5_queryset.aggregate(Sum('production'))['production__sum']
    return sum_product if sum_product else 0


def calculate_production_percentage(plan, total_product, startSmena, spotSmena):
    try:
        today = datetime.date.today()
        # количество продукции вып в сек
        d_start1 = datetime.datetime.combine(today, startSmena)
        d_end1 = datetime.datetime.combine(today, spotSmena)
        diff1 = d_end1 - d_start1

        planProdSec = plan / diff1.total_seconds()

        # количество времени которое прошло
        d_start5 = datetime.datetime.combine(today, startSmena)

        d_end5 = datetime.datetime.combine(today, datetime.datetime.now().time())
        diff5 = d_end5 - d_start5
        planNow = planProdSec * diff5.total_seconds()

        result = int(total_product / planNow * 100)
    except:
        result = 0

    return result


def update(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        value = request.POST.get('value')
        if name == "prichina":
            try:
                n = "Guid_Uchastok"
                b = Table5.objects.get(id=pk).uchastok
                v = uchastok.objects.get(Guid_Line="22b8afd6-110a-11e6-b0ff-005056ac2c77",
                                              Uchastok=b).Guid_Uchastok

                a = Table5.objects.get(id=pk)
                setattr(a, n, v)

            except Table5.DoesNotExist:
                setattr(a, n, v)
            a.save()
            # Запись гуид прицины
            n = "Guid_Prichina"
            v = prichina.objects.get(Prichina=value).Guid_Prichina
            try:
                a = Table5.objects.get(id=pk)
                setattr(a, n, v)

            except Table5.DoesNotExist:
                a = Table5(id=pk, **{n: v})
            a.save()
        if name == "comment" and not Table5.objects.get(id=pk).prichina:
            return HttpResponse('no')

        try:
            a = Table5.objects.get(id=pk)
            setattr(a, name, value)
        except Table5.DoesNotExist:
            a = Table5(id=pk, **{name: value})

        a.save()
        return HttpResponse('yes')


def update5_2(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        value = request.POST.get('value')
        if name == "prichina":
            try:
                n = "Guid_Uchastok"
                b = Table5.objects.get(id=pk).uchastok
                v = uchastok.objects.get(Guid_Line="22b8afd6-110a-11e6-b0ff-005056ac2c77",
                                              Uchastok=b).Guid_Uchastok
                a = Table5.objects.get(id=pk)
                setattr(a, n, v)

            except Table5.DoesNotExist:
                setattr(a, n, v)
            a.save()
            # Запись гуид прицины
            n = "Guid_Prichina"
            v = prichina.objects.get(Prichina=value).Guid_Prichina

            try:
                a = Table5.objects.get(id=pk)
                setattr(a, n, v)

            except Table5.DoesNotExist:
                a = Table5(id=pk, **{n: v})
            a.save()
        if name == "comment" and not Table5.objects.get(id=pk).prichina:
            return HttpResponse('no')

        try:
            a = Table5.objects.get(id=pk)
            setattr(a, name, value)
        except Table5.DoesNotExist:
            a = Table5(id=pk, **{name: value})

        a.save()
        return HttpResponse('yes')


def update_items5(request):
    start_time, stop_time = get_shift_times()

    today = datetime.date.today().isoformat()  # Convert to string representation (YYYY-MM-DD)
    table5_queryset = Table5.objects.filter(startdata=today, starttime__gte=start_time, starttime__lte=stop_time)
    return render(request, 'Line5/table_body.html', {'table5': table5_queryset})


def getData(request):
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
    avg_speed = get_average_speed(speed5_queryset)
    sum_product = get_total_product(production_output5_queryset)

    lable_chart = [str(sp.time) for sp in speed5_queryset]
    data_chart = [sp.triblok for sp in speed5_queryset]
    boomOut = get_boom_out(boom)
    temp_chart = [str(sp.time) for sp in boom]
    indicators=Line5Indicators.objects.filter(time__gte=start_time,
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
            record['start_time'] = record['first_time'].strftime('%H:%M:%S')
            record['end_time'] = record['last_time'].strftime('%H:%M:%S')
            # Добавление интервала для данного акратофора в словарь с найденными ближайшими значениями времени
            interval = {'start_time': record['start_time'], 'end_time': record['end_time']}
            intervals_by_numbacr.append(interval)

    except:
        print("intervals_by_numbacr")



    return JsonResponse({
        "data":data,
        "allProc": all_proc,
        'sumProstoy': sum_prostoy,
        'avgSpeed': avg_speed,
        'sumProduct': sum_product,
        'lableChart': lable_chart,
        'dataChart_triblok': data_chart,
        "boomOut": boomOut,
        "temp_chart": temp_chart,


    })


def getBtn5(request):
    buttons_reg = modbus_client.read_input_registers(0)

    result = {
        'buttons_reg': buttons_reg
    }

    return JsonResponse(result)
