import datetime


from django.db.models import Count, Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from temruk.models import bottling_plan, prichina, uchastok
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
slave_address='10.36.20.2'
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
def update33(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        name = request.POST.get('name')
        value = request.POST.get('value')
        if name == "prichina":

            b = Table33.objects.get(id=pk).uchastok
            if b in vid_prostoev["ТО и Переналадки АСУП"]:
                a = Table33.objects.get(id=pk)
                setattr(a, name, value)
                a.save()
                return HttpResponse('yes')
            print(uchastok.objects.all().filter(Guid_Line="d65654f8-2e89-4044-bb10-4342a9d1b722"))
            if b == "Автомат для одевания и обкатки колпака":
                b="Автомат для одевания и обкатки полиламинатной капсулы и термоусадосного колпака"


            v = uchastok.objects.get(Guid_Line="d65654f8-2e89-4044-bb10-4342a9d1b722",
                                     Uchastok__icontains=b).Guid_Uchastok

            try:
                n = "Guid_Uchastok"

                a = Table33.objects.get(id=pk)
                setattr(a, n, v)

            except Table33.DoesNotExist:

                setattr(a, n, v)
            a.save()
            # Запись гуид прицины
            n = "Guid_Prichina"
            v = prichina.objects.get(Prichina=value).Guid_Prichina
            try:
                a = Table33.objects.get(id=pk)
                setattr(a, n, v)

            except Table33.DoesNotExist:
                a = Table33(id=pk, **{n: v})
            a.save()
        if name == "comment" and not Table33.objects.get(id=pk).prichina:
            return HttpResponse('no')

        try:
            a = Table33.objects.get(id=pk)
            setattr(a, name, value)
        except Table33.DoesNotExist:
            a = Table33(id=pk, **{name: value})

        a.save()
        return HttpResponse('yes')



# получение данных в таблицу
def update_items33(request):
    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 00, 0)
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 00, 0)
        spotSmena = datetime.time(23, 59, 0)
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)

    table33 = Table33.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)

    return render(request, 'Line33/table_body33.html', {'table33': table33})


# получение данных для графика и ячеек
def getData33(requst):
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
                                         GIUDLine='d65654f8-2e89-4044-bb10-4342a9d1b722',
                                         ShiftNumber=Smena)
        plan=plan.aggregate(Sum('Quantity')).get('Quantity__sum')
        if plan== None:
            plan=31000
    except:
        plan=31000


    table33 = Table33.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)

    speed33 = Speed33.objects.filter(data=datetime.date.today(),
                                   time__gte=startSmena,
                                   time__lte=spotSmena)
    productionOutput33 = ProductionOutput33.objects.filter(data=datetime.date.today(),
                                                         time__gte=startSmena,
                                                         time__lte=spotSmena)



    try:
        count33 = 0
        avg = 0
        for el in speed33:
            if el.triblok != 0:
                count33 += 1
                avg += el.triblok

        avgSpeed33 = round(avg / count33, 2)
    except:
        avgSpeed33 = 0
    try:
        sumProstoy = table33.aggregate(Sum('prostoy')).get('prostoy__sum')

        if (sumProstoy == None):
            sumProstoy = '00:00'
    except:
        sumProstoy = '00:00'
    try:
        sumProduct33 = productionOutput33.aggregate(Sum('production')).get('production__sum')
        if (sumProduct33 == None):
            sumProduct33= '0'
    except:
        sumProduct33 = 0
    try:
        allProc33 = proc(startSmena, spotSmena, plan, sumProduct33)
    except:
        allProc33 = 0

    lableChart33 = []
    dataChart33_triblok = []
    dataChart33_kapsula = []
    dataChart33_eticetka = []
    dataChart33_ukladchik = []
    dataChart33_zakleichik = []

    for sp in speed33:
        lableChart33.append(str(sp.time))
        dataChart33_triblok.append(sp.triblok)
        dataChart33_kapsula.append(sp.kapsula)
        dataChart33_eticetka.append(sp.eticetka)
        dataChart33_ukladchik.append(sp.ukladchik)
        dataChart33_zakleichik.append(sp.zakleichik)

    result = {
        "allProc33": allProc33,
        'sumProstoy33': str(sumProstoy),
        'avgSpeed33': avgSpeed33,
        'sumProduct33': sumProduct33,

        'lableChart33': lableChart33,
        'dataChart33_triblok': dataChart33_triblok,
        'dataChart33_kapsula': dataChart33_kapsula,
        'dataChart33_eticetka': dataChart33_eticetka,
        'dataChart33_ukladchik': dataChart33_ukladchik,
        'dataChart33_zakleichik': dataChart33_zakleichik,

    }
    return JsonResponse(result)

def getBtn33(requst):
    buttons_reg = modbus_client.read_input_registers(1)
    result = {
        'buttons_reg':buttons_reg
              }
    return JsonResponse(result)
