from django.shortcuts import render,redirect
from django.urls import reverse
from rango.models import Category
from rango.models import Page,User,UserProfile

from django.http import HttpResponse,HttpRequest
from rango.forms import CategoryForm,PageForm,UserForm,UserProfileForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    visitor_cookie_handler(request) 

    context_dict = {
        'categories': category_list,
        'pages': page_list,
    }
    return render(request, 'rango/index.html', context=context_dict)



def about(request):
    visitor_cookie_handler(request)  
    visits = request.session.get('visits', 1)

    context_dict = {'visits': visits}
    return render(request, 'rango/about.html', context=context_dict)




    


def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None


    return render(request, 'rango/category.html', context=context_dict)

def add_category(request:HttpRequest):
    form = CategoryForm()
    if(request.method=='POST'):
        form= CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect('/rango/')
        else:
            print(form.errors)
        
    
    return render(request, 'rango/add_category.html', context={'form':form})

def add_page(request:HttpRequest,category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category=None

    if category is None:
        return redirect('/rango/')

    form = PageForm()

    if(request.method=='POST'):

        form= CategoryForm(request.POST)
        
        if form.is_valid():
            if category:
                page:Page=form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)
        
    context_dict = {'form':form,'category':category}
    return render(request, 'rango/add_page.html', context=context_dict)


def register(request:HttpRequest):
    registered = False

    if(request.method=='POST'):

        user_form= UserForm(request.POST)
        profile_form= UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user:User =user_form.save()
            user.set_password(user.password)
            user.save()
            profile:UserProfile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile_form.save()
            registered=True

        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'rango/register.html', context={'user_form':user_form,'profile_form':profile_form,'registered':registered})

def user_login(request:HttpRequest):

    if(request.method=='POST'):

        username= request.POST.get('username')
        password= request.POST.get('password')
        user = authenticate(username= username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse('Your Rango account is disabled')
        else:
            print(f'Invalid login details {username}, {password}')
            return HttpResponse('Invalid login details supplied.')
    else:
        return render(request,'rango/login.html')


def some_view(request:HttpRequest):
    if not request.user.is_authenticated():
        return HttpResponse('You are logged in.')
    else:
        return HttpResponse('You are not logged in.')


@login_required(login_url='/rango/login/')
def restricted(request:HttpRequest):
    return HttpResponse('Since you\'re  logged in, you can see this text')

def get_serverside_cookies(request:HttpRequest,cookie,default_val=None):
    val = request.session.get(cookie)
    if not val :
        val = default_val
    return val

def visitor_cookie_handler_x( response):
    visits =int(get_serverside_cookies(request,'visits','1'))
    last_visit_cookie = get_serverside_cookies(request,'last_visit',str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')
    if(datetime.now()-last_visit_time).days>0:
        visits+=1
        response.set_cookie('last_visit',datetime.now())
    else:
        response.set_cookie('last_visit',last_visit_time)
        
    response.set_cookie('visits',visits)

from datetime import datetime

from datetime import datetime

def visitor_cookie_handler(request):
    visits = request.session.get('visits', 0)
    last_visit = request.session.get('last_visit')

    if last_visit:
        try:
            last_visit_time = datetime.strptime(last_visit, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            last_visit_time = datetime.now()
    else:
        last_visit_time = datetime.now()

    # Increment if a day has passed (same logic as chapter)
    if (datetime.now() - last_visit_time).days >= 1:
        visits += 1
        request.session['last_visit'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        request.session['visits'] = visits
    else:
        # Initialise if missing
        if 'visits' not in request.session:
            request.session['visits'] = 1
            request.session['last_visit'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
