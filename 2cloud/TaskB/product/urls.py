from django.conf.urls import url
from .views import home
from .views import product_upload, product_edit, product_delete, product_list, product_search

urlpatterns = [
    url('home/', home, name='home'),
    url('upload/', product_upload, name='product_upload'),
    url('^edit/([0-9]+)/$', product_edit, name='product_edit'),
    url('^delete/([0-9]+)/$', product_delete, name='product_delete'),
    url('list/', product_list, name='product_list'),
    url('search/', product_search, name='product_search')
]