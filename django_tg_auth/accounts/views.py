# accounts/views.py
# Django приложение: accounts

from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.conf import settings
from .models import CustomUser
import hashlib
import time
from django.contrib.auth.decorators import login_required


def check_auth(request):
    return JsonResponse({'is_authenticated': request.user.is_authenticated})

def logout_view(request):
    logout(request)
    return redirect('index') 

@login_required
def test(request):
    return HttpResponse(f"Вы авторизованы как {request.user.username}")

def index(request):
    print(request.user)
    return render(request, "accounts/index.html", {"user": request.user})

def login_page(request):
    if not request.session.session_key:
        request.session.save()
    bot_username = settings.TELEGRAM_BOT_USERNAME
    return render(request, "accounts/login.html", {"bot_username": bot_username})

def telegram_callback(request):
    """Обрабатывает ответ от Telegram-бота"""
    data = request.GET
    telegram_id = data.get("id")
    username = data.get("username")

    # Простой пример верификации
    check_hash = data.get("hash")
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    hash_data = "\n".join([f"{k}={v}" for k, v in sorted(data.items()) if k != "hash"])
    if check_hash != hashlib.sha256((hash_data + secret_key).encode()).hexdigest():
        return JsonResponse({"error": "Invalid hash"}, status=400)

    user, created = CustomUser.objects.get_or_create(telegram_id=telegram_id)
    if username:
        user.telegram_username = username
        user.save()

    login(request, user)
    return JsonResponse({"status": "ok"})
