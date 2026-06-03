from django.shortcuts import render, redirect
from ottratings.models import Contact, Comments, Users, Ratings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Avg
from . import tmdb

def get_navbar_context():
    sort_options = [
        {'id': 'popularity.desc', 'name': 'Popularity'},
        {'id': 'vote_average.desc', 'name': 'Rating'},
        {'id': 'primary_release_date.desc', 'name': 'Release Date (Newest)'},
        {'id': 'primary_release_date.asc', 'name': 'Release Date (Oldest)'}
    ]
    return {
        'cat': tmdb.get_genres(),
        'lan': tmdb.get_languages(),
        'plat': tmdb.get_providers(),
        'year': range(2024, 1887, -1),
        'sort': sort_options
    }

def format_tmdb_results(results):
    formatted = []
    for item in results:
        tmdb_id = item.get('id')
        title = item.get('title', item.get('name', ''))
        if not tmdb_id or not title or not item.get('poster_path') or item.get('adult') == True:
            continue
            
        release_date = item.get('release_date') or item.get('first_air_date')
        year = None
        if release_date and len(release_date) >= 4:
            try:
                year = int(release_date[:4])
            except:
                pass
                
        portrait = f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None
        
        # Calculate local rating if available
        content_type = 'movie' if 'title' in item else 'tv'
        local_avg = Ratings.objects.filter(
            content_type=content_type, 
            tmdb_id=tmdb_id, 
            season_number=0, 
            episode_number=0
        ).aggregate(Avg('rating'))['rating__avg']
        
        local_rating = round(local_avg, 1) if local_avg else round(item.get('vote_average', 0.0), 1)
        
        formatted.append({
            'id': tmdb_id,
            'w_name': title,
            'portrait': portrait,
            'local_rating': local_rating,
            'content_type': content_type
        })
    return formatted

def render_media_list(request, results, context):
    context['web'] = format_tmdb_results(results)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'partials/media_cards.html', context)
    return render(request, 'index.html', context)

def index(request):
    page = request.GET.get('page', 1)
    results = tmdb.fetch_trending(page=page)
    context = get_navbar_context()
    return render_media_list(request, results, context)

def media_detail(request, content_type, tmdb_id):
    if content_type == 'movie':
        details = tmdb.get_movie_details(tmdb_id)
    else:
        details = tmdb.get_tv_details(tmdb_id)
        
    if not details:
        messages.error(request, "Media not found.")
        return redirect('home')
        
    title = details.get('title', details.get('name', ''))
    landscape = f"https://image.tmdb.org/t/p/w1280{details.get('backdrop_path')}" if details.get('backdrop_path') else None
    
    local_avg = Ratings.objects.filter(
        content_type=content_type, 
        tmdb_id=tmdb_id, 
        season_number=0, 
        episode_number=0
    ).aggregate(Avg('rating'))['rating__avg']
    
    local_rating = round(local_avg, 1) if local_avg else round(details.get('vote_average', 0.0), 1)
    
    web = {
        'id': tmdb_id,
        'w_name': title,
        'landscape': landscape,
        'local_rating': local_rating,
        'content_type': content_type,
        'overview': details.get('overview', '')
    }
    
    context = get_navbar_context()
    context['web'] = web
    context['cast'] = details.get('credits', {}).get('cast', [])[:12]
    context['com'] = Comments.objects.filter(content_type=content_type, tmdb_id=tmdb_id, season_number=0, episode_number=0).order_by("-cat")
    
    if request.user.is_authenticated:
        user_rating_obj = Ratings.objects.filter(content_type=content_type, tmdb_id=tmdb_id, season_number=0, episode_number=0, rby=request.user.users).first()
        if user_rating_obj:
            context['user_rating'] = int(user_rating_obj.rating)
    
    if content_type == 'tv':
        seasons = []
        for s in details.get('seasons', []):
            if s.get('season_number') == 0:
                continue
            
            s_local_avg = Ratings.objects.filter(
                content_type='tv', 
                tmdb_id=tmdb_id, 
                season_number=s.get('season_number'), 
                episode_number=0
            ).aggregate(Avg('rating'))['rating__avg']
            
            s_rating = round(s_local_avg, 1) if s_local_avg else round(s.get('vote_average', 0.0), 1)
            portrait = f"https://image.tmdb.org/t/p/w500{s.get('poster_path')}" if s.get('poster_path') else "https://via.placeholder.com/500x750?text=No+Poster"
            
            seasons.append({
                'season_number': s.get('season_number'),
                'w_name': s.get('name'),
                'local_rating': s_rating,
                'portrait': portrait,
                'id': f"{tmdb_id}/season/{s.get('season_number')}",
                'content_type': 'tv'
            })
        context['sea'] = seasons
        return render(request, 'seasons.html', context)
    else:
        return render(request, 'seasons.html', context)

