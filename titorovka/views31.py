import datetime

from django.db.models import Count, Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404

from temruk.models import bottling_plan, Nomenclature
from titorovka.models import *
from pyModbusTCP.client import ModbusClient

slave_address = '10.36.20.2'
unit_id = 1
modbus_client = ModbusClient(host=slave_address, unit_id=unit_id, auto_open=True)

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


# функция формирования процентов за текущию смену
def proc(startSmena, spotSmena, plan, colProduct):
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
    return int(colProduct / ((int(diff2.total_seconds()) * planProdSec) / 100))


# изменение в таблице
def update31(request):
    if request.method == 'POST':

        pk = request.POST.get('pk')
        name = request.POST.get('name')
        v = request.POST.get('value')

        if name == 'uchastok':
            try:
                a = Table31.objects.get(id=pk)
                a.uchastok = v
                a.save()
            except:
                a = Table31(uchastok=v, id=pk)
                a.save()
        elif name == 'prichina':
            try:

                a = Table31.objects.get(id=pk)
                a.prichina = v
                a.save()
            except:
                a = Table31(prichina=v, id=pk)
                a.save()
        elif name == 'otv_pod':
            try:
                a = Table31.objects.get(id=pk)
                a.otv_pod = v
                a.save()
            except:
                a = Table31(otv_pod=v, id=pk)
                a.save()
        elif name == 'comment':
            try:
                a = Table31.objects.get(id=pk)
                a.comment = v
                a.save()
            except:
                a = Table31(comment=v, id=pk)
                a.save()

    return HttpResponse('yes')


# получение данных в таблицу
def update_items31(request):
    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 00, 0)
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 00, 0)
        spotSmena = datetime.time(23, 59, 0)
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)

    table31 = Table31.objects.filter(startdata=datetime.date.today(),
                                     starttime__gte=startSmena,
                                     starttime__lte=spotSmena).filter(uchastok="Триблок") | Table31.objects.filter(
        startdata=datetime.date.today(),
        starttime__gte=startSmena,
        starttime__lte=spotSmena).filter(uchastok="Этикетировка")
    return render(request, 'Line31/table_body31.html', {'table31': table31})


# получение данных для графика и ячеек
def getData31(requst):
    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 00, 0)
        Smena = 1
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 00, 0)
        spotSmena = datetime.time(23, 59, 0)
        Smena = 2
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)
        Smena = 3

    try:

        plan = bottling_plan.objects.filter(Data=datetime.date.today(),
                                            GIUDLine='12ab36dc-0fb9-44d8-b14d-63230bf1c0cd',
                                            ShiftNumber=Smena)

        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan == None:
            plan = 31000
    except:
        plan = 31000

    table31 = Table31.objects.filter(startdata=datetime.date.today(),
                                     starttime__gte=startSmena,
                                     starttime__lte=spotSmena).filter(uchastok="Триблок") | Table31.objects.filter(
        startdata=datetime.date.today(),
        starttime__gte=startSmena,
        starttime__lte=spotSmena).filter(uchastok="Этикетировка")

    speed31 = Speed31.objects.filter(data=datetime.date.today(),
                                     time__gte=startSmena,
                                     time__lte=spotSmena)
    productionOutput31 = ProductionOutput31.objects.filter(data=datetime.date.today(),
                                                           time__gte=startSmena,
                                                           time__lte=spotSmena)

    try:
        count31 = 0
        avg = 0
        for el in speed31:
            if el.triblok != 0:
                count31 += 1
                avg += el.triblok

        avgSpeed31 = round(avg / count31, 2)
    except:
        avgSpeed31 = 0
    try:
        sumProstoy = table31.aggregate(Sum('prostoy')).get('prostoy__sum')

        if (sumProstoy == None):
            sumProstoy = '00:00'
    except:
        sumProstoy = '00:00'
    try:
        sumProduct31 = productionOutput31.aggregate(Sum('production')).get('production__sum')
        if (sumProduct31 == None):
            sumProduct31 = '0'
    except:
        sumProduct31 = 0
    try:
        allProc31 = proc(startSmena, spotSmena, plan, sumProduct31)
    except:
        allProc31 = 0

    lableChart31 = []
    dataChart31_triblok = []
    dataChart31_test = []

    # Получение времени начала и окончания из ProductionTime31
    start_times = list(ProductionTime31.objects.filter(data=datetime.date.today(),
                                                       time__gte=startSmena,
                                                       time__lte=spotSmena)
                       .values_list('time', flat=True))
    prod_name = list(ProductionTime31.objects.filter(data=datetime.date.today(),
                                                     time__gte=startSmena,
                                                     time__lte=spotSmena)
                     .values_list('nameProduct', flat=True))
    # Пустой список для хранения скоростей
    speeds = []

    # Получение скорости для каждого продукта из списка
    for product in prod_name:
        # Получение объекта SetProductionSpeed31 по названию продукта
        production_speed = SetProductionSpeed31.objects.filter(nameProduct=product).first()

        if production_speed:
            # Добавление скорости продукта в список
            speeds.append(production_speed.speed)
        else:
            speeds.append(None)

    end_times = start_times[1:] + [speed31.last().time]
    start_times = [str(time) for time in start_times]
    end_times = [str(time) for time in end_times]

    # Парное объединение элементов двух списков
    merged_list = [(elem1, elem2, elem3, elem4) for elem1, elem2, elem3, elem4 in
                   zip(start_times, end_times, speeds, prod_name)]

    for sp in speed31:
        trig = False
        lableChart31.append(str(sp.time))
        dataChart31_triblok.append(sp.triblok)
        for el in range(0, len(merged_list)):
            if datetime.datetime.strptime(merged_list[el][0], "%H:%M:%S").time() < sp.time \
                    <= datetime.datetime.strptime(merged_list[el][1], "%H:%M:%S").time():
                dataChart31_test.append(merged_list[el][2])
                trig = True

        if not trig:
            dataChart31_test.append(0)

    result = {
        "allProc31": allProc31,
        'sumProstoy31': str(sumProstoy),
        'avgSpeed31': avgSpeed31,
        'sumProduct31': sumProduct31,

        'lableChart31': lableChart31,
        'dataChart31_triblok': dataChart31_triblok,
        'dataChart31_test': dataChart31_test,

    }
    return JsonResponse(result)


