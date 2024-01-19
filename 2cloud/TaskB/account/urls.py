from django.conf.urls import url
from .views import register, user_login, user_logout

urlpatterns = [
    url('register/', register, name='register'),
    url('login/', user_login, name='login'),
    url('logout/', user_logout, name='logout'),
]
