from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse,HttpResponseRedirect
from .models import *
from .forms import  createnew
import requests
from requests.compat import quote_plus
from bs4 import BeautifulSoup
from urllib.parse import quote

headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
}

meta_url="https://www.metacritic.com/search/movie/{}/results"
base_url="https://www.rottentomatoes.com/search?search={}"
def start(response):
    return HttpResponseRedirect("/login")
def index(response):
    return render(response,"main/base.html",{})

def home(response):
    return render(response,"main/home.html",{})

def li(response,id):
    ls = list.objects.get(id=id)
    if response.method == "POST":
        if response.POST.get("save"):
            for item in ls.item_set.all():
              if response.POST.get("c"+str(item.id)):
                item.checked=True
              else:
                item.checked=False
              item.save()
        elif response.POST.get("add"):
            txt = response.POST.get("arg1")
            if len(txt)>2:
             if response.POST.get("arg2"):
                b=True
             else :
                b=False
             ls.item_set.create(text=txt,checked=b)               
    return render(response,"main/lists.html",{"ls" : ls})

def searchresults(response):
    search = response.POST.get("search")
    if  len(Searchclass.objects.all())==0:
        HttpResponseRedirect("/results/%s" %search)
    for s in Searchclass.objects.all():
        if(s.name==search):
            x=s.movieobjects.all()
            print("already searched")
            return render(response,"main/results.html",{'movie_obj' : x})
    else:
        return HttpResponseRedirect("/results/%s" %search)

def cinema(response,id):
    movie=Movie.objects.get(id=id)
    return render(response,"main/particular.html",{"movie" : movie})

def create(response):
    if response.method == "POST":
        form = createnew(response.POST)
        if form.is_valid() :
            n=form.cleaned_data["name"]
            t=list(name=n)
            t.save()
            response.user.todolist.add(t)
        return HttpResponseRedirect("/%i" %t.id)
    else:
       form = createnew()
    return render(response,"main/create.html",{"form" : form})

def view(response):
    return render(response,"main/view.html",{})


