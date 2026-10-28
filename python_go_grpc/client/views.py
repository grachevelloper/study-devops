import logging

from grpc import RpcError

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from .api.client import Certs, Client


logger = logging.getLogger(__name__)
ICONS = ["?", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
GRPC_ADDR = "127.0.0.1:8443"
NGINX_ADDR = "127.0.0.1:9448"


def roll_die(addr):
    certs = settings.BASE_DIR / "certs"
    crt = Certs(certs / "ca.pem", certs / "client.pem", certs / "client-key.pem")
    return Client(addr, crt).roll_die()


def index(request):
    value_a, value_b = 0, 0

    if request.method == "POST":
        try:
            value_a = roll_die(GRPC_ADDR)
        except (RpcError, OSError):
            logger.exception("Direct gRPC request failed")

        try:
            value_b = roll_die(NGINX_ADDR)
        except (RpcError, OSError):
            logger.exception("gRPC request through nginx failed")

    ctx = {
        "icon_a": ICONS[value_a],
        "icon_b": ICONS[value_b],
        "sign": "=" if value_a == value_b else "<" if value_a < value_b else ">",
    }
    return render(request, "index.html", context=ctx)


def grpc(request):
    try:
        value = roll_die(GRPC_ADDR)
    except (RpcError, OSError):
        logger.exception("Direct gRPC request failed")
        return HttpResponse("gRPC unavailable", status=503)

    return HttpResponse("Value: " + ICONS[value])


def nginx(request):
    try:
        value = roll_die(NGINX_ADDR)
    except (RpcError, OSError):
        logger.exception("gRPC request through nginx failed")
        return HttpResponse("nginx unavailable", status=503)

    return HttpResponse("Value: " + ICONS[value])
