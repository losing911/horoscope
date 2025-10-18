from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .legal_views import (
    terms_of_service,
    privacy_policy,
    cookie_policy,
    kvkk_clarification,
    contact,
    legal_document,
    request_data_deletion,
    record_consent
)

app_name = 'accounts'

urlpatterns = [
    # Login/Logout
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Registration
    path('register/', views.register, name='register'),

    # Password Change
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

    # Profile
    path('profile/', views.profile, name='profile'),
    
    # Legal Documents
    path('kullanim-kosullari/', terms_of_service, name='terms_of_service'),
    path('gizlilik-politikasi/', privacy_policy, name='privacy_policy'),
    path('cerez-politikasi/', cookie_policy, name='cookie_policy'),
    path('kvkk/', kvkk_clarification, name='kvkk_clarification'),
    path('iletisim/', contact, name='contact'),
    path('legal/<slug:slug>/', legal_document, name='legal_document'),
    
    # KVKK API Endpoints
    path('api/request-deletion/', request_data_deletion, name='request_data_deletion'),
    path('api/record-consent/<str:document_type>/', record_consent, name='record_consent'),
]
