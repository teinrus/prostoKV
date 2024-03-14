import time
from datetime import datetime
import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from pyModbusTCP.client import ModbusClient

from temruk.general_functions import get_plan_quantity, calculate_production_percentage, \
    get_total_product, get_total_prostoy, get_shift_times, get_average_speed
from temruk.models import Table2, Speed2, ProductionOutput2, prichina, uchastok, ProductionTime2, \
    SetProductionSpeed

slave_address = '192.168.88.230'
port = 502
unit_id = 1
modbus_client = ModbusClient(host=slave_address, port=port, unit_id=unit_id, auto_open=True)
def update2(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        value = request.POST.get('value')
        if name == "prichina":
            b = Table2.objects.get(id=pk).uchastok
            if b == "Этикетировочная машина":
                v = "e84ba6d8-7e3c-48d1-a7c5-53789e1f3b2c"
            else:

                v = uchastok.objects.get(Guid_Line="48f7e8d8-1114-11e6-b0ff-005056ac2c77",
                                         Uchastok=b).Guid_Uchastok

            try:
                n = "Guid_Uchastok"

                a = Table2.objects.get(id=pk)
                setattr(a, n, v)

            except Table2.DoesNotExist:
                setattr(a, n, v)
            a.save()
            # Запись гуид прицины
            n = "Guid_Prichina"
            v = prichina.objects.get(Prichina=value).Guid_Prichina
            try:
                a = Table2.objects.get(id=pk)
                setattr(a, n, v)

            except Table2.DoesNotExist:
                a = Table2(id=pk, **{n: v})
            a.save()
        if name == "comment" and not Table2.objects.get(id=pk).prichina:
            return HttpResponse('no')

        try:
            a = Table2.objects.get(id=pk)
            setattr(a, name, value)
        except Table2.DoesNotExist:
            a = Table2(id=pk, **{name: value})

        a.save()
        return HttpResponse('yes')


def update2_2(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        value = request.POST.get('value')
        if name == "prichina":
            try:
                n = "Guid_Uchastok"
                b = Table2.objects.get(id=pk).uchastok

                v = uchastok.objects.get(Guid_Line="48f7e8d8-1114-11e6-b0ff-005056ac2c77",
                                         Uchastok=b).Guid_Uchastok

                a = Table2.objects.get(id=pk)
                print(a)
                setattr(a, n, v)

            except Table2.DoesNotExist:
                setattr(a, n, v)
            a.save()
            # Запись гуид прицины
            n = "Guid_Prichina"
            v = prichina.objects.get(Prichina=value).Guid_Prichina
            try:
                a = Table2.objects.get(id=pk)
                setattr(a, n, v)

            except Table2.DoesNotExist:
                a = Table2(id=pk, **{n: v})
            a.save()
        if name == "comment" and not Table2.objects.get(id=pk).prichina:
            return HttpResponse('no')

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
    dataChart2_need_speed = []
    start_time, stop_time = get_shift_times()

    today = datetime.date.today().isoformat()

    plan_quantity = get_plan_quantity(GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77')

    table2_queryset = Table2.objects.filter(startdata=today, starttime__range=(start_time, stop_time))
    speed2_queryset = Speed2.objects.filter(data=today, time__range=(start_time, stop_time))
    production_output2_queryset = ProductionOutput2.objects.filter(data=today, time__range=(start_time, stop_time))

    all_proc = calculate_production_percentage(plan_quantity, get_total_product(production_output2_queryset),
                                               start_time, stop_time)
    sum_prostoy = get_total_prostoy(table2_queryset.filter())
    avg_speed = get_average_speed(speed2_queryset)
    sum_product = get_total_product(production_output2_queryset)

    lable_chart = [str(sp.time) for sp in speed2_queryset]
    data_chart = [sp.triblok for sp in speed2_queryset]

    # Получение времени начала и окончания из ProductionTime
    start_times = list(ProductionTime2.objects.filter(data=datetime.date.today(),
                                                      time__gte=start_time,
                                                      time__lte=stop_time)
                       .values_list('time', flat=True))

    prod_name = list(ProductionTime2.objects.filter(data=datetime.date.today(),
                                                    time__gte=start_time,
                                                    time__lte=stop_time)
                     .values_list('type_bottle', flat=True))
    # Пустой список для хранения скоростей
    speeds = []

    # Получение скорости для каждого продукта из списка
    for product in prod_name:
        # Получение объекта SetProductionSpeed31 по названию продукта
        production_speed = SetProductionSpeed.objects.filter(name_bottle=product).filter(line="2").first()

        if production_speed:
            # Добавление скорости продукта в список
            speeds.append(production_speed.speed)
        else:
            speeds.append(None)

    end_times = start_times[1:] + [speed2_queryset.last().time]
    start_times = [str(time) for time in start_times]
    end_times = [str(time) for time in end_times]

    # Парное объединение элементов двух списков
    merged_list = [(elem1, elem2, elem3, elem4) for elem1, elem2, elem3, elem4 in
                   zip(start_times, end_times, speeds, prod_name)]

    for sp in speed2_queryset:
        trig = False
        for el in range(0, len(merged_list)):
            if datetime.datetime.strptime(merged_list[el][0], "%H:%M:%S").time() < sp.time \
                    <= datetime.datetime.strptime(merged_list[el][1], "%H:%M:%S").time():
                dataChart2_need_speed.append(round(merged_list[el][2] * 1.18 / 0.8, 0) if merged_list[el][2] else 0)
                trig = True

        if not trig:
            dataChart2_need_speed.append(0)

    return JsonResponse({
        "allProc2": all_proc,
        'sumProstoy2': sum_prostoy,
        'avgSpeed2': avg_speed,
        'sumProduct2': sum_product,

        'lableChart2': lable_chart,
        'dataChart2': data_chart,
        'dataChart2_need_speed': dataChart2_need_speed,
    })


def getBtn2(request):
    buttons_reg = modbus_client.read_input_registers(2)

    result = {
        'buttons_reg': buttons_reg
    }

    return JsonResponse(result)


def select2(request):
    if request.method == 'POST':

        selected_value = request.POST.get('selected_value')

        response_data = {'selected_value': selected_value}

        production_time = ProductionTime2(data=datetime.datetime.today(),
                                          time=datetime.datetime.now().strftime("%H:%M:%S"), type_bottle=selected_value)
        production_time.save()
        return JsonResponse(response_data)
    else:
        # Вернуть ошибку, если запрос не является POST-запросом или не AJAX-запросом
        return JsonResponse({'error': 'Invalid request'}, status=400)
