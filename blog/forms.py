from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    """Yorum formu"""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Yorumunuzu yazın...',
                'required': True
            })
        }
        labels = {
            'content': ''
        }


class GuestCommentForm(forms.ModelForm):
    """Misafir kullanıcı yorum formu"""
    
    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adınız',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'E-posta adresiniz',
                'required': True
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Yorumunuzu yazın...',
                'required': True
            })
        }
        labels = {
            'name': 'İsim',
            'email': 'E-posta',
            'content': 'Yorum'
        }
