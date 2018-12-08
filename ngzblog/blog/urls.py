from django.conf.urls import url
from blog import views

urlpatterns = [
    # url(r'^backend/$', views.backend),
    # url(r'^add_article/$', views.add_article),
    # url(r'^upload/$', views.upload),
    # url(r'^(\w+)/$', views.home),
    url(r'^(\w[a-zA-Z]\w{5,17}@163.com)/(category|tag|archive)/(.*)/$', views.home),  # home(request, username, category, xx)
    url(r'^(\w[a-zA-Z]\w{5,17}@163.com)/p/(\d+)', views.article),
]