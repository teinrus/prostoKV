from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from temruk.models import Table2, Speed2, ProductionOutput2, bottling_plan
from pyModbusTCP.client import ModbusClient

slave_address = '192.168.88.230'
port = 502
unit_id = 1
modbus_client = ModbusClient(host=slave_address, port=port, unit_id=unit_id, auto_open=True)


import time
import datetime

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
    elif 8 <= time.localtime().tm_hour < 16:
        return 1
    else:
        return 2

def get_plan_quantity():
    try:
        today = datetime.datetime.today()
        shift_number = get_shift_number()
        plan = bottling_plan.objects.filter(Data=today, GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77', ShiftNumber=shift_number)
        plan_quantity = plan.aggregate(Sum('Quantity'))['Quantity__sum'] or 31000
        return plan_quantity
    except Exception as e:
        return 31000

def get_average_speed(speed2_queryset):
    count = 0
    total_speed = 0
    for el in speed2_queryset:
        if el.triblok != 0:
            count += 1
            total_speed += el.triblok

    return round(total_speed / count, 2) if count > 0 else 0

def get_total_prostoy(table2_queryset):
    sum_prostoy = table2_queryset.aggregate(Sum('prostoy'))['prostoy__sum']
    return str(sum_prostoy) if sum_prostoy else '00:00'

def get_total_product(production_output2_queryset):
    sum_product = production_output2_queryset.aggregate(Sum('production'))['production__sum']
    return sum_product if sum_product else 0

def calculate_production_percentage(plan, total_product, startSmena, spotSmena):
    today = datetime.date.today()
    # количество продукции вып в сек
    d_start1 = datetime.datetime.combine(today, startSmena)
    d_end1 = datetime.datetime.combine(today, spotSmena)
    diff1 = d_end1 - d_start1

    planProdSec = (plan / diff1.total_seconds())
    # количество времени которое прошло
    d_start2 = datetime.datetime.combine(today, startSmena)
    d_end2 = datetime.datetime.combine(today, datetime.datetime.now().time())
    diff2 = d_end2 - d_start2

    # проц вып продукции
    return int(total_product / ((int(diff2.total_seconds()) * planProdSec) / 100))

def update2(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        value = request.POST.get('value')

        try:
            a = Table2.objects.get(id=pk)
            setattr(a, name, value)
        except Table2.DoesNotExist:
            a = Table2(id=pk, **{name: value})

        a.save()
        return HttpResponse('yes')


def update_items2(request):
    start_time, stop_time = get_shift_times()

    today = datetime.date.today().isoformat()  # Convert to string representation (YYYY-MM-DD)

    table2_queryset = Table2.objects.filter(startdata=today, starttime__gte=start_time, starttime__lte=stop_time)
    return render(request, 'Line2/table_body2.html', {'table2': table2_queryset})



def getData2(request):
    start_time, stop_time = get_shift_times()

    today = datetime.date.today().isoformat()

    plan_quantity = get_plan_quantity()

    table2_queryset = Table2.objects.filter(startdata=today, starttime__range=(start_time, stop_time))
    speed2_queryset = Speed2.objects.filter(data=today, time__range=(start_time, stop_time))
    production_output2_queryset = ProductionOutput2.objects.filter(data=today, time__range=(start_time, stop_time))

    all_proc = calculate_production_percentage(plan_quantity, get_total_product(production_output2_queryset), start_time, stop_time)
    sum_prostoy = get_total_prostoy(table2_queryset.filter())
    avg_speed = get_average_speed(speed2_queryset)
    sum_product = get_total_product(production_output2_queryset)

    lable_chart = [str(sp.time) for sp in speed2_queryset]
    data_chart = [sp.triblok for sp in speed2_queryset]
    return JsonResponse({
        "allProc2": all_proc,
        'sumProstoy2': sum_prostoy,
        'avgSpeed2': avg_speed,
        'sumProduct2': sum_product,
        'lableChart2': lable_chart,
        'dataChart2': data_chart,
    })

def getBtn2(request):
    buttons_reg = modbus_client.read_input_registers(2)

    result = {
        'buttons_reg': buttons_reg
    }

    return JsonResponse(result)
