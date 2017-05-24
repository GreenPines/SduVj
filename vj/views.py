# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, Http404, HttpResponseRedirect, render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.template import Context, RequestContext, loader
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from django.core.files.base import ContentFile
from vj.models import *
from django.utils import timezone
from collections import OrderedDict
import datetime
import pytz
import re
import json
import pymysql
import time
import base64

LIST_NUMBER_EVERY_PAGE = 20
PAGE_NUMBER_EVERY_PAGE = 7

LANG_DICT = {0: 'G++', 1: 'GCC', 2: 'C++', 3: 'C', 4: 'Pascal', 5: 'Java', 6: 'C#', 7: 'Python'}
LANGUAGE = {
        'G++' : '0',
        'GCC' : '1',
        'C++' : '2',
        'C' : '3',
        'Pascal' : '4',
        'Java' : '5',
        'C#' : '6',
        'Python' : '7',
        }

def ren2res(template, req, dict={}):
    if req.user.is_authenticated():
        p = re.compile('^[0-9a-zA-Z_]+$')
        dict.update({'user': {  'id': req.user.id, 
                                'username': req.user.get_username(),
                                'is_staff':req.user.is_staff,
                                #'sid':req.user.info.sid,
                                #'nickname':req.user.info.nickname,
                                #'school':req.user.info.school
                                }})
    else:
        dict.update({'user': False})
    """
    if req:
        return render_to_response(template, dict, context_instance=RequestContext(req))
    else:
        return render_to_response(template, dict)
        """
    return render(req,template,dict);
def home(req):
    return ren2res("home.html", req, {})

def login(req):
    if req.method == 'GET':
        if req.user.is_anonymous():
            if req.GET.get('next'):
                req.session['next'] = req.GET.get('next')
            return ren2res("login.html", req, {})
        else:
            return HttpResponseRedirect("/")
    elif req.method == 'POST':
        user = auth.authenticate(username=req.POST.get('username'), password=req.POST.get('password'))
        if user is not None:
            auth.login(req, user)
            next = req.session.get('next')
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect('/')
        else:
            return ren2res("login.html", req, {'err': "Wrong Username or Password!"+
                "US:"+req.POST.get('username')+'  PS:'+req.POST.get('password')})

def register(req):
    if req.method == 'GET':
        if req.user.is_anonymous():
            if req.GET.get('next'):
                req.session['next'] = req.GET.get('next')
            return ren2res('register.html', req, {})
        else:
            return HttpResponseRedirect('/')
    elif req.method == 'POST':
        username = req.POST.get("username")
        email = req.POST.get('email')
        result = User.objects.filter(username=username);
        p = re.compile('^[0-9a-zA-Z_]+$')
        if len(username) == 0 or p.match(username)==None:
            return ren2res('register.html', req, {'err': "Invalid username"})
        elif len(email) == 0:
            return ren2res('register.html', req, {'err': "Email can't be null"})
        elif len(result) != 0:
            return ren2res('register.html', req, {'err': "This username has been registered! Try another"})
        else:
            pw1 = req.POST.get('pw1')
            if pw1 == "":
                return ren2res('register.html', req, {'err': "Password can't be null", 'account': account})
            pw2 = req.POST.get('pw2')
            if pw1 != pw2:
                return ren2res('register.html', req, {'err': "Password not consistent", 'account': account})
            else:
                newuser = User()
                newuser.username = username
                newuser.email = email
                newuser.set_password(pw1)
                newuser.is_staff = 0
                newuser.is_active = 1
                newuser.is_superuser = 0
                newuser.save()
                newuser = auth.authenticate(username=username, password=pw1)
                auth.login(req, newuser)
                next = req.session.get('next')
                if next:
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponseRedirect('/')


def logout(req):
    auth.logout(req)
    return HttpResponseRedirect('/')

def problem(req):
    pg = int(req.GET.get('pg', 1))
    search = req.GET.get('search', "")
    """
    if search:
        qs = Problem.objects.filter(visible=True).filter(numberOfContest=0).filter(Q(id__icontains=search) | Q(title__icontains=search))
        # .select_related("uid__name").filter(uid__contains=search)
    else:
        qs = Problem.objects.filter(visible=True).filter(numberOfContest=0).all()
    """
    qs=Problem.objects.all();
    idxstart = (pg - 1) * LIST_NUMBER_EVERY_PAGE
    idxend = pg * LIST_NUMBER_EVERY_PAGE

    max = qs.count() // 20 + 1

    if (pg > max):
        raise Http404("no such page")
    start = pg - PAGE_NUMBER_EVERY_PAGE
    if start < 1:
        start = 1
    end = pg + PAGE_NUMBER_EVERY_PAGE
    if end > max:
        end = max

    lst = qs[idxstart:idxend]
    lst = list(lst)
    aclst = []
    trylst = []
    '''
    if req.user.is_authenticated():
        user = req.user
        for item in lst:
            if item.aceduser.filter(id=user.info.id):
                aclst.append(item.id)
            elif item.trieduser.filter(id=user.info.id):
                trylst.append(item.id)
    '''
