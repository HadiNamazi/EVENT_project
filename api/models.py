from datetime import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from . import managers
from jdatetime import date
from django_jalali.db import models as jmodels


class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    access_level = models.IntegerField(blank=False, null=False) # 0(admin) -...- 4 - 5(guest)
    register_req = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=11, blank=False, null=False, unique=True)
    is_staff = models.BooleanField(default=False)
    log = models.TextField(null=True, blank=True)
    password = models.CharField(max_length=200, blank=True, null=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = managers.CustomUserManager()

    def __str__(self):
        if self.name == '' and self.lastname == '':
            return self.phone_number
        return f'{self.name} {self.lastname}'

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Product(models.Model):
    group = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=50, blank=False, null=False)
    price1 = models.IntegerField(blank=False, null=False)
    price2 = models.IntegerField(blank=False, null=False)
    price3 = models.IntegerField(blank=False, null=False)
    price4 = models.IntegerField(blank=False, null=False)
    last_modified = jmodels.jDateField(default=date.today().strftime("%Y-%m-%d"))

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Update the last_modified field with the current time before saving the object
        self.last_modified = date.today().strftime("%Y-%m-%d")
        super(Product, self).save(*args, **kwargs)