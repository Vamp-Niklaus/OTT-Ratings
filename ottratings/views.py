from django.shortcuts import render, redirect
from datetime import datetime
from ottratings.models import Contact,Comments,Web,Season,Episode,Users
from ottratings.models import Ratings,Views,Categories,Languages,Available_on,plat_list,Lang_list,Cat_list
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models.signals import pre_save,post_save
import math
# Create your views here.


def index(request):
    context={
        'web':Web.objects.all().order_by("-web_id"),
        'cat':Cat_list.objects.all(),
        'lan':Lang_list.objects.all(),
        'plat':plat_list.objects.all(),
        'year':range(2000,2023),
        'sort':['by rating','A-Z','Z-A','Newly Uploaded','Old Uploaded']
    }
    return render(request,'index.html',context)
    # return HttpResponse("this is homepage")
def seasons(request,web_id):
    context={
             'web':Web.objects.get(web_id=web_id),
             'sea':Season.objects.filter(web_id=web_id),
             'com':Comments.objects.filter(con=web_id).order_by("-cat"),
             'users':Users.objects.all(),
             'cat':Cat_list.objects.all(),
            'lan':Lang_list.objects.all(),
            'plat':plat_list.objects.all(),
            'year':range(2000,2023),
            'sort':['by rating','A-Z','Z-A','Newly Uploaded','Old Uploaded']
            }
    return render(request,'seasons.html',context)
    # return HttpResponse("this is homepage")
    
def episodes(request,sea_id):
    context={
            'web':Web.objects.get(web_id=int(float(sea_id))),
            'sea':Season.objects.get(sea_id=sea_id),
            'epi':Episode.objects.filter(sea_id=sea_id),
            'com':Comments.objects.filter(con=sea_id).order_by("-cat"),
            'users':Users.objects.all(),
            'cat':Cat_list.objects.all(),
            'lan':Lang_list.objects.all(),
            'plat':plat_list.objects.all(),
            'year':range(2000,2023),
            'sort':['by rating','A-Z','Z-A','Newly Uploaded','Old Uploaded']
            }
    return render(request,'episodes.html',context)
    # return HttpResponse("this is homepage")

    
    
def episode(request,epi_id):
    context={
            'web':Web.objects.get(web_id=int(float(epi_id))),
            'sea':Season.objects.get(sea_id=(int(float(epi_id)*100))/100),
            'epi':Episode.objects.get(epi_id=epi_id),
            'com':Comments.objects.filter(con=epi_id).order_by("-cat"),
            'users':Users.objects.all(),
            'run_time':str(Episode.objects.get(epi_id=epi_id).run_time),
            'cat':Cat_list.objects.all(),
            'lan':Lang_list.objects.all(),
            'plat':plat_list.objects.all(),
            'year':range(2000,2023),
            'sort':['by rating','A-Z','Z-A','Newly Uploaded','Old Uploaded']
            }
    return render(request,'episode.html',context)
    # return HttpResponse("this is homepage")
    
