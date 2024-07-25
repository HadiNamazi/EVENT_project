from django.contrib import admin
from . import models
from django.contrib.auth.signals import user_logged_in
import sys

sys.path.append("..")
from project import settings

def login_hook(sender, **kwargs):
    settings.SESSION_COOKIE_AGE = settings.ADMIN_SESSION_COOKIE_AGE

user_logged_in.connect(login_hook)

myModels = [
    models.CustomUser,
    models.Product,
    models.Category,
]
admin.site.register(myModels)