def episodes(request, tmdb_id, season_number):
    details = tmdb.get_tv_details(tmdb_id)
    s_details = tmdb.get_tv_season(tmdb_id, season_number)
    if not details or not s_details:
        return redirect('home')
        
    title = details.get('title', details.get('name', ''))
    landscape = f"https://image.tmdb.org/t/p/w1280{details.get('backdrop_path')}" if details.get('backdrop_path') else None
    
    web_local_avg = Ratings.objects.filter(content_type='tv', tmdb_id=tmdb_id, season_number=0, episode_number=0).aggregate(Avg('rating'))['rating__avg']
    web_local_rating = round(web_local_avg, 1) if web_local_avg else round(details.get('vote_average', 0.0), 1)
    
    web = {'id': tmdb_id, 'w_name': title, 'landscape': landscape, 'local_rating': web_local_rating, 'content_type': 'tv'}
    
    s_local_avg = Ratings.objects.filter(content_type='tv', tmdb_id=tmdb_id, season_number=season_number, episode_number=0).aggregate(Avg('rating'))['rating__avg']
    s_local_rating = round(s_local_avg, 1) if s_local_avg else round(s_details.get('vote_average', 0.0), 1)
    
    sea = {'season_number': season_number, 'local_rating': s_local_rating}
    
    episodes_list = []
    for ep in s_details.get('episodes', []):
        ep_local_avg = Ratings.objects.filter(
            content_type='tv', 
            tmdb_id=tmdb_id, 
            season_number=season_number, 
            episode_number=ep.get('episode_number')
        ).aggregate(Avg('rating'))['rating__avg']
        
        ep_rating = round(ep_local_avg, 1) if ep_local_avg else round(ep.get('vote_average', 0.0), 1)
        still = f"https://image.tmdb.org/t/p/w500{ep.get('still_path')}" if ep.get('still_path') else "https://via.placeholder.com/500x281?text=No+Image"
        
        episodes_list.append({
            'episode_number': ep.get('episode_number'),
            'e_name': ep.get('name'),
            'local_rating': ep_rating,
            'portrait': still,
            'w_name': f"Ep {ep.get('episode_number')}: {ep.get('name')}",
            'id': f"{tmdb_id}/season/{season_number}/episode/{ep.get('episode_number')}",
            'content_type': 'tv'
        })
        
    context = get_navbar_context()
    context['web'] = web
    context['sea'] = sea
    context['epi'] = episodes_list
    context['cast'] = s_details.get('credits', {}).get('cast', [])[:12]
    context['com'] = Comments.objects.filter(content_type='tv', tmdb_id=tmdb_id, season_number=season_number, episode_number=0).order_by("-cat")
    
    if request.user.is_authenticated:
        user_rating_obj = Ratings.objects.filter(content_type='tv', tmdb_id=tmdb_id, season_number=season_number, episode_number=0, rby=request.user.users).first()
        if user_rating_obj:
            context['user_rating'] = int(user_rating_obj.rating)
    
    return render(request, 'episodes.html', context)

