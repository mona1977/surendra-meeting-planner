#Developer : SURENDRA 
#date : 2-Oct-2022
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from .views import meeting_room_list, meeting_room_add, month_view
from .api import MeetingRoomAPIView, MeetingRoomTest, sending_email
from rest_framework import routers
from .makeinvoice2 import NewAPIView, NEWAPIView2
from . import my_payment

router = routers.DefaultRouter()


router.register(r'api', MeetingRoomAPIView)

urlpatterns = [
    # list/ is not for api
    path('list/', meeting_room_list),
    path('add/', meeting_room_add),
    path('download/', NewAPIView.as_view()),
    path('razorpay/', my_payment.do_payment),
    path('mailing/', sending_email),
    url(r'', include(router.urls))
]
