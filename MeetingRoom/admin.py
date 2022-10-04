#Developer : SURENDRA 
#date : 2-Oct-2022
from django.contrib import admin
from .models import MeetingRoom, MonthlyUsage, Invoice



admin.site.register(MeetingRoom)

admin.site.register(MonthlyUsage)
admin.site.register(Invoice)