def getBtn31(requst):
    buttons_reg = modbus_client.read_input_registers(0)
    result = {
        'buttons_reg': buttons_reg,
    }

    return JsonResponse(result)

def list_nomenklature31 (requst):
    buttons_reg = modbus_client.read_input_registers(0)

    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 00, 0)
        Smena = 1
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 00, 0)
        spotSmena = datetime.time(23, 59, 0)
        Smena = 2
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)
        Smena = 3

    list_nomenklature = []
    list_guid_nomenklature = bottling_plan.objects.filter(
        Data=datetime.date.today(),
        GIUDLine='12ab36dc-0fb9-44d8-b14d-63230bf1c0cd',
        ShiftNumber=Smena).values_list('GUIDNomenсlature', flat=True)

    for e in list_guid_nomenklature:
        list_nomenklature.append(Nomenclature.objects.filter(GUID=e).values('Nomenclature')[0]['Nomenclature'])
    list_nomenklature = list(set(list_nomenklature))
    list_nomenklature.insert(0, "Выберите продукт")

    result = {
        'list_nomenklature': list_nomenklature,
    }

    return JsonResponse(result)
def handle_select_position31(request):
    if request.method == 'POST':
        selected_option = request.POST.get('selected_option')
        print(f'Выбранная позиция: {selected_option}')  # Вывод позиции в консоль

        # Попытка получить объект SetProductionSpeed по полю nameProduct
        production_speed, created = SetProductionSpeed31.objects.get_or_create(nameProduct=selected_option)

        # Если объект был создан, вы можете установить начальное значение скорости
        if created:
            production_speed.speed = 3000  # Установка начальной скорости, если объект был создан
            production_speed.save()

        # Получение значения скорости из объекта
        speed = production_speed.speed
        print(f'Скорость: {speed}')  # Вывод скорости в консоль

        # Добавление времени, даты и выбранного продукта в модель ProductionTime31
        production_time = ProductionTime31.objects.create(
            data=datetime.datetime.today(),
            time=datetime.datetime.now().strftime("%H:%M:%S"),
            nameProduct=selected_option
        )

        return JsonResponse({'message': 'Успешно обработано'})  # Ответ на AJAX-запрос
    else:
        return JsonResponse({'message': 'Метод не поддерживается'})