def comments(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            cby=User.objects.get(username=request.user).id
            con= float(request.POST['con'])
            on_what=Views.objects.get(v_id=con).on_what
            c= request.POST['c']
            if len(c)>100:
                messages.error(request, "Commments must be under 100 charcters!!")
            elif len(c)<1:
                messages.error(request, "Comments can't be empty!!")
            else:
                Comments(0,con,c,cby,cat=datetime.today()).save()
                messages.success(request, "your comments saved successfully !")
                
            if on_what=='web':
                return redirect('seasons',con)
            elif on_what=='sea':
                return redirect('episodes',con)
            else:
                return redirect('episode',con)
    else:
        messages.error(request, "You must be logged in for comment!!")
        con= float(request.POST['con'])
        on_what=Views.objects.get(v_id=con).on_what
        if on_what=='web':
            return redirect('seasons',con)
        elif on_what=='sea':
            return redirect('episodes',con)
        else:
            return redirect('episode',con)
    
def ratings(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            rby=User.objects.get(username=request.user).id
            ron= float(request.POST['ron'])
            rating= request.POST['star']
            os=Views.objects.get(v_id=ron).sum
            oc=Views.objects.get(v_id=ron).count
            on_what=Views.objects.get(v_id=ron).on_what
            entries=Ratings.objects.values_list('rby','ron')
            
            if (rby,ron) in entries:
                old=Ratings.objects.get(ron=ron,rby=rby).rating
                Ratings.objects.filter(ron=ron,rby=rby).update(rating=rating)
                Views.objects.filter(v_id=ron).update(sum=(float(os)+int(rating)-int(old)))
                messages.success(request, f"Your rating updated from  {str(old)}  to   {str(rating)}.")
            else:
                Ratings(ron,rby,rating=rating).save()
                Views.objects.filter(v_id=ron).update(sum=(float(os)+int(rating)))
                Views.objects.filter(v_id=ron).update(count=(int(oc)+1))
            
            ns=Views.objects.get(v_id=ron).sum
            nc=Views.objects.get(v_id=ron).count    
            if on_what=='web':
                Web.objects.filter(web_id=ron).update(rating=round((float(ns)/int(nc)),1))
                return redirect('seasons',ron)
            elif on_what=='sea':
                Season.objects.filter(sea_id=ron).update(rating=round((float(ns)/int(nc)),1))
                return redirect('episodes',ron)
            else:
                Episode.objects.filter(epi_id=ron).update(rating=round((float(ns)/int(nc)),1))
                return redirect('episode',ron)
    else:
        messages.error(request, "You must be logged in for rating!!")
        ron= float(request.POST['ron'])
        on_what=Views.objects.get(v_id=ron).on_what
        if on_what=='web':
            return redirect('seasons',ron)
        elif on_what=='sea':
            return redirect('episodes',ron)
        else:
            return redirect('episode',ron)
        

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        dob = request.POST['dob']
        gender = request.POST['gender']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('home')
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('home')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('home')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('home')
        
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        Users(id=User.objects.get(username=username).id,birthday=dob,gender=gender,user_id=User.objects.get(username=username).id).save()
        messages.success(request, "Your Account has been created succesfully!!")
        return redirect('signin')
        
    return render(request,'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Logged In Sucessfully!!")
            return redirect('home')
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('home')
    
    return render(request, "signin.html")

def signout(request):
    logout(request)
    messages.success(request,"Logged out sucessfully!")
    return redirect('home')

def search(request):
    target=request.GET['search']
    rweb=Web.objects.filter(w_name__icontains=target).first()
    if rweb is None:
        messages.error(request,"Sorry! No Matches Found!")
        return redirect('home')
    else:
        context={
        'web':Web.objects.filter(w_name__icontains=target),
        'cat':Cat_list.objects.all(),
        'lan':Lang_list.objects.all(),
        'plat':plat_list.objects.all(),
        'year':range(2000,2023),
        'sort':['by rating','A-Z','Z-A','Newly Uploaded','Old Uploaded']
        }
        return render(request,'index.html',context)
    
def category(request,rcat):
    rweb=Categories.objects.filter(category=rcat).first()
    if rweb is None:
        messages.error(request,"Sorry! No Matches Found!")
        return redirect('home')
    else:
        rid=Categories.objects.filter(category=rcat).values_list('web_id',flat=True)
        context={
        'web':Web.objects.filter(web_id__in =rid),
        'cat':Cat_list.objects.all(),
        'lan':Lang_list.objects.all(),
        'plat':plat_list.objects.all(),
        'year':range(2000,2023),
        'sort':['by rating','A-Z','Z-A','Newly Uploaded','Old Uploaded']
        }
        return render(request,'index.html',context)
    
def platform(request,rplat):
    rweb=Available_on.objects.filter(platform=rplat).first()
    if rweb is None:
        messages.error(request,"Sorry! No Matches Found!")
        return redirect('home')
    else:
        rid=Available_on.objects.filter(platform=rplat).values_list('web_id',flat=True)
        context={
        'web':Web.objects.filter(web_id__in =rid),
        'cat':Cat_list.objects.all(),
        'lan':Lang_list.objects.all(),
        'plat':plat_list.objects.all(),
        'year':range(2000,2023),
        'sort':['by rating','A-Z','Z-A','Newly Uploaded','Old Uploaded']
        }
        return render(request,'index.html',context)



def language(request,rlang):
    rweb=Languages.objects.filter(language=rlang).first()
    if rweb is None:
        messages.error(request,"Sorry! No Matches Found!")
        return redirect('home')
    else:
        rid=Languages.objects.filter(language=rlang).values_list('web_id',flat=True)
        context={
        'web':Web.objects.filter(web_id__in =rid),
        'cat':Cat_list.objects.all(),
        'lan':Lang_list.objects.all(),
        'plat':plat_list.objects.all(),
        'year':range(2000,2023),
        'sort':['by rating','A-Z','Z-A','Newly Uploaded','Old Uploaded']
        }
        return render(request,'index.html',context)

def contact(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            first_name=request.user.first_name
            last_name=request.user.last_name
            email = request.user.email
            reason = request.POST['reason']
            at=datetime.today()
            number = request.POST['number']
            if Contact.objects.filter(customer=request.user.username).first() is None:
                if len(reason)<1:
                    messages.error(request, "Sorry you can't send empty message!!")
                    return redirect('home')
                elif len(number)<10:
                    messages.error(request, "Please Fill Complete Numbers!!")
                    return redirect('home')
                else:
                    Contact(c_id=request.user.id,customer=request.user.username,first_name=first_name,last_name=last_name,email=email,reason=reason,at=at,number=number).save()
                    messages.success(request, "Your message sent successfully!!")   
                    return redirect('home')
            else:
                messages.error(request, "Sorry you can't send message again!!")
                return redirect('home')
                
        else:
            return render(request,'contact.html')
    else:
        messages.error(request, "You must be logged in for Contact Us!!")
        return redirect('home')

def year(request,year):
    rweb=Web.objects.filter(release_year=year).first()
    if rweb is None:
        messages.error(request,"Sorry! No Matches Found!")
        return redirect('home')
    else:
        context={
        'web':Web.objects.filter(release_year=year),
        'cat':Cat_list.objects.all(),
        'lan':Lang_list.objects.all(),
        'plat':plat_list.objects.all(),
        'year':range(2000,2023),
        'sort':['by rating','A-Z','Z-A','Newly Uploaded','Old Uploaded']
        }
        return render(request,'index.html',context)
    
    
    
def sort(request,sort):
    if sort=='by rating':
        context={
        "web":Web.objects.all().order_by("-rating"),
        'cat':Cat_list.objects.all(),
        'lan':Lang_list.objects.all(),
        'plat':plat_list.objects.all(),
        'year':range(2000,2023),
        'sort':['by rating','A-Z','Z-A','Newly Uploaded','Old Uploaded']
        }
        return render(request,'index.html',context)
    elif sort=='A-Z':
        context={
        "web":Web.objects.all().order_by("w_name"),
        'cat':Cat_list.objects.all(),
        'lan':Lang_list.objects.all(),
        'plat':plat_list.objects.all(),
        'year':range(2000,2023),
        'sort':['by rating','A-Z','Z-A','Newly Uploaded','Old Uploaded']
        }
        return render(request,'index.html',context)
    elif sort=='Z-A':
            context={
        "web":Web.objects.all().order_by("-w_name"),
        'cat':Cat_list.objects.all(),
        'lan':Lang_list.objects.all(),
        'plat':plat_list.objects.all(),
        'year':range(2000,2023),
        'sort':['by rating','A-Z','Z-A','Newly Uploaded','Old Uploaded']
        }
            return render(request,'index.html',context)
    elif sort=='Newly Uploaded':
        context={
        "web":Web.objects.all().order_by("-web_id"),
        'cat':Cat_list.objects.all(),
        'lan':Lang_list.objects.all(),
        'plat':plat_list.objects.all(),
        'year':range(2000,2023),
        'sort':['by rating','A-Z','Z-A','Newly Uploaded','Old Uploaded']
        }
        return render(request,'index.html',context)
    elif sort=='Old Uploaded':
        context={
        "web":Web.objects.all().order_by("web_id"),
        'cat':Cat_list.objects.all(),
        'lan':Lang_list.objects.all(),
        'plat':plat_list.objects.all(),
        'year':range(2000,2023),
        'sort':['by rating','A-Z','Z-A','Newly Uploaded','Old Uploaded']
        }
        return render(request,'index.html',context)
    
    
def web_post_save(instance, **kwargs):
    Views(instance.web_id,0,0,'web').save()
pre_save.connect(web_post_save,sender=Web)

def season_post_save(instance, **kwargs):
    Views(instance.sea_id,0,0,'sea').save()
    s=Season.objects.filter(web_id=instance.web_id)
    Web.objects.filter(web_id=instance.web_id).update(seasons=s)
pre_save.connect(season_post_save,sender=Season)

def episode_post_save(instance, **kwargs):
    Views(instance.epi_id,0,0,'epi').save()
    e=Episode.objects.filter(sea_id=instance.sea_id)
    Web.objects.filter(web_id=instance.web_id).update(episodes=e)
pre_save.connect(episode_post_save,sender=Episode)