def results(response,moviename):
    # search = response.POST.get("search")
    # print(search)
    print("new search")
    s10bj=Searchclass(name=moviename)
    s10bj.save()
    final_url=base_url.format(quote_plus(moviename))
    r = requests.get(final_url)
    print(final_url)
    soup = BeautifulSoup(r.content, 'html5lib')
    x=soup.find_all('search-page-media-row')
    movie_title=[]
    movie_links=[]
    # movie_cast=[]
    # movie_year=[]
    movie_rating=[]
    movie_images=[]
    show_title=[]
    show_links=[]
    show_cast=[]
    show_year=[]
    show_rating=[]
    show_images=[]
    meta_rating=[]
    for i in range(0,len(x)):
       z=x[i].get('releaseyear')
       if len(z)!=0 :
          y=x[i].find('a',attrs={ 'class' : 'unset',
                             'slot' : 'title'  })
          img=x[i].find('a',attrs={'class' : 'unset',
                             'slot' : 'thumbnail'  })
          img1 = img.find('img').get('src')
          if (y.get('href') != ""):
            movie_links.append(y.get('href'))                         
            movie_title.append(y.text.strip())
            movie_images.append(img1)
        #   movie_cast.append(x[i].get('cast'))
        #   movie_year.append(x[i].get('releaseyear'))
            if x[i].get('tomatometerscore')=="":
             movie_rating.append('N/A')
            else:
             movie_rating.append(x[i].get('tomatometerscore'))
       else:
          y=x[i].find('a',attrs={ 'class' : 'unset',
                             'slot' : 'title'  })
          img=x[i].find('a',attrs={'class' : 'unset',
                             'slot' : 'thumbnail'  })
          img1 = img.find('img').get('src')
          show_images.append(img1)
          show_links.append(y.get('href'))                         
          show_title.append(y.text.strip())
          show_cast.append(x[i].get('cast'))
          show_year.append(x[i].get('startyear'))
          show_rating.append(x[i].get('tomatometerscore'))
    # movies_list=[]
    shows_list=[]
    movies_id=[]
    movie_obj=[]
    
    for i in range(0,len(show_title)):
        shows_list.append((show_title[i],show_links[i],show_cast[i],show_images[i],show_rating[i],show_year[i])) 



    # cast_list=[]
    # movie_info_list=[]
    # watch_list=[]
    # scraped=0
    # rotten_reviews_list=[]
    # meta_reviews_list=[]
    for i in range(0,len(movie_title)):
        
        for x in Movie.objects.all():
         if (x.title == movie_title[i]):
            cine_id=x.id
            meta_rating.append('err')
            break
        else:
              site=None
              if (movie_links[i] != ''):
               site=requests.get(movie_links[i])
              else:
               continue
              soup = BeautifulSoup(site.content, 'html5lib')



              movie_info={}
              plot=soup.find('div' , attrs={'id' : 'movieSynopsis'}).text.strip()
              movie_info['plot:']=plot
              y=soup.find('ul' , attrs={'class' : 'content-meta info'})
              z=y.find_all('li')
              t=z[0].find('div', attrs={'class' : 'meta-label subtle'}).text
              if z[0].find('div', attrs={'class' : 'meta-value genre'}) !=None:
                 t1=z[0].find('div', attrs={'class' : 'meta-value genre'}).text.strip()
                 t1 = t1.replace("\n", "")
                 t1=t1.replace(" ","")
                 movie_info[t]=t1
              for j in range(1,len(z)):
                   t=z[j].find('div', attrs={'class' : 'meta-label subtle'}).text
                   t1=z[j].find('div', attrs={'class' : 'meta-value'}).text.strip()
                   t1 = t1.replace("\n", "")
                   t1=t1.replace(" ","")
                   if t=="Release Date (Theaters):" or t=="Release Date (Streaming):" :
                             movie_info['Release Date:']=t1
                   else:
                             movie_info[t]=t1
              if 'Release Date:' not in movie_info.keys():
               movie_info['Release Date:']='N/A'
              if 'Director:' not in movie_info.keys():
               movie_info['Director:']='N/A'
              if 'Producer:' not in movie_info.keys():
               movie_info['Producer:']='N/A'
              if 'Writer:' not in movie_info.keys():
               movie_info['Writer:']='N/A'
              if 'Genre:' not in movie_info.keys():
               movie_info['Genre:']='N/A'
              if 'Original Language:' not in movie_info.keys():
               movie_info['Original Language:']='N/A'
              if 'Runtime:' not in movie_info.keys():
               movie_info['Runtime:']='N/A'
              if 'Plot:' not in movie_info.keys():
               movie_info['Plot:']='N/A'




              watch_dict={}
              where=soup.find_all('where-to-watch-meta')
              x=soup.find_all('where-to-watch-bubble')
              for k in where:
               k.find('where-to-watch-bubble').find()
               watch_dict[k.get('href')]=k.find('where-to-watch-bubble').get('image')



              cast_dict={}
              castsection = soup.find('div', attrs={'class':'castSection'})
              cast_table=[]
              if(castsection):
                cast_table=castsection.find_all('div', attrs={'class':'cast-item media inlineBlock'})
              for l in cast_table:
               cast_dict[l.find_all('span')[0].text.strip()]=l.find_all('span')[1].text.strip()


              ul="{}/reviews"
              reviewsRT={}
              print(movie_links[i])
              if (BeautifulSoup(requests.get(ul.format(movie_links[i])).content, 'html5lib').find('div', attrs={'class':'review_table'})):
                 crtRvwSite=BeautifulSoup(requests.get(ul.format(movie_links[i])).content, 'html5lib').find('div', attrs={'class':'review_table'}).find_all('div',attrs={'class':'row review_table_row'})
                 reviewsRT[10]=(crtRvwSite[0].find('div', attrs={'class':'the_review'}).text.strip())
                 if (len(crtRvwSite)>1):
                    reviewsRT[6]=(crtRvwSite[1].find('div', attrs={'class':'the_review'}).text.strip())
              print(reviewsRT)

              se=meta_url.format(quote(movie_title[i]))
              got=requests.get(se, headers=headers)
              res=BeautifulSoup(got.content, 'html5lib')
              if (res.find('span', attrs={'class':'metascore_w medium movie positive'})):
                print(se)
                meta_rating.append(res.find('span', attrs={'class':'metascore_w medium movie positive'}).text)
                print(meta_rating)
              else:
                print(se)
                meta_rating.append("N/A")
                print(meta_rating)


              searchMeta="https://www.metacritic.com/search/movie/{}/results"
              movieMeta="https://www.metacritic.com/{}" 
              name=movie_title[i]
              s=requests.Session()
              s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
              search_results = s.get(searchMeta.format(quote(name)))
              soup = BeautifulSoup(search_results.content, 'html5lib')
              reviewsMC={}
              if(soup.find('ul', attrs={'class':'search_results module'})):
                 firstsearch=soup.find('ul', attrs={'class':'search_results module'}).find('a')
                 m_url=movieMeta.format(firstsearch.get('href'))
                 previews="{}/user-reviews?dist=positive"
                 nreviews="{}/user-reviews?dist=negative"
                 pr=previews.format(m_url)
                 nr=nreviews.format(m_url)
                 if (BeautifulSoup(s.get(pr).content, 'html5lib').find('div', attrs={'class':'user_reviews'})):
                            psoup=BeautifulSoup(s.get(pr).content, 'html5lib').find('div', attrs={'class':'user_reviews'}).find('div',attrs={'class':'review pad_top1'})
                            if psoup:
                             if  psoup.find('div', attrs={'class':'right fl'}).find('div', attrs={'class':'summary'}).find('span', attrs={'class':'blurb blurb_expanded'}):
                              reviewsMC['10']=psoup.find('div', attrs={'class':'right fl'}).find('div', attrs={'class':'summary'}).find('span', attrs={'class':'blurb blurb_expanded'}).text
                 if (BeautifulSoup(s.get(nr).content, 'html5lib').find('div', attrs={'class':'user_reviews'})):
                            nsoup=BeautifulSoup(s.get(nr).content, 'html5lib').find('div', attrs={'class':'user_reviews'}).find('div',attrs={'class':'review pad_top1'})
                            if nsoup:
                             if  nsoup.find('div', attrs={'class':'right fl'}).find('div', attrs={'class':'summary'}).find('span', attrs={'class':'blurb blurb_expanded'}):
                              reviewsMC['5']=nsoup.find('div', attrs={'class':'right fl'}).find('div', attrs={'class':'summary'}).find('span', attrs={'class':'blurb blurb_expanded'}).text
              print(reviewsMC)

              soup = BeautifulSoup(site.content, 'html5lib')
              kwargs=[]
              if (soup.find('section', attrs={'id':'you-might-like'})):
                similar_names=[]
                similar_names_tag=soup.find('section', attrs={'id':'you-might-like'}).find_all('span', attrs={'class':'p--small'})
                for m in similar_names_tag:
                   similar_names.append(m.text)
                print(similar_names)
                for n in range(0, len(similar_names)):
                #    if (Movie.objects.filter(title=similar_names[n]).first()):
                #       print(similar_names[n])
                #       kwargs.append(Movie.objects.get(title=similar_names[n]))
                    for x in Movie.objects.all():
                           if (x.title == similar_names[n]):
                              simmovie_id=x.id
                              kwargs.append(Movie.objects.get(id=simmovie_id))
                              break
                    else:
                        temp=2                       
              print(i)
              print(len(movie_title))
              print(len(meta_rating))
              print(meta_rating[i])
              if meta_rating[i] != 'err' :
               m1=Movie(title=movie_title[i],plot=movie_info['plot:'],language=movie_info['Original Language:'],
                  Director=movie_info['Director:'],Producer=movie_info['Producer:'],Writer=movie_info['Writer:'],
                  year=movie_info['Release Date:'],duration=movie_info['Runtime:'],
                  genre=movie_info['Genre:'],rating=movie_rating[i],platform=watch_dict,
                  cast=cast_dict,image=movie_images[i],rotten_reviews=reviewsRT,meta_reviews=reviewsMC,m_rating=meta_rating[i])
               m1.save()
               m1.similar_movies.add(*kwargs)
              #m1.save()
               cine_id=m1.id
        movies_id.append(cine_id)
        movie_obj.append(Movie.objects.get(id=cine_id))
        s10bj.movieobjects.add(Movie.objects.get(id=cine_id))
        s10bj.save()
    stuff={
         'shows_list' : shows_list,
         'movie_obj':movie_obj,
    }

    return render(response,"main/results.html",stuff)

