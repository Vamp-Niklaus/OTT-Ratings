from django.urls import path
from ottratings import views

urlpatterns = [
    path("", views.index, name='home'),
    path("media/<str:content_type>/<int:tmdb_id>/", views.media_detail, name='media_detail'),
    path("media/tv/<int:tmdb_id>/season/<int:season_number>/", views.episodes, name='episodes'),
    path("media/tv/<int:tmdb_id>/season/<int:season_number>/episode/<int:episode_number>/", views.episode, name='episode'),
    path("platform/<str:rplat>/", views.platform, name='platform'),
    path("language/<str:rlang>/", views.language, name='language'),
    path("category/<str:rcat>/", views.category, name='category'),
    path("year/<str:year>/", views.year, name='year'),
    path("sort/<str:sort>/", views.sort, name='sort'),
    path("comments", views.comments, name='comments'),
    path("ratings", views.ratings, name='ratings'),
    path("signup", views.signup, name='signup'),
    path("signin", views.signin, name='signin'),
    path("signout", views.signout, name='signout'),
    path("search", views.search, name='search'),
    path("contact", views.contact, name='contact'),
]