from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Views(models.Model):
    v_id=models.FloatField(primary_key= True)
    sum=models.FloatField()
    count=models.PositiveIntegerField()
    on_what=models.CharField(max_length=3)
    def __str__(self):
        return str(self.v_id) + ", " + str(self.sum) + ", " + str(self.count)
    
    
class Users(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    birthday = models.DateField()
    gender = models.CharField(
        max_length=11,
        choices=[('Male','Male'),('Female','Female'),('Other','Other')]
    )
    def __str__(self):
        return self.user.username
    

class Ratings(models.Model):
    ron=models.ForeignKey(Views,db_column='ron', on_delete=models.CASCADE)
    rby=models.ForeignKey(Users,db_column='rby', on_delete=models.CASCADE)
    rating=models.FloatField()
    rorb_id=models.AutoField(primary_key = True)
    class Meta:
        unique_together = (("ron", "rby"))
    def __str__(self):
        return  str(self.ron.v_id) + ", " + self.rby.user.username +", " + str(self.rating)
        

class Comments(models.Model):
    tag=models.PositiveIntegerField()
    con=models.ForeignKey(Views,db_column='con', on_delete=models.CASCADE)
    c=models.CharField(max_length=100)
    cby=models.ForeignKey(Users,db_column='cby', on_delete=models.CASCADE)
    cat=models.DateTimeField()
    cocb_id=models.AutoField(primary_key = True)
    class Meta:
        unique_together = (("con", "cby","cat"))
    def __str__(self):
        return  str(self.con.v_id) + ", " +  self.cby.user.username +", " + self.c
    
        
class Cat_list(models.Model):
    category=models.CharField(max_length=30,primary_key = True)
    def __str__(self):
        return self.category
    
class Lang_list(models.Model):
    language=models.CharField(max_length=30,primary_key = True)
    def __str__(self):
        return self.language
    
class plat_list(models.Model):
    platform=models.CharField(max_length=30,primary_key = True)
    def __str__(self):
        return self.platform
    
class Web(models.Model):
    web_id=models.FloatField(primary_key= True)
    w_name=models.CharField(max_length=50)
    release_year=models.PositiveIntegerField()
    seasons=models.PositiveIntegerField()
    rating=models.FloatField(null=True, blank=True)
    studio=models.CharField(max_length=30)
    ageplus=models.PositiveIntegerField()
    portrait = models.ImageField(upload_to='static/upload')
    landscape = models.ImageField(upload_to='static/upload')
    def __str__(self):
        return str(self.web_id) + ", " + self.w_name
    
    
    
class Season(models.Model):
    web_id=models.ForeignKey(Web, db_column='web_id',on_delete=models.CASCADE)
    episodes=models.PositiveIntegerField()
    release_year=models.PositiveIntegerField()
    rating=models.FloatField(null=True, blank=True)
    sea_id=models.FloatField(primary_key= True)
    def __str__(self):
        return str(self.sea_id)
    
    
class Episode(models.Model):
    sea_id=models.ForeignKey(Season, db_column='sea_id',on_delete=models.CASCADE)
    e_name=models.CharField(max_length=100)
    rating=models.FloatField(null=True, blank=True)
    run_time=models.TimeField()
    epi_id=models.FloatField(primary_key= True)
    def __str__(self):
        return str(self.epi_id)
    
    
class Available_on(models.Model):
    avap_id=models.AutoField(primary_key = True)
    web_id=models.ForeignKey(Web, db_column='web_id',on_delete=models.CASCADE)
    platform=models.ForeignKey(plat_list,db_column='platform', on_delete=models.CASCADE)
    class Meta:
        unique_together = (("web_id", "platform"))
    def __str__(self):
        return  self.web_id.w_name + ", " + self.platform.platform
    
    
class Categories(models.Model):
    cwcc_id=models.AutoField(primary_key = True)
    web_id=models.ForeignKey(Web, db_column='web_id',on_delete=models.CASCADE)
    category=models.ForeignKey(Cat_list,db_column='category', on_delete=models.CASCADE)
    class Meta:
        unique_together = (("web_id", "category"))
    def __str__(self):
        return self.web_id.w_name + ", " + self.category.category
    

class Languages(models.Model):
    lwll_id=models.AutoField(primary_key = True)
    web_id=models.ForeignKey(Web, db_column='web_id',on_delete=models.CASCADE)
    language=models.ForeignKey(Lang_list,db_column='language', on_delete=models.CASCADE)
    class Meta:
        unique_together = (("web_id", "language"))
    def __str__(self):
        return self.web_id.w_name + ", " + self.language.language

class Contact(models.Model):
    c_id=models.PositiveIntegerField()
    customer=models.CharField(max_length=150)
    first_name=models.CharField(max_length=150)
    last_name=models.CharField(max_length=150)
    email=models.CharField(max_length=254)
    reason=models.CharField(max_length=500)
    at=models.DateTimeField()
    number=models.CharField(max_length=16)
    def __str__(self):
        return  self.first_name + " " +  self.last_name +" (" + self.customer +")"