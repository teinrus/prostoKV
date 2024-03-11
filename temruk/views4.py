from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from temruk.models import Table4, Speed4, ProductionOutput4, bottling_plan, uchastok, prichina, ProductionTime4, \
    SetProductionSpeed
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
        plan = bottling_plan.objects.filter(Data=today, GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77', ShiftNumber=shift_number)
        plan_quantity = plan.aggregate(Sum('Quantity'))['Quantity__sum'] or 31000
        return plan_quantity
    except Exception as e:
        print("alarme")
        return 31000

def get_average_speed(speed4_queryset):
    count = 0
    total_speed = 0
    for el in speed4_queryset:
        if el.triblok != 0:
            count += 1
            total_speed += el.triblok

    return round(total_speed / count, 2) if count > 0 else 0

def get_total_prostoy(table4_queryset):
    sum_prostoy = table4_queryset.aggregate(Sum('prostoy'))['prostoy__sum']
    return str(sum_prostoy) if sum_prostoy else '00:00'

def get_total_product(production_output4_queryset):
    sum_product = production_output4_queryset.aggregate(Sum('production'))['production__sum']
    return sum_product if sum_product else 0

def calculate_production_percentage(plan, total_product, startSmena, spotSmena):
    today = datetime.date.today()
    # количество продукции вып в сек
    d_start1 = datetime.datetime.combine(today, startSmena)
    d_end1 = datetime.datetime.combine(today, spotSmena)
    diff1 = d_end1 - d_start1

    planProdSec = (plan / diff1.total_seconds())
    # количество времени которое прошло
    d_start4 = datetime.datetime.combine(today, startSmena)
    d_end4 = datetime.datetime.combine(today, datetime.datetime.now().time())
    diff4 = d_end4 - d_start4
    planNow=planProdSec*diff4.total_seconds()
    try:
        result=int(total_product/planNow*100)
    except:
        result=0

    return result



def update4(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        value = request.POST.get('value')
        if name == "prichina":
            try:

                n = "Guid_Uchastok"
                b = Table4.objects.get(id=pk).uchastok
                v = uchastok.objects.get(Guid_Line="b84d1e71-1109-11e6-b0ff-005056ac2c77",
                                              Uchastok=b).Guid_Uchastok

                a = Table4.objects.get(id=pk)
                print(a, n, v)
                setattr(a, n, v)

            except Table4.DoesNotExist:
                setattr(a, n, v)
            a.save()
            # Запись гуид прицины
            n = "Guid_Prichina"
            v = prichina.objects.get(Prichina=value).Guid_Prichina
            try:
                a = Table4.objects.get(id=pk)
                setattr(a, n, v)

            except Table4.DoesNotExist:
                a = Table4(id=pk, **{n: v})
            a.save()

        if name == "comment" and not Table4.objects.get(id=pk).prichina:
            return HttpResponse('no')


        try:
            a = Table4.objects.get(id=pk)
            setattr(a, name, value)
        except Table4.DoesNotExist:
            a = Table4(id=pk, **{name: value})

        a.save()
        return HttpResponse('yes')
def update4_2(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        value = request.POST.get('value')
        if name == "prichina":
            try:
                n = "Guid_Uchastok"
                b = Table4.objects.get(id=pk).uchastok
                v = uchastok.objects.get(Guid_Line="b84d1e71-1109-11e6-b0ff-005056ac2c77",
                                              Uchastok=b).Guid_Uchastok

                a = Table4.objects.get(id=pk)
                setattr(a, n, v)

            except Table4.DoesNotExist:
                setattr(a, n, v)
            a.save()
            # Запись гуид прицины
            n = "Guid_Prichina"
            v = prichina.objects.get(Prichina=value).Guid_Prichina
            try:
                a = Table4.objects.get(id=pk)
                setattr(a, n, v)

            except Table4.DoesNotExist:
                a = Table4(id=pk, **{n: v})
            a.save()



        try:
            a = Table4.objects.get(id=pk)
            setattr(a, name, value)
        except Table4.DoesNotExist:
            a = Table4(id=pk, **{name: value})

        a.save()
        return HttpResponse('yes')


def update_items4(request):
    start_time, stop_time = get_shift_times()

    today = datetime.date.today().isoformat()  # Convert to string representation (YYYY-MM-DD)
    table4_queryset = Table4.objects.filter(startdata=today, starttime__gte=start_time, starttime__lte=stop_time)
    return render(request, 'Line4/table_body4.html', {'table4': table4_queryset})



def getData4(request):
    dataChart4_need_speed = []
    start_time, stop_time = get_shift_times()

    today = datetime.date.today().isoformat()

    plan_quantity = get_plan_quantity()

    table4_queryset = Table4.objects.filter(startdata=today, starttime__range=(start_time, stop_time))
    speed4_queryset = Speed4.objects.filter(data=today, time__range=(start_time, stop_time))
    production_output4_queryset = ProductionOutput4.objects.filter(data=today, time__range=(start_time, stop_time))

    all_proc = calculate_production_percentage(plan_quantity, get_total_product(production_output4_queryset), start_time, stop_time)
    sum_prostoy = get_total_prostoy(table4_queryset)
    avg_speed = get_average_speed(speed4_queryset)
    sum_product = get_total_product(production_output4_queryset)

    lable_chart = [str(sp.time) for sp in speed4_queryset]
    data_chart = [sp.triblok for sp in speed4_queryset]

       # Получение времени начала и окончания из ProductionTime
    start_times = list(ProductionTime4.objects.filter(data=datetime.date.today(),
                                                       time__gte=start_time,
                                                       time__lte=stop_time)
                       .values_list('time', flat=True))

    prod_name = list(ProductionTime4.objects.filter(data=datetime.date.today(),
                                                     time__gte=start_time,
                                                     time__lte=stop_time)
                     .values_list('type_bottle', flat=True))
    # Пустой список для хранения скоростей
    speeds = []

    # Получение скорости для каждого продукта из списка
    for product in prod_name:
        # Получение объекта SetProductionSpeed31 по названию продукта
        production_speed = SetProductionSpeed.objects.filter(name_bottle=product).filter(line="4").first()

        if production_speed:
            # Добавление скорости продукта в список
            speeds.append(production_speed.speed)
        else:
            speeds.append(None)

    end_times = start_times[1:] + [speed4_queryset.last().time]
    start_times = [str(time) for time in start_times]
    end_times = [str(time) for time in end_times]

    # Парное объединение элементов двух списков
    merged_list = [(elem1, elem2, elem3, elem4) for elem1, elem2, elem3, elem4 in
                   zip(start_times, end_times, speeds, prod_name)]

    for sp in speed4_queryset:
        trig = False
        for el in range(0, len(merged_list)):
            if datetime.datetime.strptime(merged_list[el][0], "%H:%M:%S").time() < sp.time \
                    <= datetime.datetime.strptime(merged_list[el][1], "%H:%M:%S").time():
                dataChart4_need_speed.append(merged_list[el][2])
                trig = True

        if not trig:
            dataChart4_need_speed.append(0)


    return JsonResponse({
        "allProc4": all_proc,
        'sumProstoy4': sum_prostoy,
        'avgSpeed4': avg_speed,
        'sumProduct4': sum_product,

        'lableChart4': lable_chart,
        'dataChart4_triblok': data_chart,
        'dataChart4_need_speed': dataChart4_need_speed,
    })

def getBtn4(request):
    buttons_reg = modbus_client.read_input_registers(1)

    result = {
        'buttons_reg': buttons_reg
    }

    return JsonResponse(result)

def select4(request):
    if request.method == 'POST':

        selected_value = request.POST.get('selected_value')

        response_data = {'selected_value': selected_value}
        print(selected_value)
        production_time = ProductionTime4(data=datetime.datetime.today(),
                                          time=datetime.datetime.now().strftime("%H:%M:%S"), type_bottle=selected_value)
        production_time.save()
        return JsonResponse(response_data)
    else:
        # Вернуть ошибку, если запрос не является POST-запросом или не AJAX-запросом
        return JsonResponse({'error': 'Invalid request'}, status=400)
