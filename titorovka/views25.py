import datetime


from django.db.models import Count, Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from temruk.models import bottling_plan, prichina, uchastok, SetProductionSpeed
from titorovka.models import *
from  pyModbusTCP.client import ModbusClient

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

    "ТО и Переналадки АСУП":["ТО",
                        "Доналадка",
                        "Переналадка"]
}
slave_address='10.36.20.4'

unit_id = 1
modbus_client = ModbusClient(host=slave_address, unit_id=unit_id,auto_open=True)

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
def update25(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        value = request.POST.get('value')
        if name == "prichina":
            b = Table25.objects.get(id=pk).uchastok
            if b in vid_prostoev["ТО и Переналадки АСУП"]:
                a = Table25.objects.get(id=pk)
                setattr(a, name, value)
                a.save()
                return HttpResponse('yes')
            v = uchastok.objects.get(Guid_Line="33b39bdb-a94a-4baf-bf9c-31ab906efb9e",
                                     Uchastok=b).Guid_Uchastok

            try:
                n = "Guid_Uchastok"

                a = Table25.objects.get(id=pk)
                setattr(a, n, v)

            except Table25.DoesNotExist:

                setattr(a, n, v)
            a.save()
            # Запись гуид прицины
            n = "Guid_Prichina"
            v = prichina.objects.get(Prichina=value).Guid_Prichina
            try:
                a = Table25.objects.get(id=pk)
                setattr(a, n, v)

            except Table25.DoesNotExist:
                a = Table25(id=pk, **{n: v})
            a.save()
        if name == "comment" and not Table25.objects.get(id=pk).prichina:
            return HttpResponse('no')

        try:
            a = Table25.objects.get(id=pk)
            setattr(a, name, value)
        except Table25.DoesNotExist:
            a = Table25(id=pk, **{name: value})

        a.save()
        return HttpResponse('yes')


# получение данных в таблицу
def update_items25(request):
    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 00, 0)
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 00, 0)
        spotSmena = datetime.time(23, 59, 0)
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)

    table25 = Table25.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)

    return render(request, 'Line25/table_body25.html', {'table25': table25})


# получение данных для графика и ячеек
def getData25(requst):
    dataChart25_need_speed = []
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
                                         GIUDLine='33b39bdb-a94a-4baf-bf9c-31ab906efb9e',
                                         ShiftNumber=Smena)
        plan=plan.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan== None:
            plan=31000
    except:
        plan=31000


    table25 = Table25.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)

    speed25 = Speed25.objects.filter(data=datetime.date.today(),
                                   time__gte=startSmena,
                                   time__lte=spotSmena)
    productionOutput25 = ProductionOutput25.objects.filter(data=datetime.date.today(),
                                                         time__gte=startSmena,
                                                         time__lte=spotSmena)



    try:
        count25 = 0
        avg = 0
        for el in speed25:
            if el.triblok != 0:
                count25 += 1
                avg += el.triblok

        avgSpeed25 = round(avg / count25, 2)
    except:
        avgSpeed25 = 0
    try:
        sumProstoy = table25.aggregate(Sum('prostoy')).get('prostoy__sum')

        if (sumProstoy == None):
            sumProstoy = '00:00'
    except:
        sumProstoy = '00:00'
    try:
        sumProduct25 = productionOutput25.aggregate(Sum('production')).get('production__sum')
        if (sumProduct25 == None):
            sumProduct25= '0'
    except:
        sumProduct25 = 0
    try:
        allProc25 = proc(startSmena, spotSmena, plan, sumProduct25)
    except:
        allProc25 = 0

    lableChart25 = []
    dataChart25_triblok = []


    for sp in speed25:
        lableChart25.append(str(sp.time))
        dataChart25_triblok.append(sp.triblok)

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

    end_times = start_times[1:] + [speed25.last().time]
    start_times = [str(time) for time in start_times]
    end_times = [str(time) for time in end_times]

    # Парное объединение элементов двух списков
    merged_list = [(elem1, elem2, elem3, elem4) for elem1, elem2, elem3, elem4 in
                   zip(start_times, end_times, speeds, prod_name)]

    for sp in speed25:
        trig = False
        for el in range(0, len(merged_list)):
            if datetime.datetime.strptime(merged_list[el][0], "%H:%M:%S").time() < sp.time \
                    <= datetime.datetime.strptime(merged_list[el][1], "%H:%M:%S").time():
                dataChart25_need_speed.append(round(merged_list[el][2] , 0) if merged_list[el][2] else 0)
                trig = True

        if not trig:
            dataChart25_need_speed.append(0)
    result = {
        "allProc25": allProc25,
        'sumProstoy25': str(sumProstoy),
        'avgSpeed25': avgSpeed25,
        'sumProduct25': sumProduct25,

        'lableChart25': lableChart25,
        'dataChart25_triblok': dataChart25_triblok,
        'dataChart25_need_speed': dataChart25_need_speed,


    }
    return JsonResponse(result)

def getBtn25(requst):
    buttons_reg = modbus_client.read_input_registers(1)
    result = {
        'buttons_reg':buttons_reg
              }
    return JsonResponse(result)

def select25(request):
    if request.method == 'POST':

        selected_value = request.POST.get('selected_value')

        response_data = {'selected_value': selected_value}
        production_time = ProductionTime25(data=datetime.datetime.today(),
                                           time=datetime.datetime.now().strftime("%H:%M:%S"),
                                           type_bottle=selected_value)
        production_time.save()
        return JsonResponse(response_data)
    else:
        # Вернуть ошибку, если запрос не является POST-запросом или не AJAX-запросом
        return JsonResponse({'error': 'Invalid request'}, status=400)
