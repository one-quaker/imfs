import os
import sys

from .models import Photo, Wallet


def get_ip():
    if sys.platform == 'darwin':
        cmd = 'ifconfig en0|grep -v inet6|grep inet'
    else:
        cmd = 'ifconfig wlan0|grep -v inet6|grep inet'
    out = os.popen(cmd).read()
    try:
        ip = out.strip().split(' ')[1]
    except:
        ip = 'unknown'
    print(sys.platform)
    return ip


def get_base_data(request):
    ctx = {}
    ctx['ip'] = get_ip()
    ctx['main_url'] = 'http://{ip}:8000'.format(**ctx)
    ctx['wallet'] = Wallet.objects.first()
    return ctx
