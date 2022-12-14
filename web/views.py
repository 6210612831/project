import requests
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import *
from django.urls import reverse
from rest_framework import status
from .utils import check_2_factor_authen


# Goold Authenticator
import pyotp
import time
from django.http import JsonResponse
from .models import AuthInfo,ChannelForAPI
import qrcode
import json
from io import BytesIO
import base64

# Create your views here.
HOST = "http://127.0.0.1:8000"


def index(request):
    try:
        if request.session['user_id']:
            # print(request.session['user_id'])
            return render(request, "web/home.html", {'name': request.session['user_id']})
    except Exception as e:
        print(e)
        return render(request, "web/index.html")


def login_view(request):
    try:
        if request.session['user_id']:
            # print(request.session['user_id'])
            return render(request, "web/index2.html", {'name': response.json()['name']})
    except:
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            # response = ldap3_authen(username,password)
            data = {
                'username': username,
                'password': password
            }
            response = requests.post(
                HOST+'/api/v1/authentication/', data=data)
            if response.status_code == status.HTTP_200_OK:
                request.session['user_id'] = username
                print(request.session['user_id'])
                # print("render policy page")
                request.session['login_status'] = username
                request.session.modified = True
                # return render(request, "web/policy.html")
                return HttpResponseRedirect(reverse("web:pdpa_page"))
            else:
                return render(request, "web/login.html")
        return render(request, "web/login.html")


def logout_view(request):
    del request.session['user_id']
    return HttpResponseRedirect(reverse("web:index"))


def pdpa_page(request):
    try:
        if request.session['user_id']:
            return render(request, "web/policy.html")
    except Exception as e:
        # print(request.session['user_id'])
        # print(e)
        return render(request, "web/index.html")


def setting_page(request):
    return render(request, "web/setting.html")


def privacy_page(request):
    return render(request, "web/privacy.html")


def home(request):
    return render(request, "web/home.html")


def channel_page(request):
    return render(request, "web/channel.html")


def document(request):
    return render(request, "web/document.html")


def report_page(request):
    return render(request, "web/report.html")


def help_page(request):
    return render(request, "web/help.html")


def update_page(request):
    return render(request, "web/update.html")


def createChannel_page(request):
    try:
        if request.session['user_id']:
            channels = ChannelForAPI.objects.filter(user=request.session['user_id'])
            channel_lists =[]
            for channel in channels:
                channel_lists.append(channel)
            return render(request, "web/authkey.html",{'channel_list':channel_lists})
    except Exception as e:
        # print(request.session['user_id'])
        # print(e)
        return render(request, "web/index.html")
    
    


def getStart_page(request):
    return render(request, "web/documentsGettingStart.html")


def twoFactor_page(request):
    return render(request, "web/documentsTwoFactor.html")



def test_page(request,pin):
    try:
        authtor = AuthInfo.objects.get(user=request.session['user_id'])
        secret_key = authtor.secret_key
    except:
        secret_key = pyotp.random_base32()
        AuthInfo.objects.create(user=request.session['user_id'],secret_key=secret_key)
    # Check TOTP
    totp = pyotp.TOTP(secret_key)
    # Create QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(secret_key)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    # Save img and convert to str for sent to frontend and render
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("ascii")

    return render(request, "web/test_page.html",{'data':{'status':'True' if totp.verify(pin) else 'False' ,'image':img_str}})


def check2fa_view(request):
    data =json.loads(request.body)
    pin = data['pin']
    user_id = data['user_id']
    chname = data['chname']
    chdesc = data['chdesc']
    # Check 2FA Pin
    response = check_2_factor_authen(user_id,pin)
    if response['status'] == 'True':
        # Create Channel
        ChannelForAPI.objects.create(name=chname,desc=chdesc,user=user_id,status=False)
        # Reture Status If channel created
        data = {'status':'True'}
        response = JsonResponse(data)
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    else:
        # Reture Status If channel not created
        data = {'status':'False'}
        response = JsonResponse(data)
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response

        

