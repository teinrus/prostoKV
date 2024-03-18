import time
from datetime import datetime
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from temruk.models import bottling_plan

def get_shift_number():
    if 0 <= time.localtime().tm_hour < 8:
        return 3
    elif 8 <= time.localtime().tm_hour < 17:
        if time.localtime().tm_hour < 16 and time.localtime().tm_min <= 29:
            return 1
        elif time.localtime().tm_hour < 16 and time.localtime().tm_min > 29:
            return 2
        return 1
    else:
        return 2


def get_plan_quantity(GIUDLine):
    try:
        today = datetime.datetime.today()
        shift_number = get_shift_number()
        plan = bottling_plan.objects.filter(Data=today, GIUDLine=GIUDLine,
                                            ShiftNumber=shift_number)

        plan_quantity = plan.aggregate(Sum('Quantity'))['Quantity__sum'] or 31000
        return plan_quantity
    except Exception as e:
        return 31000


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

    planNow = planProdSec * diff2.total_seconds()
    try:
        result = int(total_product / planNow * 100)
    except:
        result = 0

    return result


def get_shift_times():
    now_time = time.localtime().tm_hour * 3600 + time.localtime().tm_min * 60 + time.localtime().tm_sec

    if 0 <= now_time < 8 * 3600:
        return datetime.time(0, 0), datetime.time(8, 0)
    elif 8 * 3600 <= now_time < 16 * 3600 + 30 * 60:
        return datetime.time(8, 0), datetime.time(16, 30)
    else:
        return datetime.time(16, 30), datetime.time(23, 59, 59)

def get_shift_times_tiorovka():
    now_time = time.localtime().tm_hour * 3600 + time.localtime().tm_min * 60 + time.localtime().tm_sec

    if 0 <= now_time < 8 * 3600:
        return datetime.time(0, 0), datetime.time(8, 0)
    elif 8 * 3600 <= now_time < 16 * 3600 :
        return datetime.time(8, 0), datetime.time(16, 00)
    else:
        return datetime.time(16, 00), datetime.time(23, 59, 59)


def get_total_product(production_output_queryset):
    sum_product = production_output_queryset.aggregate(Sum('production'))['production__sum']
    return sum_product if sum_product else 0


def get_total_prostoy(table_queryset):
    sum_prostoy = table_queryset.aggregate(Sum('prostoy'))['prostoy__sum']
    return str(sum_prostoy) if sum_prostoy else '00:00'


def get_average_speed(speed_queryset):
    count = 0
    total_speed = 0
    for el in speed_queryset:
        if el.triblok != 0:
            count += 1
            total_speed += el.triblok

    return round(total_speed / count, 2) if count > 0 else 0

def get_boom_out(boom):
    try:
        return boom.aggregate(Sum('bottle')).get('bottle__sum') or 0
    except ObjectDoesNotExist:
        return 0