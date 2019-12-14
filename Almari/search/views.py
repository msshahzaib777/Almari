from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import views as auth_view
from django.views import generic
from django.views.generic import View
from django.template import loader
from subprocess import Popen, PIPE
from .models import product, fav, profile
import sys, json, re,  subprocess
from operator import itemgetter
from .forms import UserForm, loginForm
from django import forms

def home(request):
    template = loader.get_template('index.html')
    userprofile =  get_userprofile(request)
    context = {
        'userprofile' : userprofile,
    }
    return HttpResponse(template.render(context, request))

def search(request):
    template = loader.get_template('result.html')
    l1 = ''
    l2 = ''
    lists = []
    searched_query = ''
    if ('query' in request.GET):
        searched_query = request.GET['query']
    else:
        return redirect('/')
    if 'csrfmiddlewaretoken' not in request.GET:
        return redirect('/directaccess')
    if ('query' not in request.session):
        request.session['query'] = searched_query
        lists = get_products(searched_query)
        request.session['products'] = lists
    elif (request.session['query'] != searched_query):
        request.session['query'] = searched_query
        lists = get_products(searched_query)
        request.session['products'] = lists
    if 'sort' in request.GET:
        if request.GET['sort'] == 'low':
            request.session['products'] = sorted(request.session['products'], key=itemgetter('abs'))
            l1 = 'disabled'
        else:
            request.session['products'] = sorted(request.session['products'], key=itemgetter('abs'), reverse=True)
            l2 = 'disabled'

    sublist = request.session['products']
    array = range(1, int(len(sublist)/24)+2)
    a=0
    b=0
    if len(sublist) > 24:
        pg = True
    else:
        pg = False

    if 'page' not in request.GET:
       b=21 
    else:
        if (int(request.GET['page']) <= int(len(sublist)/24)+1):
            a = 24*(int(request.GET['page'])-1)+1
            if int(request.GET['page']) == 0:
                a=0
            b = a+24
        else:
            return redirect('/error404')
    userprofile =  get_userprofile(request)
    context = {
                'userprofile' : userprofile,
                'q' : sublist[a:b],
                'pglink' : pg,
                'pagecount' : array,
                'current' : int(request.GET['page']),
                'query' : request.session['query'],
                'link1' : l1, 
                'link2'  : l2,
    }
    return HttpResponse(template.render(context, request))

def error404(request):
    template = loader.get_template('error404.html')
    userprofile =  get_userprofile(request)
    context = {
                'userprofile' : userprofile,
                'error' : 'but the page you requested was not found'}
    return HttpResponse(template.render(context, request))

def directaccess(request):
    template = loader.get_template('error404.html')
    userprofile =  get_userprofile(request)
    context = {
                'userprofile' : userprofile,
                'error' : 'Direct Access are not allowed' }
    return HttpResponse(template.render(context, request))

def get_products(query):
    url = query.replace(' ', '+')
    mylist = [url]
    
    process = subprocess.Popen(["python", "search/spider.py"] + mylist, stdout=PIPE)
    out , err = process.communicate()
    
    output = out.decode('cp1252')
    data = output.split('**\r\n')    
        
    lists= []
    for i in range(0,len(data)-1,4):
        prdt = dict.fromkeys(['title', 'price', 'imglnk', 'link', 'abs', 'theme', 'json'])
        prdt['title'] = data[i]
        prdt['link'] = data[i+1]
        prdt['imglnk'] = data[i+2]
        prdt['price'] = data[i+3]
        y = re.findall('[0-9]+.[0-9]+', prdt['price'])
        if len(y) > 0 :    
            prdt['abs'] = float(y[len(y)-1].replace(',','.'))
            
            if(re.search('amazon', prdt['link'])):
                prdt['theme'] = ' bg-success text-white '
            elif(re.search('ebay', prdt['link'])):
                prdt['theme'] = ' text-white bg-info '
            elif(re.search('ali', prdt['link'])):
                prdt['theme'] = ' bg-danger text-white '
            
            prdt['json'] = json.dumps(prdt)
            prdt['json'] = json.dumps(prdt)
            lists.append(prdt)
    return lists

class custom_login(auth_view.LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True

    login = auth_view.LoginView.as_view()
    
class UserFormView(View):
    form_class = UserForm
    template_name = 'reg.html'
    
    #blank form
    def get(self, request):
        form = self.form_class(None)
        if request.user.is_authenticated:
            return redirect('/')
        else:    
            return render(request, self.template_name, {'form': form})
    #process form data    
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password) 
            user.save()

            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)
                    return redirect('/')
        else:
            return render(request, self.template_name, {'form': form})

