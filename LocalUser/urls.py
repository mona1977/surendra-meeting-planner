#Developer : SURENDRA 
#date : 2-Oct-2022
from django.urls import path, include
from django.conf.urls import url
from .api import (
    RegisterAPI,
    LoginAPI,
    UserAPI,
    CompanyAPIView
)
from knox import views as knox_views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'api', CompanyAPIView)

urlpatterns = [


    url(r'^api/auth/login/', (LoginAPI.as_view()), name='mylogin'),
 
    url(r'^company/', include(router.urls)),


    path(r'api/auth/user/', UserAPI.as_view()),
    path(r'api/auth/register/', RegisterAPI.as_view()),
    path(r'api/auth/logout/', knox_views.LogoutView.as_view(), name="knox_logout"),
    path(r'api/auth/logallout/', knox_views.LogoutAllView.as_view(), name='knox_logallout'),
    path(r'api/myauth/', include('knox.urls'))
]