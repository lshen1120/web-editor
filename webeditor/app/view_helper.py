# -*- coding:utf-8 -*-
import time,datetime
import utils

#拼接menu_1 和menu_2菜单
def append_menu(respo_dict,menu_1,menu_2):
    if respo_dict is None:
        respo_dict = {}

    if not respo_dict.has_key('menu_1'):
        respo_dict.setdefault('menu_1',menu_1)
    else:
        respo_dict.update('menu_1',menu_1)

    if not respo_dict.has_key('menu_2'):
        respo_dict.setdefault('menu_2',menu_2)
    else:
        respo_dict.update('menu_2',menu_2)

    return respo_dict

def truncate_str(value,cut_size):
    if value is None:
        return value

    if len(value) > cut_size:
        return value[0:cut_size]

    return value

def format_time_stamp(time_stamp, my_format='%Y.%m.%d %H:%M'):
    if time_stamp is None or time_stamp == 0:
        return ''

    return time.strftime(my_format, time.localtime(time_stamp))


def set_str_default(value,my_format=''):
    if value is None:
        value = my_format

    return value


def set_int_default(value, my_default=0):
    if value is None:
        value = my_default
    return value

def get_percent_rate(rate_value):
        if not isinstance(rate_value, float) and not isinstance(rate_value, int):
            return rate_value

        rate_value = abs(rate_value)
        percent = rate_value * 100;
        return str(percent) + "%"


def make_day_end_time(str_date):
    next_day = add_date_time(str_date, '%Y-%m-%d', days=1)
    day_end_time = time.mktime(time.strptime(next_day, '%Y-%m-%d')) - 1
    return int(day_end_time)


def add_date_time(str_date, str_format, days):
    if str_date is None or len(str_date) == 0 :
        return str_date
    origin_date = datetime.datetime.strptime(str_date, str_format)
    origin_date += datetime.timedelta(days=days)

    return origin_date.strftime(str_format)


def get_days(start_date, end_date, str_format='%Y-%m-%d'):
    if start_date is None or len(start_date) ==0 :
        return 0
    if end_date is None or len(end_date) ==0:
        return 0

    start = datetime.datetime.strptime(start_date, str_format)
    end = datetime.datetime.strptime(end_date, str_format)
    delta_time = end - start
    return delta_time.days


#获取本周的开始日期，如果为周一，则返回当前日期
def get_week_start(str_date, str_format='%Y-%m-%d'):
    if str_date is None or len(str_date) == 0:
        return str_date

    #周一.weekday==0,周日.weekday==6
    curr_date = datetime.datetime.strptime(str_date, str_format)
    if curr_date.weekday() == 0:
        #周一
        return str_date

    week_start = curr_date + datetime.timedelta(days=-curr_date.weekday())
    return week_start.strftime(str_format)


#获取时间的月开始时间
def get_month_start(str_date, str_format='%Y-%m-%d'):
    if str_date is None or len(str_date) == 0:
        return str_date
    curr_date = datetime.datetime.strptime(str_date, str_format)
    month_start = curr_date.strftime('%Y-%m-1')
    return month_start


#计算增长率，返回float数
def calculate_grow_percent(curr_value, pre_value):

    curr_value = float(curr_value)
    pre_value = float(pre_value)

    if pre_value < 0:
        pre_value = abs(pre_value)
    if pre_value == 0:
        if curr_value == 0:
            return 0
        else:
            return 1
    if curr_value == 0:
        return -1
    rate = (curr_value - pre_value) / pre_value

    rate = float("%0.4f" % rate)

    return rate


def get_obj_field(obj, field_name, default):
    if obj is None:
        return default
    return obj.get(field_name, default)


def replace_with_star(str_value, star_num):
    str_value = utils.decode(str_value)
    if str_value is None or len(str_value) < 2:
        return str_value

    if len(str_value) <= star_num:
        return str_value

    result = [str_value[0: -1*star_num-1]]
    for i in range(0, star_num):
        result.append("*")
    result.append(str_value[-1])

    return ''.join(result)


def get_obj_id_array(objs, field):
    if objs is None:
        return []

    result = []
    for one in objs:
        a_value = one.get(field, '')
        result.append(str(a_value))
    return result


def sum_field(objs, field):
    if objs is None:
        return 0
    total = 0
    for one in objs:
        total += one.get(field, 0)

    return total


def compare_date(one_date, another_date):
    str_format = '%Y-%m-%d'
    one_time = time.mktime(time.strptime(one_date, str_format))
    another_time = time.mktime(time.strptime(another_date, str_format))
    if one_time > another_time:
        return 1
    elif one_time == another_time:
        return 0
    return -1


def empty(value):
    if value is None:
        return True
    value = value.strip()
    if len(value) == 0:
        return True
    return False


def replace_sql_chars(search_value, ignore_char=None):
    if search_value is None or len(search_value) == 0:
        return search_value
    special_chars = ["'", "<", ">", "%", "\"", ",", ".", ">=", "=<", "<>", "-", ";", "||", "[", "]", "&", "/", "-", "|", " "]
    for one in special_chars:
        if ignore_char is not None and one in ignore_char:
            continue
        search_value = search_value.replace(one, '')

    return search_value


def convert_float(value, point=2):
    if value is None:
        return 0
    if value % 1 == 0:
        return int(value)
    format_str = "%0.{}f".format(point)
    return float(format_str % value)