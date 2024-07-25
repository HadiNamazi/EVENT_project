from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.login_view, name='login-view'),
    path('sms-confirmation/', views.sms_confirmation, name='sms-confirmation'),
    path('logout/', views.logout_view, name='logout-view'),
    path('register-req/', views.register_req, name='register-req'),
    path('register-req/confirm/', views.register_confirm, name='register-confirm'),
]
