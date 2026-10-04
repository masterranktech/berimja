from django.urls import path
from .views_web import login_phone_view, verify_code_view, logout_view

app_name = 'accounts_web'

urlpatterns = [
    path('login/', login_phone_view, name='login_phone'),
    path('login/verify/', verify_code_view, name='verify_code'),
    path('logout/', logout_view, name='logout'),
]