def get_fav(request):
    if request.user.is_authenticated:
        template = loader.get_template('fav.html')
        if 'query' in request.GET:
            your_search_query = request.GET['query']
            qset = Q()
            for term in your_search_query.split():
                qset |= Q(title__contains=term)    
            lists = fav.objects.filter(qset)
            lists = lists.filter(user=request.user.get_username())
        else:        
            lists = fav.objects.filter(user=request.user.get_username())
        sublist = []  
        for i in lists:
            prdt = dict.fromkeys(['title', 'price', 'imglnk', 'link', 'abs', 'theme', 'json'])
            prdt['title'] = i.title
            prdt['link'] = i.link
            prdt['imglnk'] = i.imglink
            prdt['price'] = i.price
            prdt['abs'] = i.abs
            prdt['theme'] = i.theme
            prdt['json'] = i.json
            sublist.append(prdt)
        array = range(1, int(len(sublist)/24)+2)
        a=0
        b=0
        if len(sublist) > 24 :
            pg = True
        else:
            pg = False
            
        l1 = ''
        l2 = ''
        if 'sort' in request.GET:
            if request.GET['sort'] == 'low':
                sublist = sorted(sublist, key=itemgetter('abs'))
                l1 = 'disabled'
            else:
                sublist = sorted(sublist, key=itemgetter('abs'), reverse=True)
                l2 = 'disabled'
    
        if 'page' not in request.GET:
            b=24
            page = 1
        else:
            page = int(request.GET['page'])
            if (int(request.GET['page']) <= int(len(sublist)/24)+1):
                a = 24*(int(request.GET['page'])-1)
                if int(request.GET['page']) == 0:
                    a=0
                b = a+24
            else:
                return redirect('/error404')

        userprofile =  get_userprofile(request)
        context = {
                    'userprofile' : userprofile,
                    'q' : sublist[a:b],
                    'pglink' : pg,
                    'pagecount' : array,
                    'current' : page,
                    'link1' : l1, 
                    'link2'  : l2,
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect('/login')

def add_to_fav(request, Json):
    if request.user.is_authenticated:
        prdt = json.loads(Json)
        fav_prdt = fav(
                        user = request.user.get_username(),
                        title = prdt['title'],
                        price = prdt['price'],
                        imglink = prdt['imglnk'],
                        link = prdt['link'],
                        abs = prdt['abs'],
                        theme = prdt['theme'],
                        json = prdt['json'],
                    )
                    
        obj = fav.objects.filter(
                        user = request.user.get_username(),
                        title = prdt['title'],
                        price = prdt['price'],
                        link = prdt['link'],
                    )
        if obj.count() == 0:
            fav_prdt.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('/login')

def remove(request, Json):
    prdt = json.loads(Json)
    obj = fav.objects.filter(
                    user = request.user.get_username(),
                    title = prdt['title'],
                    price = prdt['price'],
                    link = prdt['link'],
                )
    obj.delete()            

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def user(request):
    if request.user.is_authenticated:
        template = loader.get_template('profile.html')
        userprofile =  get_userprofile(request)
        context = {
           'userprofile' : userprofile,
            'error': ''
        }
        return HttpResponse(template.render(context, request))
    else:
        return redirect('/login')    

def reset_pass(request):
    if request.user.is_authenticated:
        template = loader.get_template('profile.html')
        userprofile =  get_userprofile(request)
        if (request.POST['pass_n'] == request.POST['pass_n2'] and  len(request.POST['pass_n'])>6 ):
            current = request.POST['pass_c']
            c_user = authenticate(username=request.user.get_username(), password=current)
            if c_user != None:
                if c_user.get_username() == request.user.get_username():
                    u = User.objects.get(username = c_user.get_username())
                    u.set_password( request.POST['pass_n'] )
                    u.save()
                    context = {
                            'userprofile' : userprofile,
                            'error' :'password changed !'}    
                    return HttpResponse(template.render(context, request))
                else:
                    context = {
                            'userprofile' : userprofile,
                            'error' :'password Incorrect !'}    
                    return HttpResponse(template.render(context, request))
            else:
                context = {
                            'userprofile' : userprofile,
                            'error' :'password Incorrect !'}    
                return HttpResponse(template.render(context, request))
        else:
            context = {
                        'userprofile' : userprofile,
                        'error' :'password doesnot match the criteria'}
            return HttpResponse(template.render(context, request))
    else:
        return redirect('/login')

def get_userprofile(request):
    Myprofile = dict.fromkeys(['firstname', 'lastname', 'image'])
    Myprofile['firstname'] = 'Not Set yet'
    Myprofile['lastname'] = 'Not Set yet'
    Myprofile['image'] =  '/static/img/account.png'

    if request.user.is_authenticated:
        userpofile = profile.objects.filter(user = request.user.get_username())
        if userpofile:
            Myprofile['firstname'] = userpofile[0].firstname
            Myprofile['lastname'] = userpofile[0].lastname
            Myprofile['image'] =  userpofile[0].profilepic.url
            print(Myprofile['image'])
    return Myprofile        

def setprofile(request):
    if request.method == 'POST':
        Myprofile = profile.objects.filter(user = request.user.get_username() )
        if len(Myprofile) == 0:
            userprofile = profile(user = request.user.get_username(), profilepic= request.FILES['image'] )
            userprofile.save()
        else:
            print('i am not None')
            userprofile =  Myprofile[0]
            userprofile.profilepic = request.FILES['image']
            userprofile.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))    