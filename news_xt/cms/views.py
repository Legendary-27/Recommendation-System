from django.shortcuts import render,redirect,reverse
from django.contrib import auth
from django.db import connection
from .models import users
from front.models import user_center

# Create your views here.
def get_corsor():
    return connection.cursor()

def cms_index(request):
    if request.session.get('is_login',None):
        cursor = get_corsor()
        cursor.execute("select * from cms_news")
        cms_news = cursor.fetchall()
        return render(request,'cms_index.html',context={"cms_news":cms_news})
    else:
        return redirect(reverse('login'))
    
def login(request):
    if request.method == "GET":
        return render(request,'login.html')
    else:
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = users.objects.filter(username=username,password=password)
        #user = auth.authenticate(username=username,password=password)
        if user:
            request.session["username"] = username
            request.session["is_login"] = True
            record = user_center(username_id=username,news_id_id="100000")
            record.save()
            is_superuser = users.objects.get(username=username,password=password).is_superuser
            if is_superuser == 1:
                return redirect(reverse('cms:cms_index'))
            else:
                return redirect(reverse('front:index'))
        else:
            return render(request,'login.html',context={"error":"您的用户名或密码错误"})
    

def register(request):
    if request.method == 'GET':
        return render(request,"register.html")
    else:
        username = request.POST.get("username")
        password = request.POST.get("password")
        reqpassword = request.POST.get("reqpassword")
        if users.objects.filter(username=username):
            error1="用户名已存在"
            return render(request,"register.html",context={"error1":error1})
        elif len(username)==0:
            error2="用户名不能为空"
            return render(request,"register.html",context={"error2":error2})
        elif len(password)==0:
            error3="密码不能为空"
            return render(request,"register.html",context={"error3":error3})
        elif password != reqpassword:
            error4="与第一次输入的密码不一致"
            return render(request,"register.html",context={"error4":error4})
        else:
            user = users(username=username,password=password)
            user.save()
            return redirect(reverse("login"))
        
def logout(request):
    request.session.flush()
    auth.logout(request)
    return redirect(reverse("login"))

def news_add(request):
    if request.session.get('is_login',None):
        if request.method == 'GET':
            return render(request,'news_add.html')
        else:
            number = request.POST.get("number")
            title = request.POST.get("title")
            date = request.POST.get("date")
            content = request.POST.get("content")
            count = request.POST.get("count")
            category = request.POST.get("category")
            cursor = get_corsor()
            cursor.execute("insert into cms_news values(s%,'%s','%s','%s','%s',%s)"%(number,category,title,date,content,count))
        return redirect(reverse('cms:cms_index'))
    else:
        return redirect(reverse('login'))

#def news_update(request,new_id):
#    if request.method == 'GET':
#        new = yule.objects.get(number=new_id)
#        return render(request,'news_add.html',context={"new":new})
#    else:
#        number = request.POST.get("number")
#        title = request.POST.get("title")
#        date = request.POST.get("date")
#        content = request.POST.get("content")
#        count = request.POST.get("count")
#        category = request.POST.get("category")
#        new.number = number
#        new.title = title
#        new.date = date
#        new.content = content
#        new.count = count
#        new.category = category
#        new.save()
#    return redirect(reverse('cms:cms_index'))

def news_delate(request):
    if request.session.get('is_login',None):
        if request.method == 'POST':
            new_id = request.POST.get("new_id")
            cursor = get_corsor()
            cursor.execute("delete from cms_news where number=%s" % new_id)
            return redirect(reverse('cms:cms_index'))
        else:
            raise RuntimeError("删除新闻的方法错误")
    else:
        return redirect(reverse('login'))


def news_detail(request,new_id):
    if request.session.get('is_login',None):
        cursor = get_corsor()
        cursor.execute("select * from cms_news where number=%s"%new_id)
        detail_news = cursor.fetchall()
        return render(request,'new_detail.html',context={"detail_news":detail_news})
    else:
        return redirect(reverse('login'))
