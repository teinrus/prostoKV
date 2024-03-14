from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Min, Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from temruk.general_functions import get_shift_number, get_plan_quantity, calculate_production_percentage, \
    get_total_product, get_total_prostoy, get_average_speed, get_shift_times, get_boom_out
from temruk.models import Table5, Speed5, ProductionOutput5, bottling_plan, bottleExplosion5, Line5Indicators, prichina, \
    uchastok, SetProductionSpeed, ProductionTime5
from pyModbusTCP.client import ModbusClient
import datetime


slave_address = '192.168.88.230'
port = 502
unit_id = 1
modbus_client = ModbusClient(host=slave_address, port=port, unit_id=unit_id, auto_open=True)
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
    dataChart5_need_speed = []
    start_time, stop_time = get_shift_times()

    today = datetime.date.today().isoformat()

    plan_quantity = get_plan_quantity(GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77')

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
            record['start_time'] = record['first_time'].strftime('%H:%M:%S')
            record['end_time'] = record['last_time'].strftime('%H:%M:%S')
            # Добавление интервала для данного акратофора в словарь с найденными ближайшими значениями времени
            interval = {'start_time': record['start_time'], 'end_time': record['end_time']}
            intervals_by_numbacr.append(interval)

    except:
        print("intervals_by_numbacr")
        # Получение времени начала и окончания из ProductionTime
    start_times = list(ProductionTime5.objects.filter(data=datetime.date.today(),
                                                       time__gte=start_time,
                                                       time__lte=stop_time)
                       .values_list('time', flat=True))

    prod_name = list(ProductionTime5.objects.filter(data=datetime.date.today(),
                                                     time__gte=start_time,
                                                     time__lte=stop_time)
                     .values_list('type_bottle', flat=True))
    # Пустой список для хранения скоростей
    speeds = []

    # Получение скорости для каждого продукта из списка
    for product in prod_name:
        # Получение объекта SetProductionSpeed31 по названию продукта
        production_speed = SetProductionSpeed.objects.filter(name_bottle=product).filter(line="5").first()

        if production_speed:
            # Добавление скорости продукта в список
            speeds.append(production_speed.speed)
        else:
            speeds.append(None)

    end_times = start_times[1:] + [speed5_queryset.last().time]
    start_times = [str(time) for time in start_times]
    end_times = [str(time) for time in end_times]

    # Парное объединение элементов двух списков
    merged_list = [(elem1, elem2, elem3, elem4) for elem1, elem2, elem3, elem4 in
                   zip(start_times, end_times, speeds, prod_name)]

    for sp in speed5_queryset:
        trig = False
        for el in range(0, len(merged_list)):
            if datetime.datetime.strptime(merged_list[el][0], "%H:%M:%S").time() < sp.time \
                    <= datetime.datetime.strptime(merged_list[el][1], "%H:%M:%S").time():
                dataChart5_need_speed.append(round(merged_list[el][2]*1.18/0.8,0) if merged_list[el][2] else 0)
                trig = True

        if not trig:
            dataChart5_need_speed.append(0)

    return JsonResponse({
        "data": data,
        "allProc": all_proc,
        'sumProstoy': sum_prostoy,
        'avgSpeed': avg_speed,
        'sumProduct': sum_product,
        'lableChart': lable_chart,
        'dataChart_triblok': data_chart,
        'dataChart5_need_speed': dataChart5_need_speed,
        "boomOut": boomOut,
        "temp_chart": temp_chart,

    })

def getBtn5(request):
    buttons_reg = modbus_client.read_input_registers(0)

    result = {
        'buttons_reg': buttons_reg
    }

    return JsonResponse(result)

def select5(request):
    if request.method == 'POST':

        selected_value = request.POST.get('selected_value')
        response_data = {'selected_value': selected_value}

        production_time = ProductionTime5(data=datetime.datetime.today(),
                                          time=datetime.datetime.now().strftime("%H:%M:%S"), type_bottle=selected_value)
        production_time.save()
        return JsonResponse(response_data)
    else:
        # Вернуть ошибку, если запрос не является POST-запросом или не AJAX-запросом
        return JsonResponse({'error': 'Invalid request'}, status=400)
