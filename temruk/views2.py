import datetime

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from django.db.models import Count, Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from temruk.models import *

from .forms import Otchet

start1 = datetime.time(8, 00, 0)
start2 = datetime.time(16, 30, 0)
start3 = datetime.time(23, 59, 0)

if start1 <= datetime.datetime.now().time() <= start2:
    startSmena = datetime.time(8, 00, 0)
    spotSmena = datetime.time(16, 30, 0)
elif start2 <= datetime.datetime.now().time() <= start3:
    startSmena = datetime.time(16, 30, 0)
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
    planProdSec = int(plan / int(diff1.total_seconds()))

    # количество времени которое прошло
    d_start2 = datetime.datetime.combine(today, startSmena)
    d_end2 = datetime.datetime.combine(today, datetime.datetime.now().time())
    diff2 = d_end2 - d_start2

    # проц вып продукции
    return int(colProduct / ((int(diff2.total_seconds()) * planProdSec) / 100))

#изменение в таблице
def update2(request):
    if request.method == 'POST':

        pk = request.POST.get('pk')
        name = request.POST.get('name')
        v = request.POST.get('value')

        if name == 'uchastok':
            try:
                a = Table2.objects.get(id=pk)
                a.uchastok = v
                a.save()
            except:
                a = Table2(uchastok=v, id=pk)
                a.save()
        elif name == 'prichina':
            try:

                a = Table2.objects.get(id=pk)
                a.prichina = v
                a.save()
            except:
                a = Table2(prichina=v, id=pk)
                a.save()
        elif name == 'otv_pod':
            try:
                a = Table2.objects.get(id=pk)
                a.otv_pod = v
                a.save()
            except:
                a = Table2(otv_pod=v, id=pk)
                a.save()
        elif name == 'comment':
            try:
                a = Table2.objects.get(id=pk)
                a.comment = v
                a.save()
            except:
                a = Table2(comment=v, id=pk)
                a.save()

    return HttpResponse('yes')

# получение данных в таблицу
def update_items2(request):
    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 30, 0)
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 30, 0)
        spotSmena = datetime.time(23, 59, 0)
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)

    table2 = Table2.objects.filter(startdata=datetime.date.today(),
                                   starttime__gte=startSmena,
                                   starttime__lte=spotSmena)
    # plan = bottling_plan.objects.filter(Data=datetime.date.today(),
    #                                ShiftNumber=2,
    #                                BottlingLine='Линия розлива шампанских и игрист бутылка (Темрюк)')
    #
    # planTest=plan.aggregate(Sum('Quantity')).get('Quantity__sum')
    # print(planTest)
    list = []
    for table in table2:
        table_info = {
            'id': table.id,
            'startdata': table.startdata,
            'starttime': table.starttime,
            'prostoy': table.prostoy,

            'uchastok': table.uchastok,
            'otv_pod': table.otv_pod,
            'prichina': table.prichina,
            'comment': table.comment,
        }
        list.append(table_info)

    table_dic = {}
    table_dic['data'] = list

    return render(request, 'Line2/table_body2.html', {'table2': table2})

# получение данных для графика и ячеек
def getData2(requst):

    plan = 31500

    if start1 <= datetime.datetime.now().time() <= start2:
        startSmena = datetime.time(8, 00, 0)
        spotSmena = datetime.time(16, 30, 0)
    elif start2 <= datetime.datetime.now().time() <= start3:
        startSmena = datetime.time(16, 30, 0)
        spotSmena = datetime.time(23, 59, 0)
    else:
        startSmena = datetime.time(00, 00, 00)
        spotSmena = datetime.time(8, 00, 00)

    table2 = Table2.objects.filter(startdata=datetime.date.today(),
                                  starttime__gte=startSmena,
                                  starttime__lte=spotSmena)
    speed2 = Speed2.objects.filter(data=datetime.date.today(),
                                  time__gte=startSmena,
                                  time__lte=spotSmena)
    productionOutput2=ProductionOutput2.objects.filter(data=datetime.date.today(),
                                  time__gte=startSmena,
                                  time__lte=spotSmena)

    try:
        count2=0
        avg=0
        for el in speed2:
            if el.speed!=0:
                count2+=1
                avg+=el.speed

        avgSpeed = round(avg/count2, 2)
    except:
        avgSpeed = 0
    try:
        sumProstoy = table2.aggregate(Sum('prostoy')).get('prostoy__sum')

        if (sumProstoy == None):
            sumProstoy = '00:00'
    except:
        sumProstoy = '00:00'
    try:
        sumProduct2 = productionOutput2.aggregate(Sum('production')).get('production__sum')
        allProc2 = proc(startSmena, spotSmena, plan, sumProduct2),
    except:
        sumProduct2 = 0
        allProc2 = 0



    lableChart2 = []
    dataChart2 = []

    for sp in speed2:
        lableChart2.append(str(sp.time))
        dataChart2.append(sp.speed)

    result = {
            "allProc2": allProc2,
            'sumProstoy2': str(sumProstoy),
            'avgSpeed2': avgSpeed,
            'sumProduct2':sumProduct2,

            'lableChart2': lableChart2,
            'dataChart2': dataChart2,

              }
    return JsonResponse(result)
