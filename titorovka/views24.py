import datetime

from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from pyModbusTCP.client import ModbusClient

from temruk.models import bottling_plan, uchastok, prichina, SetProductionSpeed
from titorovka.models import *

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
                    "Переход по этикетке, в/м и бутылке (переход с изменением объема бутылки)"],

    "ТО и Переналадки АСУП": ["ТО",
                              "Доналадка",
                              "Переналадка"]
}
slave_address = '10.36.20.4'

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
def update24(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        value = request.POST.get('value')

        if name == "prichina":
            b = Table24.objects.get(id=pk).uchastok
            if b in vid_prostoev["ТО и Переналадки АСУП"]:
                a = Table24.objects.get(id=pk)
                setattr(a, name, value)
                a.save()
                return HttpResponse('yes')
            if b == "Моноблок автоматический PRISMA":
                b = "Моноблок автоматический для распределения капсул PRISMA"
                v = uchastok.objects.get(Guid_Line="90aef8a3-8edd-4904-b22b-8f53d903f90d",
                                         Uchastok=b).Guid_Uchastok
            else:
                v = uchastok.objects.get(Guid_Line="90aef8a3-8edd-4904-b22b-8f53d903f90d",
                                         Uchastok=b).Guid_Uchastok

            try:
                n = "Guid_Uchastok"

                a = Table24.objects.get(id=pk)
                setattr(a, n, v)

            except Table24.DoesNotExist:

                setattr(a, n, v)
            a.save()
            # Запись гуид прицины
            n = "Guid_Prichina"
            v = prichina.objects.get(Prichina=value).Guid_Prichina
            try:
                a = Table24.objects.get(id=pk)
                setattr(a, n, v)

            except Table24.DoesNotExist:
                a = Table24(id=pk, **{n: v})
            a.save()
        if name == "comment" and not Table24.objects.get(id=pk).prichina:
            return HttpResponse('no')

        try:
            a = Table24.objects.get(id=pk)
            setattr(a, name, value)
        except Table24.DoesNotExist:
            a = Table24(id=pk, **{name: value})

        a.save()
        return HttpResponse('yes')


# получение данных в таблицу
def update_items24(request):
    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 00, 0)
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 00, 0)
        spotSmena = datetime.time(23, 59, 0)
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)

    table24 = Table24.objects.filter(startdata=datetime.date.today(),
                                     starttime__gte=startSmena,
                                     starttime__lte=spotSmena)

    return render(request, 'Line24/table_body24.html', {'table24': table24})


# получение данных для графика и ячеек
def getData24(requst):
    dataChart24_need_speed = []
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
                                            GIUDLine='90aef8a3-8edd-4904-b22b-8f53d903f90d',
                                            ShiftNumber=Smena)
        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan == None:
            plan = 31000
    except:
        plan = 31000

    table24 = Table24.objects.filter(startdata=datetime.date.today(),
                                     starttime__gte=startSmena,
                                     starttime__lte=spotSmena)

    speed24 = Speed24.objects.filter(data=datetime.date.today(),
                                     time__gte=startSmena,
                                     time__lte=spotSmena)
    productionOutput24 = ProductionOutput24.objects.filter(data=datetime.date.today(),
                                                           time__gte=startSmena,
                                                           time__lte=spotSmena)

    try:
        count24 = 0
        avg = 0
        for el in speed24:
            if el.triblok != 0:
                count24 += 1
                avg += el.triblok

        avgSpeed24 = round(avg / count24, 2)
    except:
        avgSpeed24 = 0
    try:
        sumProstoy = table24.aggregate(Sum('prostoy')).get('prostoy__sum')

        if (sumProstoy == None):
            sumProstoy = '00:00'
    except:
        sumProstoy = '00:00'
    try:
        sumProduct24 = productionOutput24.aggregate(Sum('production')).get('production__sum')
        if (sumProduct24 == None):
            sumProduct24 = '0'
    except:
        sumProduct24 = 0
    try:
        allProc24 = proc(startSmena, spotSmena, plan, sumProduct24)
    except:
        allProc24 = 0

    lableChart24 = []
    dataChart24_triblok = []

    for sp in speed24:
        lableChart24.append(str(sp.time))
        dataChart24_triblok.append(sp.triblok)
    # Получение времени начала и окончания из ProductionTime
    start_times = list(ProductionTime24.objects.filter(data=datetime.date.today(),
                                                       time__gte=startSmena,
                                                       time__lte=spotSmena)
                       .values_list('time', flat=True))

    prod_name = list(ProductionTime24.objects.filter(data=datetime.date.today(),
                                                     time__gte=startSmena,
                                                     time__lte=spotSmena)
                     .values_list('type_bottle', flat=True))
    # Пустой список для хранения скоростей
    speeds = []

    # Получение скорости для каждого продукта из списка
    for product in prod_name:
        # Получение объекта SetProductionSpeed31 по названию продукта
        production_speed = SetProductionSpeed.objects.filter(name_bottle=product).filter(line="24").first()

        if production_speed:
            # Добавление скорости продукта в список
            speeds.append(production_speed.speed)
        else:
            speeds.append(None)

    end_times = start_times[1:] + [speed24.last().time]
    start_times = [str(time) for time in start_times]
    end_times = [str(time) for time in end_times]

    # Парное объединение элементов двух списков
    merged_list = [(elem1, elem2, elem3, elem4) for elem1, elem2, elem3, elem4 in
                   zip(start_times, end_times, speeds, prod_name)]

    for sp in speed24:
        trig = False
        for el in range(0, len(merged_list)):
            if datetime.datetime.strptime(merged_list[el][0], "%H:%M:%S").time() < sp.time \
                    <= datetime.datetime.strptime(merged_list[el][1], "%H:%M:%S").time():
                dataChart24_need_speed.append(round(merged_list[el][2], 0) if merged_list[el][2] else 0)
                trig = True

        if not trig:
            dataChart24_need_speed.append(0)
    result = {
        "allProc24": allProc24,
        'sumProstoy24': str(sumProstoy),
        'avgSpeed24': avgSpeed24,
        'sumProduct24': sumProduct24,

        'lableChart24': lableChart24,
        'dataChart24_triblok': dataChart24_triblok,
        'dataChart24_need_speed': dataChart24_need_speed,

    }
    return JsonResponse(result)


def getBtn24(requst):
    buttons_reg = modbus_client.read_input_registers(0)
    result = {
        'buttons_reg': buttons_reg
    }
    return JsonResponse(result)


def select24(request):
    if request.method == 'POST':

        selected_value = request.POST.get('selected_value')

        response_data = {'selected_value': selected_value}
        production_time = ProductionTime24(data=datetime.datetime.today(),
                                           time=datetime.datetime.now().strftime("%H:%M:%S"),
                                           type_bottle=selected_value)
        production_time.save()
        return JsonResponse(response_data)
    else:
        # Вернуть ошибку, если запрос не является POST-запросом или не AJAX-запросом
        return JsonResponse({'error': 'Invalid request'}, status=400)
