# -*- coding: utf-8 -*-

import os
import hashlib
import re
import string
import math
import random
import datetime
import sys


def is_valid_mobile_phone_number(phone_number):
    return phone_number and len(phone_number) == 11 \
           and re.compile(r"^(13|15|17|18)\d{9}$").match(phone_number) is not None


def rand_code(code_length=6, digits_only=False):
    codes = string.digits if digits_only is True else string.ascii_letters + string.digits
    return ''.join(random.sample(codes, code_length))


def split_to_int(s, delimiter=','):
    """
    使用指定分隔符将字符串分割为整数列表
    :type s: str
    :type delimiter: str
    :rtype: list
    """
    return map(int, s.split(delimiter)) if s else []


ll2mc_factors = [[-0.00157021024440, 1.113207020616939e+005,
                  1.704480524535203e+015, -1.033898737604234e+016,
                  2.611266785660388e+016, -3.514966917665370e+016,
                  2.659570071840392e+016, -1.072501245418824e+016,
                  1.800819912950474e+015, 82.50000000000000],
                 [8.277824516172526e-004, 1.113207020463578e+005,
                  6.477955746671608e+008, -4.082003173641316e+009,
                  1.077490566351142e+010, -1.517187553151559e+010,
                  1.205306533862167e+010, -5.124939663577472e+009,
                  9.133119359512032e+008, 67.50000000000000],
                 [0.00337398766765, 1.113207020202162e+005,
                  4.481351045890365e+006, -2.339375119931662e+007,
                  7.968221547186455e+007, -1.159649932797253e+008,
                  9.723671115602145e+007, -4.366194633752821e+007,
                  8.477230501135234e+006, 52.50000000000000],
                 [0.00220636496208, 1.113207020209128e+005,
                  5.175186112841131e+004, 3.796837749470245e+006,
                  9.920137397791013e+005, -1.221952217112870e+006,
                  1.340652697009075e+006, -6.209436990984312e+005,
                  1.444169293806241e+005, 37.50000000000000],
                 [-3.441963504368392e-004, 1.113207020576856e+005,
                  2.782353980772752e+002, 2.485758690035394e+006,
                  6.070750963243378e+003, 5.482118345352118e+004,
                  9.540606633304236e+003, -2.710553267466450e+003,
                  1.405483844121726e+003, 22.50000000000000],
                 [-3.218135878613132e-004, 1.113207020701615e+005,
                  0.00369383431289, 8.237256402795718e+005,
                  0.46104986909093, 2.351343141331292e+003,
                  1.58060784298199, 8.77738589078284,
                  0.37238884252424, 7.45000000000000]]

llband = [75, 60, 45, 30, 15, 0]


def ll2mc(longitude, latitude):
    """
    坐标转换，算法来自 Android 应用的代码。(CoordtransHelper)
    """
    if longitude > 180.0:
        longitude = 180.0
    elif longitude < -180.0:
        longitude = -180.0

    if 0.0 <= latitude < 1E-7:
        latitude = 1E-7
    elif -1.0E-7 < latitude < 0:
        latitude = -1E-7
    elif latitude > 74:
        latitude = 74
    elif latitude < -74:
        latitude = -74

    factor = [0] * 10
    latitude_abs = abs(latitude)
    for i in range(len(llband)):
        if latitude_abs > llband[i]:
            factor = ll2mc_factors[i]
            break

    to_longitude = factor[0] + factor[1] * abs(longitude)
    temp = abs(latitude) / factor[9]
    to_latitude = 0
    for i in range(2, 9):
        to_latitude += factor[i] * pow(temp, (i - 2))

    if longitude < 0:
        to_longitude *= -1
    if latitude < 0:
        to_latitude *= -1

    return to_longitude, to_latitude


def calc_distance_between_two_pos(from_pos, to_pos):
    int_factor = 1000000.0  # 存储的坐标都是整数，乘了100w. 还原

    from_lng = from_pos.get('lng', 0) / int_factor
    from_lat = from_pos.get('lat', 0) / int_factor
    from_lng, from_lat = ll2mc(from_lng, from_lat)

    to_lng = to_pos.get('lng', 0) / int_factor
    to_lat = to_pos.get('lat', 0) / int_factor

    to_lng, to_lat = ll2mc(to_lng, to_lat)

    distance = math.sqrt((from_lng - to_lng) ** 2 + (from_lat - to_lat) ** 2)

    return distance


def cast_int(value, default=0):
    try:
        return int(value)
    except:
        return default


SECONDS_PER_DAY = 24 * 60 * 60


def get_today_remain_seconds():
    now = datetime.datetime.now()
    beginning_of_day = datetime.datetime.combine(now, datetime.time(second=1))
    passed = (now - beginning_of_day).seconds
    remain_seconds = max(SECONDS_PER_DAY - passed, 0)

    return remain_seconds


def find_python_modules(modules, dir_name):
    files = os.listdir(dir_name)
    for f in files:
        file_path = os.path.abspath(os.path.join(dir_name, f))
        if os.path.isdir(file_path):
            if os.path.isfile(os.path.join(file_path, "__init__.py")):
                find_python_modules(modules, file_path)
            continue
        if not f.endswith(".py"):
            continue
        file_path = file_path[len(os.path.abspath(".")):]
        modules.append(file_path[1:-3].replace(os.path.sep, "."))
    return modules