def wishlist(request):
    movies = Movie.objects.filter(users_wishlist=request.user)
    return render(request, "main/watchlist.html", {"wishlist": movies})


def add_to_wishlist(request, id):
    product = get_object_or_404(Movie, id=id)
    if product.users_wishlist.filter(id=request.user.id).exists():
        product.users_wishlist.remove(request.user)
    else:
        if (product.users_watchedlist.filter(id=request.user.id).exists()):
            print("But you've already watched it!")
        else:
            product.users_wishlist.add(request.user)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

def favlist(request):
    movies = Movie.objects.filter(users_favlist=request.user)
    return render(request, "main/favlist.html", {"favlist": movies})

def add_to_favlist(request, id):
    product = get_object_or_404(Movie, id=id)
    if product.users_favlist.filter(id=request.user.id).exists():
        product.users_favlist.remove(request.user)
    else:
        product.users_favlist.add(request.user)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

def watchedlist(request):
    movies = Movie.objects.filter(users_watchedlist=request.user)
    return render(request, "main/watchedlist.html", {"watchedlist": movies})

def add_to_watchedlist(request, id):
    product = get_object_or_404(Movie, id=id)
    if product.users_watchedlist.filter(id=request.user.id).exists():
        product.users_watchedlist.remove(request.user)
    else:
        if (product.users_wishlist.filter(id=request.user.id).exists()):
            print("shifting movie from wishlist to watchedlist")
            product.users_wishlist.remove(request.user)
        product.users_watchedlist.add(request.user)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])