#        print(aclst)
#        print('trylst')
#        print(trylst)

    return ren2res("problem.html", req, {'pg': pg, 'page': list(range(start, end + 1)), 'list': lst, 'aclst':aclst, 'trylst':trylst})


#db = pymysql.connect("211.87.227.207","vj","vDpAZE74bJrYahZKmcvZxwc","vj")

def problem_detail(req, proid):
    problem = Problem.objects.get(proid=proid)
    return ren2res("problem/problem_detail.html", req, {'problem': problem})
#    smp = TestCase.objects.filter(pid__exact=pid).filter(sample__exact=True)
#    return ren2res("problem/problem_detail.html", req, {'problem': problem, 'sample': smp})


@login_required
def problem_submit(req, proid):
    if req.method == 'GET':
        return ren2res("problem/problem_submit.html", req, {'problem': Problem.objects.get(proid=proid)})
    elif req.method == 'POST':
        status = Status(user=req.user, pro=Problem.objects.get(proid=proid), lang=req.POST.get('lang'), result='Waiting', 
            time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        if req.POST.get('code'):
            # f = open('JudgeFiles/source/' + str(sub.id), 'w')
            # f.write(req.POST.get('code'))
            status.code = base64.b64encode(bytes(req.POST.get('code'), 'utf-8'))
        else:
            return ren2res("problem/problem_submit.html", req,
                           {'problem': Problem.objects.get(proid=proid), 'err': "No Submit!"})
        # f.close()
        status.save()
        #sub.source_code.save(name=str(sub.id), content=content_file)
        #sub.save()
        #judger.Judger(sub);

        return HttpResponseRedirect("/status/")

def status(req):
    pro_id = req.GET.get('pro_id')
    if pro_id:
        query = Status.objects.filter(pro_id=pro_id).all().order_by('-runid')
    else:
        query = Status.objects.all().order_by('-runid')

    search = req.GET.get('search')
    if search:
        query = query.filter(Q(pro__title__icontains=search) | Q(user__username__icontains=search))

    #print(len(query))

    pg = req.GET.get('pg')
    if not pg:
        pg = 1
    pg = int(pg)

    max_cnt = query.count() // 20 + 1
    start = max(pg - PAGE_NUMBER_EVERY_PAGE, 1)
    end = min(pg + PAGE_NUMBER_EVERY_PAGE, max_cnt)

    lst = query[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]
    #print(len(lst))

    return ren2res('status.html', req, {'pro_id': pro_id, 'page': range(start, end + 1), 'list': lst })


@login_required
def profile(req):
    if req.method == 'GET':
        return ren2res('profile.html',req,{})
    else:
        user = req.user
        if not user:
            return ren2res('profile.html',req,{})
        else:
            pw = req.POST.get('password')
            if not user.check_password(pw):
                return ren2res('profile.html', req, {'err': "Wrong password"})
            '''
            user.info.nickname = req.POST.get('nickname')
            if len(user.info.nickname)==0:
                return ren2res('profile.html', req, {'err': "Nickname can't be null"})
            user.info.school = req.POST.get('school')
            user.info.sid = req.POST.get('sid')
            user.info.save()
            '''
            npw1 = req.POST.get('npw1')
            if npw1 == "":
                return ren2res('profile.html', req, {'err': "User Profile Updated"})
            npw2 = req.POST.get('npw2')
            if npw1 != npw2:
                return ren2res('profile.html', req, {'err': "New Password not consistent"})
            else:
                user.set_password(npw1)
                user.save()
                return ren2res("login.html", req, {})
        return HttpResponseRedirect('/')

@login_required
def show_source(req):
    solution_id = req.GET.get('solution_id')
    query = Status.objects.filter(runid=solution_id)
    if len(query) == 0:
        raise Http404
    elif query[0].user.id != req.user.id and not req.user.is_staff:
        raise Http404
    else:
        status = query[0]
        code = base64.b64decode(bytes(status.code, 'utf-8'))
        '''
        err = ""
        try:
            f = open('/home/sduacm/OnlineJudge/JudgeFiles/result/' + str(submit.id), 'r')
            err = f.read()
            f.close()
        except IOError:
            pass
        err = err.replace("/tmp","...")
        err = err.replace("/sduoj/source","")
        print('error:')
        print(err)
        if err == '':
            err = 'Successful'
        '''
        return ren2res('show_source.html', req, {'status': status, 'code': code, 'lang': LANG_DICT[status.lang]})
