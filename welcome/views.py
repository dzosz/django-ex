import os
import json
import requests
import pprint
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from . import database
from .models import PageView

# Create your views here.
CLIENT_ID = os.getenv('CLIENT_ID', 'unknown')

def index(request):
    hostname = os.getenv('HOSTNAME', 'unknown')
    PageView.objects.create(hostname=hostname)

    host = request.get_host()
    if not host.startswith('http'):
        host = 'http://' + host

    uri = host + '/login'
    link = 'https://api.instagram.com/oauth/authorize/?client_id=%s&redirect_uri=%s&response_type=token&scope=follower_list+basic' % (CLIENT_ID, uri)

    return render(request, 'welcome/index.html', {
        'hostname': hostname,
        'database': database.info(),
        'count': PageView.objects.count(),
        'link': link,
    })

def login(request):
    token = request.GET.get('access_token', '')
    #user = request.GET.get('user', '')

    api_link = 'https://api.instagram.com/v1/users/self/?access_token=' + token
    data = requests.get(api_link).json()
    return HttpResponse(json.dumps(data), content_type='application/json')

def health(request):
    return HttpResponse(PageView.objects.count())
