from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from temruk.models import Table5, Speed5, ProductionOutput5, bottling_plan, bottleExplosion5
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
        return datetime.time(0, 0),datetime.time(8, 0)
    elif 8 * 3600 <= now_time < 16 * 3600 + 30 * 60:
        return datetime.time(8, 0),datetime.time(16, 30)
    else:
        return datetime.time(16, 30),datetime.time(23, 59, 59)



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
        plan = bottling_plan.objects.filter(Data=today, GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77', ShiftNumber=shift_number)
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
    planNow=planProdSec*diff5.total_seconds()


    return int(total_product/planNow*100)

def update(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        value = request.POST.get('value')

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



# def getData(request):
#     start_time, stop_time = get_shift_times()
#
#     today = datetime.date.today().isoformat()
#
#     plan_quantity = get_plan_quantity()
#
#     table5_queryset = Table5.objects.filter(startdata=today, starttime__range=(start_time, stop_time))
#     speed5_queryset = Speed5.objects.filter(data=today, time__range=(start_time, stop_time))
#     production_output5_queryset = ProductionOutput5.objects.filter(data=today, time__range=(start_time, stop_time))
#     boom = bottleExplosion5.objects.filter(data=datetime.date.today(),time__range=(start_time, stop_time))
#
#     all_proc = calculate_production_percentage(plan_quantity, get_total_product(production_output5_queryset), start_time, stop_time)
#     sum_prostoy = get_total_prostoy(table5_queryset)
#     avg_speed = get_average_speed(speed5_queryset)
#     sum_product = get_total_product(production_output5_queryset)
#
#     lable_chart = [str(sp.time) for sp in speed5_queryset]
#     data_chart = [sp.triblok for sp in speed5_queryset]
#     boomOut = get_boom_out(boom)
#
#     boomTemp=list(boom)
#     return JsonResponse({
#         "allProc": all_proc,
#         'sumProstoy': sum_prostoy,
#         'avgSpeed': avg_speed,
#         'sumProduct': sum_product,
#         'lableChart': lable_chart,
#         'dataChart_triblok': data_chart,
#         "boomOut":boomOut,
#         "boomTemp":boomTemp,
#
#     })

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







    return JsonResponse({
        "allProc": all_proc,
        'sumProstoy': sum_prostoy,
        'avgSpeed': avg_speed,
        'sumProduct': sum_product,
        'lableChart': lable_chart,
        'dataChart_triblok': data_chart,
        "boomOut": boomOut,
        "temp_chart":temp_chart,
    })

def getBtn5(request):
    buttons_reg = modbus_client.read_input_registers(0)

    result = {
        'buttons_reg': buttons_reg
    }

    return JsonResponse(result)
