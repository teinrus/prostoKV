import datetime

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from django.db.models import Sum, Avg

from django.shortcuts import render, redirect

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

# стартовая страница
def index(request):
    if request.method == 'GET':
        user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if user_ip:
            ip = user_ip.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    ipMask=ip.split('.')
    if ipMask[2] =="97":
        return redirect('temruk')
    else:
        return redirect('titorovka')



def temruk(request):
    if request.method == 'GET':
        table5 = Table5.objects.filter(startdata=datetime.date.today(),
                                      starttime__gte=startSmena,
                                      starttime__lte=spotSmena)
        speed5 = Speed5.objects.filter(data=datetime.date.today(),
                                      time__gte=startSmena,
                                      time__lte=spotSmena)
        table4 = Table4.objects.filter(startdata=datetime.date.today(),
                                      starttime__gte=startSmena,
                                      starttime__lte=spotSmena)
        speed4 = Speed4.objects.filter(data=datetime.date.today(),
                                      time__gte=startSmena,
                                      time__lte=spotSmena)
        table2 = Table2.objects.filter(startdata=datetime.date.today(),
                                       starttime__gte=startSmena,
                                       starttime__lte=spotSmena)
        speed2 = Speed2.objects.filter(data=datetime.date.today(),
                                       time__gte=startSmena,
                                       time__lte=spotSmena)

    prichAll=prichina.objects.all()
    podrazdeleniaEl=[]
    for el in prichAll:
        podrazdeleniaEl.append(el.key)
    otv_p=set(podrazdeleniaEl)

    prich = list(prichAll.values())
    uch = uchastok.objects.all()
    uch_vino=uchastok.objects.exclude(uchastok="Мюзле")
    return render(request, "temruk.html", {

        'otv_p':otv_p ,
        'prich': prich,
        'uch': uch,
        'uch_vino': uch_vino,

        'table5': table5,
        'speed5': speed5,

        'table4': table4,
        'speed4': speed4,

        'table2': table2,
        'speed2': speed2,

    })


