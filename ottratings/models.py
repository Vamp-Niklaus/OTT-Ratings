from django.db import models
from django.contrib.auth.models import User

class Users(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(max_length=15, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}"

class Ratings(models.Model):
    content_type = models.CharField(max_length=20) # 'movie', 'tv'
    tmdb_id = models.IntegerField()
    season_number = models.IntegerField(default=0)
    episode_number = models.IntegerField(default=0)
    rating = models.FloatField()
    rby = models.ForeignKey(Users, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.content_type} {self.tmdb_id} - S{self.season_number}E{self.episode_number}: {self.rating}"

class Comments(models.Model):
    content_type = models.CharField(max_length=20) # 'movie', 'tv'
    tmdb_id = models.IntegerField()
    season_number = models.IntegerField(default=0)
    episode_number = models.IntegerField(default=0)
    c = models.TextField(max_length=150)
    cat = models.DateTimeField(auto_now_add=True)
    cby = models.ForeignKey(Users, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cby.user.username} on {self.content_type} {self.tmdb_id}"

class Contact(models.Model):
    customer = models.CharField(max_length=50)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    number = models.IntegerField()
    reason = models.TextField(max_length=300)

    def __str__(self):
        return self.customer