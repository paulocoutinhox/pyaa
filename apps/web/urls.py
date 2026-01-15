"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from .views import account, banner, contact, content, gallery, home, newsletter
from .views.shop import shop_web, shop_webhook

urlpatterns = []

urlpatterns += home.urlpatterns
urlpatterns += account.urlpatterns
urlpatterns += content.urlpatterns
urlpatterns += gallery.urlpatterns
urlpatterns += contact.urlpatterns
urlpatterns += shop_web.urlpatterns
urlpatterns += shop_webhook.urlpatterns
urlpatterns += banner.urlpatterns
urlpatterns += newsletter.urlpatterns