# блок формирования отчета
def otchet(request):
    plan=0
    timeTemp = 0
    form = Otchet(request.GET)
    if form.is_valid():
        # Сортировка по дате
        if form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 5'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    table = Table5.objects.filter(starttime__gte=datetime.time(0),
                                                  starttime__lte=datetime.time(23, 59),
                                                  startdata__gte=form.cleaned_data["start_data"],
                                                  startdata__lte=form.cleaned_data["finish_data"]
                                                  ).order_by('startdata', 'starttime')

                    speed = Speed5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(0),
                                                  time__lte=datetime.time(23, 59))
                    boom = bottleExplosion.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                          data__lte=form.cleaned_data["finish_data"],
                                                          time__gte=datetime.time(0),
                                                          time__lte=datetime.time(23, 59))
                    prod = ProductionOutput5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(0),
                                                  time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                                            )
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data[
                            "start_data"] + datetime.timedelta(days=1)



                    except:
                        timeTemp = 0

        if form.cleaned_data["SmenaF"] == 'Смена 1':
            table = Table5.objects.filter(starttime__gte=datetime.time(8),
                                          starttime__lte=datetime.time(16, 30),
                                          startdata__gte=form.cleaned_data["start_data"],
                                          startdata__lte=form.cleaned_data["finish_data"]
                                          ).order_by('startdata', 'starttime')
            speed = Speed5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                          data__lte=form.cleaned_data["finish_data"],
                                          time__gte=datetime.time(8),
                                          time__lte=datetime.time(16, 30))
            boom = bottleExplosion.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(8),
                                                  time__lte=datetime.time(16, 30))
            prod = ProductionOutput5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                          data__lte=form.cleaned_data["finish_data"],
                                          time__gte=datetime.time(8),
                                          time__lte=datetime.time(16, 30))
            try:
                plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                    Data__lte=form.cleaned_data["finish_data"],
                                                    GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                                    ShiftNumber=1)
                plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
            except:
                plan = 0

            try:
                timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                count=1+timeTemp.total_seconds()/3600/24
                timeTemp=datetime.timedelta(hours=(8*count),minutes=30*count)
            except:
                timeTemp = 0
        if form.cleaned_data["SmenaF"] == 'Смена 2':
            table = Table5.objects.filter(starttime__gte=datetime.time(16, 30),
                                          starttime__lte=datetime.time(23, 59),
                                          startdata__gte=form.cleaned_data["start_data"],
                                          startdata__lte=form.cleaned_data["finish_data"]
                                          ).order_by('startdata', 'starttime')
            speed = Speed5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                          data__lte=form.cleaned_data["finish_data"],
                                          time__gte=datetime.time(16, 30),
                                          time__lte=datetime.time(23, 59))
            boom = bottleExplosion.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(16, 30),
                                                  time__lte=datetime.time(23, 59))
            prod = ProductionOutput5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                          data__lte=form.cleaned_data["finish_data"],
                                          time__gte=datetime.time(16, 30),
                                          time__lte=datetime.time(23, 59))
            try:
                plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                    Data__lte=form.cleaned_data["finish_data"],
                                                    GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                                    ShiftNumber=2)
                plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
            except:
                plan = 0

            try:
                timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                count=timeTemp.total_seconds()/3600/24+1

                timeTemp=datetime.timedelta(hours=(7*count),minutes=30*count)
            except:
                timeTemp = 0
        if form.cleaned_data["SmenaF"] == 'Смена 3':
            table = Table5.objects.filter(starttime__gte=datetime.time(00, 00),
                                          starttime__lte=datetime.time(8, 00),
                                          startdata__gte=form.cleaned_data["start_data"],
                                          startdata__lte=form.cleaned_data["finish_data"]
                                          ).order_by('startdata', 'starttime')
            speed = Speed5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                          data__lte=form.cleaned_data["finish_data"],
                                          time__gte=datetime.time(00, 00),
                                          time__lte=datetime.time(8, 00))
            boom = bottleExplosion.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                  data__lte=form.cleaned_data["finish_data"],
                                                  time__gte=datetime.time(00, 00),
                                                  time__lte=datetime.time(8, 00))
            prod = ProductionOutput5.objects.filter(data__gte=form.cleaned_data["start_data"],
                                          data__lte=form.cleaned_data["finish_data"],
                                          time__gte=datetime.time(00, 00),
                                          time__lte=datetime.time(8, 00))
            try:
                plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                    Data__lte=form.cleaned_data["finish_data"],
                                                    GIUDLine='22b8afd6-110a-11e6-b0ff-005056ac2c77',
                                                    ShiftNumber=3)
                plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
            except:
                plan = 0

            try:
                timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                count=timeTemp.total_seconds()/3600/24+1

                timeTemp=datetime.timedelta(hours=(8*count))
            except:
                timeTemp = 0
        # Сортировка по сменам линии 2:
        if form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 2'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    table2 = Table2.objects.filter(starttime__gte=datetime.time(0),
                                                   starttime__lte=datetime.time(23, 59),
                                                   startdata__gte=form.cleaned_data["start_data"],
                                                   startdata__lte=form.cleaned_data["finish_data"]
                                                   ).order_by('startdata', 'starttime')

                    speed2 = Speed2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(0),
                                                   time__lte=datetime.time(23, 59))
                    productionOutput2 = ProductionOutput2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(0),
                                                   time__lte=datetime.time(23, 59))
                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77')
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0

                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data[
                            "start_data"] + datetime.timedelta(days=1)
                    except:
                        timeTemp = 0
            if form.cleaned_data["SmenaF"] == 'Смена 1':
                table2 = Table2.objects.filter(starttime__gte=datetime.time(8),
                                               starttime__lte=datetime.time(16, 30),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed2 = Speed2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(8),
                                               time__lte=datetime.time(16, 30))
                productionOutput2 = ProductionOutput2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(8),
                                               time__lte=datetime.time(16, 30))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=1)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan=0
                try:

                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(8*count),minutes=30*count)
                except:
                    timeTemp = 0
            if form.cleaned_data["SmenaF"] == 'Смена 2':
                table2 = Table2.objects.filter(starttime__gte=datetime.time(16, 30),
                                               starttime__lte=datetime.time(23, 59),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed2 = Speed2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(16, 30),
                                               time__lte=datetime.time(23, 59))
                productionOutput2 = ProductionOutput2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(16, 30),
                                               time__lte=datetime.time(23, 59))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=2)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan=0

                try:

                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(7*count),minutes=30*count)
                except:
                    timeTemp = 0


            if form.cleaned_data["SmenaF"] == 'Смена 3':
                table2 = Table2.objects.filter(starttime__gte=datetime.time(00, 00),
                                               starttime__lte=datetime.time(8, 00),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed2 = Speed2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(00, 00),
                                               time__lte=datetime.time(8, 00))
                productionOutput2 = ProductionOutput2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(00, 00),
                                               time__lte=datetime.time(8, 00))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='48f7e8d8-1114-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=3)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan=0
                try:
                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(8 * count))
                except:
                    timeTemp = 0

            table=table2
            speed=speed2
            prod=productionOutput2
            boom=0
        if form.cleaned_data["start_data"] and form.cleaned_data["finish_data"] and (
                form.cleaned_data["LineF"] == 'Линиия 4'):
            if form.cleaned_data["SmenaF"]:
                if form.cleaned_data["SmenaF"] == 'Смена 0':
                    table4 = Table4.objects.filter(starttime__gte=datetime.time(0),
                                                   starttime__lte=datetime.time(23, 59),
                                                   startdata__gte=form.cleaned_data["start_data"],
                                                   startdata__lte=form.cleaned_data["finish_data"]
                                                   ).order_by('startdata', 'starttime')

                    speed4 = Speed4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(0),
                                                   time__lte=datetime.time(23, 59))
                    productionOutput4 = ProductionOutput2.objects.filter(data__gte=form.cleaned_data["start_data"],
                                                   data__lte=form.cleaned_data["finish_data"],
                                                   time__gte=datetime.time(0),
                                                   time__lte=datetime.time(23, 59))

                    try:
                        plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                            Data__lte=form.cleaned_data["finish_data"],
                                                            GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77')
                        plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                    except:
                        plan = 0
                    try:
                        timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data[
                            "start_data"] + datetime.timedelta(days=1)


                    except:
                        timeTemp = 0
            if form.cleaned_data["SmenaF"] == 'Смена 1':
                table4 = Table4.objects.filter(starttime__gte=datetime.time(8),
                                               starttime__lte=datetime.time(16, 30),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed4 = Speed4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(8),
                                               time__lte=datetime.time(16, 30))
                productionOutput4 = ProductionOutput4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(8),
                                               time__lte=datetime.time(16, 30))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=1)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0
                try:
                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(8*count),minutes=30*count)
                except:
                    timeTemp = 0
            if form.cleaned_data["SmenaF"] == 'Смена 2':
                table4 = Table4.objects.filter(starttime__gte=datetime.time(16, 30),
                                               starttime__lte=datetime.time(23, 59),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed4 = Speed4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(16, 30),
                                               time__lte=datetime.time(23, 59))
                productionOutput4 = ProductionOutput4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(16, 30),
                                               time__lte=datetime.time(23, 59))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=2)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0
                try:
                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(7*count),minutes=30*count)
                except:
                    timeTemp = 0


            if form.cleaned_data["SmenaF"] == 'Смена 3':
                table4 = Table4.objects.filter(starttime__gte=datetime.time(00, 00),
                                               starttime__lte=datetime.time(8, 00),
                                               startdata__gte=form.cleaned_data["start_data"],
                                               startdata__lte=form.cleaned_data["finish_data"]
                                               ).order_by('startdata', 'starttime')
                speed4 = Speed4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(00, 00),
                                               time__lte=datetime.time(8, 00))
                productionOutput4 = ProductionOutput4.objects.filter(data__gte=form.cleaned_data["start_data"],
                                               data__lte=form.cleaned_data["finish_data"],
                                               time__gte=datetime.time(00, 00),
                                               time__lte=datetime.time(8, 00))
                try:
                    plan = bottling_plan.objects.filter(Data__gte=form.cleaned_data["start_data"],
                                                        Data__lte=form.cleaned_data["finish_data"],
                                                        GIUDLine='b84d1e71-1109-11e6-b0ff-005056ac2c77',
                                                        ShiftNumber=3)
                    plan = plan.aggregate(Sum('Quantity')).get('Quantity__sum')
                except:
                    plan = 0
                try:
                    timeTemp = form.cleaned_data["finish_data"] - form.cleaned_data["start_data"]
                    count = timeTemp.total_seconds() / 3600 / 24 + 1

                    timeTemp = datetime.timedelta(hours=(8 * count))
                except:
                    timeTemp = 0

            table=table4
            speed=speed4
            prod=productionOutput4
            boom=0
    lableChart = []
    dataChart = []

    #Общее количество  продукции
    try:
        allProd = prod.aggregate(Sum('production')).get('production__sum')
        if (allProd == None):
            allProd = 0
    except:
        allProd = 0


    #Общее количество  врывов бутылок
    try:
        boomOut = boom.aggregate(Sum('bottle')).get('bottle__sum')
        if (boomOut == None):
            boomOut = 0
    except:
        boomOut = 0

    #Общее время простоя
    try:
        sumProstoy = table.aggregate(Sum('prostoy')).get('prostoy__sum')
        if sumProstoy== None:
            sumProstoy=datetime.timedelta(0)
    except:
        table = []
        sumProstoy = 0
    # Средняя скорость
    try:
        timeWork=(timeTemp -sumProstoy)
    except:
        timeWork=0
    try:
        avgSpeed =round((allProd / timeWork.total_seconds() * 3600),2)

    except:
        avgSpeed=0

    try:
        for sp in speed:
            lableChart.append(str(sp.time))
            dataChart.append(sp.speed)
    except:
        lableChart = []
        dataChart = []


    # Данные для графика
    if form.cleaned_data["LineF"] == 'Линиия 4' or form.cleaned_data["LineF"] == 'Линиия 5':
        try:
            for sp in speed:
                lableChart.append(str(sp.time))
                dataChart.append(sp.triblok)
        except:
            lableChart = []
            dataChart = []




    uch = uchastok.objects.all()
    uch_vino=uchastok.objects.exclude(uchastok="Мюзле")

    prichAll = prichina.objects.all()
    podrazdeleniaEl = []
    for el in prichAll:
        podrazdeleniaEl.append(el.key)
    otv_p = set(podrazdeleniaEl)

    prich = list(prichAll.values())

    line = form.cleaned_data["LineF"]
    smena=form.cleaned_data["SmenaF"]
    nachaloOt = form.cleaned_data["start_data"]
    okonchanieOt = form.cleaned_data["finish_data"]



    return render(request, "otchet.html", {
        'table': table,
        'form': form,


        'line':line,
        'smena':smena,
        'nachaloOt':nachaloOt,
        'okonchanieOt':okonchanieOt,

        'timeWork':timeWork,
        'plan':plan,
        'sumProstoy': sumProstoy,

        'avgSpeed': avgSpeed,


        'boomOut': boomOut,
        'allProd': allProd,

        'lableChart': lableChart,
        'dataChart': dataChart,

        'otv_p': otv_p,
        'prich': prich,
        'uch': uch,
        'uch_vino':uch_vino,



    })







# блок аунтефикации
@login_required
def profile_view(request):
    return render(request, 'registration/profile.html')
def profileOut_view(request):
    logout(request)
    if request.method == 'GET':
        user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if user_ip:
            ip = user_ip.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    ipMask = ip.split('.')
    if ipMask[2] == "97":
        return redirect('temruk')
    else:
        return redirect('titorovka')