def episode(request, tmdb_id, season_number, episode_number):
    details = tmdb.get_tv_details(tmdb_id)
    s_details = tmdb.get_tv_season(tmdb_id, season_number)
    ep_details = tmdb.get_tv_episode(tmdb_id, season_number, episode_number)
    
    if not details or not ep_details:
        return redirect('home')
        
    title = details.get('title', details.get('name', ''))
    landscape = f"https://image.tmdb.org/t/p/w1280{details.get('backdrop_path')}" if details.get('backdrop_path') else None
    
    web_local_avg = Ratings.objects.filter(content_type='tv', tmdb_id=tmdb_id, season_number=0, episode_number=0).aggregate(Avg('rating'))['rating__avg']
    web_local_rating = round(web_local_avg, 1) if web_local_avg else round(details.get('vote_average', 0.0), 1)
    web = {'id': tmdb_id, 'w_name': title, 'landscape': landscape, 'local_rating': web_local_rating, 'content_type': 'tv'}
    
    s_local_avg = Ratings.objects.filter(content_type='tv', tmdb_id=tmdb_id, season_number=season_number, episode_number=0).aggregate(Avg('rating'))['rating__avg']
    s_local_rating = round(s_local_avg, 1) if s_local_avg else round(s_details.get('vote_average', 0.0), 1)
    sea = {'season_number': season_number, 'local_rating': s_local_rating}
    
    ep_local_avg = Ratings.objects.filter(content_type='tv', tmdb_id=tmdb_id, season_number=season_number, episode_number=episode_number).aggregate(Avg('rating'))['rating__avg']
    ep_local_rating = round(ep_local_avg, 1) if ep_local_avg else round(ep_details.get('vote_average', 0.0), 1)
    
    epi = {
        'episode_number': episode_number,
        'e_name': ep_details.get('name'),
        'local_rating': ep_local_rating
    }
    
    context = get_navbar_context()
    context['web'] = web
    context['sea'] = sea
    context['epi'] = epi
    context['run_time'] = f"{ep_details.get('runtime', 'N/A')} mins"
    context['overview'] = ep_details.get('overview', '')
    context['cast'] = ep_details.get('guest_stars', [])[:12]
    context['com'] = Comments.objects.filter(content_type='tv', tmdb_id=tmdb_id, season_number=season_number, episode_number=episode_number).order_by("-cat")
    
    if request.user.is_authenticated:
        user_rating_obj = Ratings.objects.filter(content_type='tv', tmdb_id=tmdb_id, season_number=season_number, episode_number=episode_number, rby=request.user.users).first()
        if user_rating_obj:
            context['user_rating'] = int(user_rating_obj.rating)
    
    return render(request, 'episode.html', context)

