from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages


def register(request):
    """Kullanıcı kayıt sayfası"""
    if request.user.is_authenticated:
        return redirect('tarot:index')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Hoş geldiniz {user.username}! Hesabınız başarıyla oluşturuldu.')
            return redirect('tarot:index')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """Kullanıcı profil sayfası"""
    return render(request, 'accounts/profile.html')
