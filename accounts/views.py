from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, UserProfileForm


def register(request):
    """Kullanıcı kayıt sayfası"""
    if request.user.is_authenticated:
        return redirect('tarot:index')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(request=request)  # request parametresini geç
            login(request, user)
            username = user.username
            messages.success(request, f'Hoş geldiniz {username}! Hesabınız başarıyla oluşturuldu.')
            return redirect('tarot:index')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """Kullanıcı profil sayfası"""
    from accounts.models import TokenPackage
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profiliniz başarıyla güncellendi.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Token paketlerini al
    token_packages = TokenPackage.objects.filter(is_active=True).order_by('display_order', 'price')
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'token_packages': token_packages
    })


def logout_view(request):
    """Kullanıcı çıkış sayfası - GET ve POST destekler"""
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('tarot:index')
