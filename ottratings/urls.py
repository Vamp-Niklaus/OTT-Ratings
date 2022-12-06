from django.contrib import admin
from django.urls import path
from ottratings import views

urlpatterns = [
    path("", views.index,name='home'),
    path("seasons/<str:web_id>/", views.seasons,name='seasons'),
    path("episodes/<str:sea_id>/", views.episodes,name='episodes'),
    path("episode/<str:epi_id>/", views.episode,name='episode'),
    path("platform/<str:rplat>/", views.platform,name='platform'),
    path("language/<str:rlang>/", views.language,name='language'),
    path("category/<str:rcat>/", views.category,name='category'),
    path("year/<str:year>/", views.year,name='year'),
    path("sort/<str:sort>/", views.sort,name='sort'),
    path("comments", views.comments,name='comments'),
    path("ratings", views.ratings,name='ratings'),
    path("signup", views.signup,name='signup'),
    path("signin", views.signin,name='signin'),
    path("signout", views.signout,name='signout'),
    path("search", views.search,name='search'),
    path("contact", views.contact,name='contact'),
]