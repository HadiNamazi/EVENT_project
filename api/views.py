import http
import json
import sys
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from . import models
sys.path.append("..")
from django.conf import settings
from random import randint
from hashlib import sha256
from jdatetime import datetime

def phone_number_checker(phone_number):
    if len(phone_number) == 11 and phone_number[:2] == '09':
        return True
    return False

def confirm_code_sms(phone_number, code):
    conn = http.client.HTTPSConnection("api.sms.ir")
    payload = {
        "mobile": str(phone_number),
        "templateId": "271590",
        "parameters": [
            {'name': 'CODE' , 'value': str(code)},
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/plain',
        'x-api-key': '***'
    }

    # Encode payload and headers to bytes
    encoded_payload = json.dumps(payload).encode('utf-8')
    encoded_headers = {key.encode('utf-8'): value.encode('utf-8') for key, value in headers.items()}

    conn.request("POST", "/v1/send/verify", encoded_payload, encoded_headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")

def admin_sms(phone_number, code=None, phone_dest=None):
    conn = http.client.HTTPSConnection("api.sms.ir")
    payload = json.dumps({
        "lineNumber": 30007732912304,
        "messageTexts": [
            f"درخواست عضویت با شماره {str(phone_dest)}",
        ],
        "mobiles": [
            str(phone_number),
        ],
        "senddatetime": None
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/plain',
        'X-API-KEY': '***'
    }
    conn.request("POST", "/v1/send/likeToLike", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")

#-----------------------------------------------------------------------------------------------------

def main(req):
    if req.user.is_authenticated:
        if req.user.access_level == 0:
            settings.SESSION_COOKIE_AGE = settings.ADMIN_SESSION_COOKIE_AGE

        products = models.Product.objects.order_by('group', 'name')
        try:
            last_modified_arr = str(products[0].last_modified).split('-')
            last_modified = last_modified_arr[0] + '/' + last_modified_arr[1] + '/' + last_modified_arr[2]
        except:
            last_modified = ''
        context = {
            'access_level': req.user.access_level,
            'products': products,
            'last_modified': last_modified,
        }
        return render(req, 'api/main.html', context)
    return redirect('login-view')

def login_view(req):
    if req.user.is_authenticated:
        return redirect('main')
    
    if req.method == 'POST':
        try:
            phone_number = '0' + str(int(req.POST['phone_number']))
            if not phone_number_checker(phone_number):
                return render(req, 'api/login.html', context)
        except:
            return redirect('login-view')
        
        confirmation_code = str(randint(10000, 99999))
        try:
            confirm_code_sms(phone_number, confirmation_code)
        except:
            context = {'error': 'vpn'}
            return render(req, 'api/login.html', context)

        confirmation_code = '465' + confirmation_code + '9841' # just some salt
        confirmation_code = sha256(confirmation_code.encode('utf-8')).hexdigest()

        req.session['cc'] = confirmation_code
        req.session['pn'] = phone_number

        context = {'confirmation_code': confirmation_code}
        return render(req, 'api/sms_confirmation.html', context)

    elif req.method == 'GET':
        context = {}
        return render(req, 'api/login.html', context)
    
def logout_view(req):
    logout(req)
    return redirect('login-view')
    
def sms_confirmation(req):
    if req.user.is_authenticated:
        return redirect('main')

    if req.method == 'POST':
        confirmation_code = req.session.get('cc')
        phone_number = req.session.get('pn')
        cc_post = '465' + str(int(req.POST['verification_code'])) + '9841'
        cc_post = sha256(cc_post.encode('utf-8')).hexdigest()
        user = None
        try:
            user = models.CustomUser.objects.get(phone_number=phone_number)
        except:
            pass

        if confirmation_code is not None and phone_number is not None:
            if cc_post == confirmation_code:
                # register guest user
                if user is None:
                    user = models.CustomUser.objects.create(phone_number=phone_number, access_level=5)
                    user.save()

                login(req, user)

                now = str(datetime.today().strftime("%Y/%m/%d - %H:%M:%S"))
                if user.log is None or user.log == '':
                    user.log = '1 - ' + now
                else:
                    n = str(int(user.log.split(' ')[0]) + 1)
                    user.log = n + ' - ' + now + '\n' + user.log
                user.save()

                return redirect('main')
            return redirect('sms-confirmation')
    return redirect('login-view')

def register_req(req):
    if req.user.is_authenticated and req.user.access_level == 5:
        return render(req, 'api/register_req.html')
    return redirect('main')

def register_confirm(req):
    try:
        user = req.user
        user.register_req = True
        user.save()
        admin_sms('***', phone_dest=user.phone_number)
    except:
        pass
    return redirect('main')