from django.http import JsonResponse
from sign.models import Event, Guest
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib import auth as django_auth
import base64, time
import hashlib
from django.http import HttpResponse
# from Crypto.Cipher import AES    # 请安装 Crypto
import json

'''
为接口参加安全机制：认证、前面、AES加密
'''


# ============用户认证==============
# 用户认证
def user_auth(request):
    get_http_auth = request.META.get('HTTP_AUTHORIZATION', b'')
    print(get_http_auth)
    auth = get_http_auth.split()
    try:
        auth_parts = base64.b64decode(auth[1]).decode('utf-8').partition(':')
    except IndexError:
        return "null"
    userid, password = auth_parts[0], auth_parts[2]
    user = django_auth.authenticate(username=userid, password=password)
    if user is not None and user.is_active:
        django_auth.login(request, user)
        return "success"
    else:
        return "fail"


# 发布会查询接口---增加用户认证
def get_event_list(request):
    auth_result = user_auth(request)
    if auth_result == "null":
        return JsonResponse({'status': 10011, 'message': 'user auth null'})

    if auth_result == "fail":
        return JsonResponse({'status': 10012, 'message': 'user auth fail'})

    eid = request.GET.get("eid", "")  # 发布会id
    name = request.GET.get("name", "")  # 发布会名称

    if eid == '' and name == '':
        return JsonResponse({'status': 10021, 'message': 'parameter error'})

    if eid != '':
        event = {}
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 10022, 'message': 'query result is empty'})
        else:
            event['eid'] = result.id
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time
            return JsonResponse({'status': 200, 'message': 'success', 'data': event})

    if name != "":
        datas = []
        results = Event.objects.filter(name__contains=name)
        if results:
            for r in results:
                event = {}
                event['eid'] = r.id
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                datas.append(event)
            return JsonResponse({'status': 200, 'message': 'success', 'data': datas})
        else:
            return JsonResponse({'status': 10022, 'message': 'query result is empty'})


# =======用户签名+时间戳===============
# 用户签名+时间戳
def user_sign(request):
    if request.method == 'POST':
        clint_time = request.POST.get('time', '')  # 获取客户的时间戳
        clint_sign = request.POST.get('sign', '')  # 获取客户端签名
    else:
        return "error"

    if clint_time == '' or clint_sign == '':
        return "sign null"

    # 服务器时间
    now_time = time.time()  # eg:14562332.3131
    server_time = str(now_time).split('.')[0]  # 只要小数点前面的整数
    # 获取服务器时间和客户端时间的时间差
    time_difference = int(server_time) - int(clint_time)
    if time_difference >= 60:
        return "timeout"

    # 签名检查
    md5 = hashlib.md5()
    sign_str = clint_time + "&Guest-Bugmaster"
    sign_bytes_utf8 = sign_str.encode(encoding="utf-8")
    md5.update(sign_bytes_utf8)
    server_sign = md5.hexdigest()
    if server_sign != clint_sign:
        return "sign fail"
    else:
        return "sign right"


# 添加发布会接口---增加签名+时间戳
def add_event(request):
    sign_result = user_sign(request)
    if sign_result == "error":
        return JsonResponse({'status': 10011, 'message': 'request error'})
    elif sign_result == 'sign null':
        return JsonResponse({'status': 10012, 'message': 'user sign null'})
    elif sign_result == 'timeout':
        return JsonResponse({'status': 10013, 'message': 'user sign timeout'})
    elif sign_result == 'sign fail':
        return JsonResponse({'status': 10014, 'message': 'user sign error'})

    eid = request.POST.get('eid', '')  # 发布会id
    name = request.POST.get('name', '')  # 发布会名称
    limit = request.POST.get('limit', '')  # 限制人数
    status = request.POST.get('status', '')  # 状态
    address = request.POST.get('address', '')  # 地址
    start_time = request.POST.get('start_time', '')  # 发布会时间

    if eid == '' or name == '' or limit == '' or address == '' or start_time == '':
        return JsonResponse({'status': 10021, 'message': 'parameter error'})

    result = Event.objects.filter(id=eid)
    if result:
        return JsonResponse({'status': 10020, 'message': 'event id is already exists'})

    result = Event.objects.filter(name=name)
    if result:
        return JsonResponse({'status': 10023, 'message': 'event name already exists'})

    if status == '':
        status = 1
    try:
        Event.objects.create(id=eid, name=name, limit=limit, status=int(status),
                             address=address, start_time=start_time)
    except ValidationError as e:
        error = 'start_time format error.It must be in YYYY-MM-DD HH:MM:SS format.'
        return JsonResponse({'status': 10024, 'message': error})
    return JsonResponse({'status': 200, 'message': 'add event success'})

