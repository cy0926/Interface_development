from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from sign.models import Event, Guest


# Create your views here.
def index(request):
    # return HttpResponse("<h1>hello django<h1>")
    return render(request, "new_index.html")


# 登录功能
def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if username == '' or password == '':
            return render(request, "new_index.html", {'error': 'username or password null'})
        else:
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)  # 登录
                request.session['user'] = username
                response = HttpResponseRedirect('/event_manage/')
                return response
            else:
                return render(request, "new_index.html", {'error': 'username or password error'})
    else:
        return render(request, "new_index.html")


# 发布会界面
@login_required
def event_manage(request):
    event_list = Event.objects.all()
    # username = request.COOKIES.get('user')  # 读取浏览器cookie
    username = request.session.get('user')  # 读取浏览器session
    return render(request, "event_manage.html", {"user": username,
                                                 "events": event_list})


# 发布会名称搜索
@login_required
def event_search(request):
    if request.method == "GET":
        username = request.session.get('user', '')
        search_name = request.GET.get("name", "")
        event_list = Event.objects.filter(name__contains=search_name)
        return render(request, "event_manage.html", {"user": username,
                                                     "events": event_list})
    else:
        return render(request, "new_index.html")


# 嘉宾管理
@login_required
def guest_manage(request):
    if request.method == "GET":
        username = request.session.get('user', '')
        guest_list = Guest.objects.all()
        paginator = Paginator(guest_list, 2)
        page = request.GET.get('page')      # 接受一个页数:page
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range(e.g.:9999),deliver last page of results
            contacts = paginator.page(paginator.num_pages)
        return render(request, "guest_manage.html", {"user": username,
                                                     "guests": contacts})
    else:
        return render(request, "new_index.html")


# 嘉宾页搜索功能
@login_required
def guest_search(request):
    if request.method == "GET":
        username = request.session.get('user', '')
        search_phone = request.GET.get('phone')
        guest_list = Guest.objects.filter(phone=search_phone)
        return render(request, "guest_manage.html", {"user": username,
                                                     "guests": guest_list})
    else:
        return render(request, "new_index.html")


# 签到页面
@login_required
def sign_index(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "sign_index.html", {'event': event})


# 签到动作
@login_required
def sign_index_action(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    phone = request.POST.get('phone', '')

    result = Guest.objects.filter(phone=phone)
    if not result:
        return render(request, 'sign_index.html', {'event': event,
                                                   'hint': 'phone error.'})

    result = Guest.objects.filter(phone=phone, event_id=event_id)
    if not result:
        return render(request, 'sign_index.html', {'event': event,
                                                   'hint': 'event id or phone error.'})

    result = Guest.objects.get(phone=phone, event_id=event_id)
    if result.sign:
        return render(request, 'sign_index.html', {'event': event,
                                                   'hint': 'user has sign in.'})
    else:
        Guest.objects.filter(phone=phone, event_id=event_id).update(sign='1')
        return render(request, "sign_index.html", {'event': event,
                                                   'hint': 'sign in success!',
                                                   'guest': result})


# 退出登录
@login_required
def logout(request):
    auth.logout(request)  # 退出登录
    response = HttpResponseRedirect('/index/')
    return response
