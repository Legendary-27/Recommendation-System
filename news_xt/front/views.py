from django.shortcuts import render,redirect,reverse
from datetime import datetime
from django.db import connection
from .models import user_center
from cms.models import news
from recommend import LFM,UserIIF,ItemCF,Random 
# Create your views here.

def get_corsor():
    return connection.cursor()

def index(request):
    if request.session.get('is_login',None):
        username = request.session["username"]
        user_name = {}
        cursor = get_corsor()
        cursor.execute("select * from front_user_center")
        news_record = cursor.fetchall()
        for item in news_record:
            u = item[1]
            if u not in user_name:
                user_name[u] = []
            v = item[2]
            user_name[u].append(v)
        BaU = UserIIF(user_name)
        BaUrec = BaU.GetRecommendation(username,15,8)
        IT = ItemCF(user_name)
        ITrec = IT.GetRecommendation(username, 15,8)
        Ro = Random(user_name)
        Rorec = Ro.GetRecommendation(username,15,8)
        LFm = LFM(user_name,5,0.02,100,100,0.01)
        LFMrec = LFm.GetRecommendation(username,8)
        news_list = ITrec+BaUrec+Rorec+LFMrec
        news_id = []
        for item in news_list:
            news_id.append(item[0])
        news_id = set(news_id)
        news_id = list(news_id)
        news_recommends = []
        for item in news_id:
            cursor.execute("select * from cms_news where number={}".format(item))
            news_recommend = cursor.fetchall()
            news_recommends.append(news_recommend)
        return render(request, 'index.html',context={"news_recommend":news_recommends})
    else:
        return render(request,'login.html')

def redu(request):
    if request.session.get('is_login',None):
        cursor = get_corsor()
        cursor.execute("select * from cms_news order by count desc")
        redu_news = cursor.fetchall()
        return render(request,'redu.html',context={"redu_news":redu_news})
    else:
        return redirect(reverse('login'))

def technology(request):
    if request.session.get('is_login',None):
        cursor = get_corsor()
        cursor.execute("select * from cms_news where category='科技'")
        keji_news = cursor.fetchall()
        return render(request,'keji.html',context={"keji_news":keji_news})
    else:
        return redirect(reverse('login'))

def entertainment(request):
    if request.session.get('is_login',None):
        cursor = get_corsor()
        cursor.execute("select * from cms_news where category='娱乐'")
        yule_news = cursor.fetchall()
        return render(request,'yule.html',context={"yule_news":yule_news})
    else:
        return redirect(reverse('login'))

def financial(request):
    if request.session.get('is_login',None):
        cursor = get_corsor()
        cursor.execute("select * from cms_news where category='经济'")
        caijing_news = cursor.fetchall()
        return render(request,'caijing.html',context={"caijing_news":caijing_news})
    else:
        return redirect(reverse('login'))

def military(request):
    if request.session.get('is_login',None):
        cursor = get_corsor()
        cursor.execute("select * from cms_news where category='军事'")
        junshi_news = cursor.fetchall()
        return render(request,'junshi.html',context={"junshi_news":junshi_news})
    else:
        return redirect(reverse('login'))

def society(request):
    if request.session.get('is_login',None):
        cursor = get_corsor()
        cursor.execute("select * from cms_news where category='社会'")
        shehui_news = cursor.fetchall()
        return render(request,'shehui.html',context={"shehui_news":shehui_news})
    else:
        return redirect(reverse('login'))
 
def international(request):
    if request.session.get('is_login',None):
        cursor = get_corsor()
        cursor.execute("select * from cms_news where category='国际'")
        guoji_news = cursor.fetchall()
        return render(request,'guoji.html',context={"guoji_news":guoji_news})
    else:
        return redirect(reverse('login'))

def usercenter(request):
    if request.session.get('is_login',None):
        username = request.session["username"]
        user_news = news.objects.filter(user_center__username=username).values_list("number","category","title","date","content","count")
        return render(request,'user_center.html',context={"user_news":user_news})
    else:
        return redirect(reverse('login'))


def view(request,news_id):
    if request.session.get('is_login',None):
        username = request.session["username"]
        view_infor = user_center(username_id=username,news_id_id=news_id)
        view_infor.save()
        cursor = get_corsor()
        cursor.execute("select * from cms_news where number=%s"%news_id)
        view_news = cursor.fetchall()
        c_news = news.objects.get(number = news_id)
        c_news.count = c_news.count+1
        c_news.save()
        return render(request,'new_detail2.html',context={"view_news":view_news})
    else:
        return redirect(reverse('login'))


def add(request):
    #return render(request,"add.html")
    context = {
        'value1':['1','2','3'],
        'value2':['4','5','6']
            }
    return render(request,'add.html',context=context)

def cut(request):
    #return render(request,"add.html")
    context = {
        'value1':"hello world",
        'value2':" ",
            }
    return render(request,'cut.html',context=context)

def date(request):
    #return render(request,"add.html")
    context = {
        'today':datetime.now(),
            }
    return render(request,'date.html',context=context)

def suanfa(request):
    pass
        
'''
def login(request):
    next = request.GET.get('next')
    text = '登陆完成后要跳转的页面url是'+next
    return HttpResponse(text)

    
def login(request):#登陆
    #html2 = render_to_string("login.html")
    #return HttpResponse(html2)
    return render(request, 'index.html')
''' 


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    