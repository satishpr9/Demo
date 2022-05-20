from pyexpat import model
from unicodedata import category
from django.db import models

# Create your models here.

class Item(models.Model):
    tittle=models.CharField(max_length=100)
    subtitle=models.CharField(max_length=50)
    price=models.PositiveBigIntegerField()

    def __str__(self) -> str:
        return self.tittle

class file(models.Model):
    def nameFile(instance, filename):
        return '/'.join(['images',str(instance.remark),filename])
    file= models.ImageField(upload_to=nameFile,null=True,blank=True)
    remark=models.CharField(max_length=20,default="satish",blank=True)

    def __str__(self) -> str:
        return self.remark