import os
import json
import requests
import urllib
import pprint
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from . import database
from .models import PageView

# Create your views here.
CLIENT_ID = os.getenv('CLIENT_ID', 'unknown')
CLIENT_SECRET = os.getenv('CLIENT_SECRET', 'unknown')

def get_redirect_uri(request):
    host = request.get_host()
    if not host.startswith('http'):
        host = 'http://' + host

    uri = host + '/login'
    return uri;

def index(request):
    hostname = os.getenv('HOSTNAME', 'unknown')
    PageView.objects.create(hostname=hostname)

    uri = get_redirect_uri(request)
    link = 'https://api.instagram.com/oauth/authorize/?client_id=%s&redirect_uri=%s&response_type=code&scope=follower_list+basic' % (CLIENT_ID, uri)

    return render(request, 'welcome/index.html', {
        'hostname': hostname,
        'database': database.info(),
        'count': PageView.objects.count(),
        'link': link,
    })

def login(request):
    code = request.GET.get('code', '')

    api_link = 'https://api.instagram.com/oauth/access_token'
    uri = get_redirect_uri(request)
    params = {'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': uri,
            'code': code}

    txt = '&'.join(['?client_id='+ CLIENT_ID,
            'client_secret='+ CLIENT_SECRET,
            'grant_type='+ 'authorization_code',
            'redirect_uri='+ uri,
            'code='+ code])

    data = urllib.parse.urlencode(params)
    data = data.encode('ascii')
    req = urllib.request.Request(api_link, data=data, method='POST')
    res = urllib.request.urlopen(req)
    data = res.read()
    if res.getcode() == 200:
        data = data.decode('ascii')
        user = json.loads(data)['user']
        return HttpResponse(json.dumps(user), content_type='application/json')

    return HttpResponse("ERROR: ", data)

def health(request):
    return HttpResponse(PageView.objects.count())