def load_module(module_name, base_dir='', fromlist=[]):
    if not module_name:
        return None
    module_path = os.path.join(base_dir, module_name.replace('.', os.path.sep))
    isdir = os.path.isdir(module_path)
    if not isdir:
        module_path += '.py'
        if not os.path.isfile(module_path):
            return None
    if module_name in sys.modules:
        del sys.modules[module_name]
    m = __import__(module_name, globals=globals(), fromlist=fromlist)
    if not m:
        return None
    subs = module_name.split(".")
    for x in xrange(len(subs) - 1):
        m = getattr(m, subs[x + 1])
        if not m:
            return None
    return m


def decode(s):
    if type(s) is not type(''): return s
    try:
        decoded_s = s.decode('utf-8')
    except:
        try:
            decoded_s = s.decode('gb18030')
        except:
            decoded_s = s.decode('gb2312')
    return decoded_s


def encode_utf8(val):
    if isinstance(val, unicode):
        return val.encode("utf8")
    return val


def get_value_if_not_none(value, default):
    if value is not None:
        return value
    return default


def print_utf8_obj(val):
    if not isinstance(val, (dict, list)):
        sys.stdout.write(val)
        return
    if isinstance(val, list):
        if len(val) == 1:
            print_utf8_obj(val[0])
            return
        arr = []
        for item in val:
            arr.append(encode_utf8(item))
        sys.stdout.write("[\n\t{}\n]".format(",\n\t".join(arr)))
        return
    arr = []
    for name, value in sorted(val.iteritems()):
        arr.append("{}: {}".format(name, encode_utf8(value)))
    sys.stdout.write("{{\n\t{}\n}}".format(",\n\t".join(arr)))


"""
    实现工作日的 iter, 从start_date 到 end_date , 如果在工作日内,计数器加1
"""


def get_workdays(start_date, end_date, hodidays=0, days_off=None):
    if days_off is None:
        days_off = 5, 6

    workdays = [x for x in range(7) if x not in days_off]

    # 还没排除法定节假日
    tag_date = start_date
    work_count = 0
    while True:
        if tag_date > end_date:
            break
        if tag_date.weekday() in workdays:
            work_count += 1
        tag_date += datetime.timedelta(days=1)

    return work_count - hodidays


# TODO:删除掉view_helper类中的方法
def convert_float(value, point=2):
    if value is None:
        return 0
    if value % 1 == 0:
        return int(value)
    format_str = "%0.{}f".format(point)
    return float(format_str % value)


def format_ten_thousand(value, point=0, comma_separate=False):
    if value == 0:
        return 0
    if value < 10000:
        return value

    format_value = value / 10000
    if point == 0:
        if comma_separate:
            if format_value % 1 == 0:
                return "{}万".format('{:,}'.format(int(format_value)))
            return "{}万".format('{:,}'.format(format_value))
        else:
            if format_value % 1 == 0:
                return "{}万".format(int(format_value))
            return "{}万".format(format_value)
    else:

        if comma_separate:
            if format_value % 1 == 0:
                return "{}万".format('{:,}'.format(int(format_value)))
            return "{}万".format('{:,}'.format(convert_float(format_value, point=point)))
        else:
            if format_value % 1 == 0:
                return "{}万".format(int(format_value))
            return "{}万".format(convert_float(format_value, point=point))


def format_comma(value, point=0):
    if value == 0:
        return 0

    is_integer = False
    if value % 1 == 0:
        value = int(value)
        is_integer = True

    if math.fabs(value) < 10000:
        if point <= 0 or is_integer:
            return value
        else:
            return convert_float(value, point)

    if is_integer:
        return "{:,}".format(value)
    else:
        return "{:,}".format(convert_float(value, point))


def get_as_ids(items, field_name, separator=','):
    if items is None or len(items) == 0:
        return ''

    id_array = []
    for one in items:
        a_value = str(one.get(field_name, ''))
        if a_value == '':
            continue
        id_array.append(a_value)

    return separator.join(id_array)


def equals_json(one, another):
    if not one or not another:
        return False
    for key, value in one.iteritems():
        another_value = another.get(key, '')
        if isinstance(value, dict) and isinstance(another_value, dict) and not equals_json(value, another_value):
            return False
        if str(encode_utf8(value)) != str(encode_utf8(another_value)):
            return False

    for key, value in another.iteritems():
        another_value = one.get(key, '')
        if isinstance(value, dict) and isinstance(another_value, dict) and not equals_json(value, another_value):
            return False
        if str(encode_utf8(value)) != str(encode_utf8(another_value)):
            return False
    return True


def exclude_list(a_list, exclude_str):
    if not a_list or len(a_list) == 0:
        return []
    if not exclude_str:
        return a_list
    result = []
    for one in a_list:
        if one.upper() == exclude_str.upper():
            continue
        result.append(one)

    return result


# 生成签名算法
def get_sign(my_app_id, timestamp, my_app_secret):
    lst = [my_app_id, timestamp, my_app_secret]
    lst.sort()
    sha1 = hashlib.sha1()
    map(sha1.update, lst)
    hashcode = sha1.hexdigest()
    return hashcode