def comments(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            content_type = request.POST.get('content_type')
            tmdb_id = int(request.POST.get('tmdb_id'))
            season_number = int(request.POST.get('season_number', 0))
            episode_number = int(request.POST.get('episode_number', 0))
            c = request.POST.get('c')
            
            if len(c) > 100:
                messages.error(request, "Comments must be under 100 characters!")
            elif len(c) < 1:
                messages.error(request, "Comments can't be empty!")
            else:
                Comments.objects.create(
                    content_type=content_type, 
                    tmdb_id=tmdb_id, 
                    season_number=season_number,
                    episode_number=episode_number,
                    c=c, 
                    cby=request.user.users
                )
                messages.success(request, "Your comment saved successfully!")
                
            if episode_number > 0:
                return redirect('episode', tmdb_id=tmdb_id, season_number=season_number, episode_number=episode_number)
            elif season_number > 0:
                return redirect('episodes', tmdb_id=tmdb_id, season_number=season_number)
            else:
                return redirect('media_detail', content_type=content_type, tmdb_id=tmdb_id)
    else:
        messages.error(request, "You must be logged in for comment!")
        return redirect('home')
    
def ratings(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            content_type = request.POST.get('content_type')
            tmdb_id = int(request.POST.get('tmdb_id'))
            season_number = int(request.POST.get('season_number', 0))
            episode_number = int(request.POST.get('episode_number', 0))
            star = float(request.POST.get('star'))
            
            rating_obj, created = Ratings.objects.update_or_create(
                content_type=content_type,
                tmdb_id=tmdb_id,
                season_number=season_number,
                episode_number=episode_number,
                rby=request.user.users,
                defaults={'rating': star}
            )
            
            msg = "Your rating saved successfully!" if created else "Your rating updated successfully!"
            messages.success(request, msg)
            
            if episode_number > 0:
                return redirect('episode', tmdb_id=tmdb_id, season_number=season_number, episode_number=episode_number)
            elif season_number > 0:
                return redirect('episodes', tmdb_id=tmdb_id, season_number=season_number)
            else:
                return redirect('media_detail', content_type=content_type, tmdb_id=tmdb_id)
    else:
        messages.error(request, "You must be logged in for rating!!")
        return redirect('home')

def search(request):
    target = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    results = tmdb.search_tmdb(target, page=page)
    if not results and int(page) == 1:
        messages.error(request, "Sorry! No Matches Found!")
        return redirect('home')
        
    context = get_navbar_context()
    return render_media_list(request, results, context)

def category(request, rcat):
    try:
        genre_id = int(rcat)
    except:
        genre_id = None
        
    page = request.GET.get('page', 1)
    results = tmdb.discover_movies(genre_id=genre_id, page=page) + tmdb.discover_tv(genre_id=genre_id, page=page)
    
    context = get_navbar_context()
    return render_media_list(request, results, context)

def platform(request, rplat):
    try:
        provider_id = int(rplat)
    except:
        provider_id = None
        
    page = request.GET.get('page', 1)
    results = tmdb.discover_movies(provider_id=provider_id, page=page) + tmdb.discover_tv(provider_id=provider_id, page=page)
    
    context = get_navbar_context()
    return render_media_list(request, results, context)

def language(request, rlang):
    page = request.GET.get('page', 1)
    results = tmdb.discover_movies(language=rlang, page=page) + tmdb.discover_tv(language=rlang, page=page)
    
    context = get_navbar_context()
    return render_media_list(request, results, context)

def year(request, year):
    page = request.GET.get('page', 1)
    results = tmdb.discover_movies(year=year, page=page) + tmdb.discover_tv(year=year, page=page)
    
    context = get_navbar_context()
    return render_media_list(request, results, context)

def sort(request, sort):
    page = request.GET.get('page', 1)
    results = tmdb.discover_movies(sort_by=sort, page=page) + tmdb.discover_tv(sort_by=sort, page=page)
    
    context = get_navbar_context()
    return render_media_list(request, results, context)

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists! Please try another.")
            return redirect('signup')
        
        myuser = User.objects.create_user(username=username, password=pass1)
        myuser.save()
        Users.objects.create(user=myuser)
        messages.success(request, "Your Account has been created successfully!!")
        return redirect('signin')
        
    context = get_navbar_context()
    return render(request, 'signup.html', context)

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        user = authenticate(username=username, password=pass1)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged In Successfully!!")
            return redirect('home')
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('signin')
            
    context = get_navbar_context()
    return render(request, "signin.html", context)

def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')

def contact(request):
    if request.method == "POST" and request.user.is_authenticated:
        reason = request.POST['reason']
        number = request.POST['number']
        Contact.objects.create(
            customer=request.user.username,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            email=request.user.email,
            reason=reason,
            number=number
        )
        messages.success(request, "Your message sent successfully!!")
        return redirect('home')
        
    context = get_navbar_context()
    return render(request, 'contact.html', context)