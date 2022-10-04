#Developer : SURENDRA 
#date : 2-Oct-2022
from django.db import models
from LocalUser.models import Company
from datetime import datetime, timezone

# Create your models here.
class MeetingRoom(models.Model):
   
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING)
    start = models.DateTimeField()
    end = models.DateTimeField()


    allowed = models.BooleanField(default=False)
    used_till_date = models.FloatField(default=0)

    def __str__(self):
        now = datetime.now(timezone.utc)
        return str(self.company) + " START= " + str(self.start) + " \n End=" + str(self.end) + " ALLOWED=" + str(self.allowed)


class MonthlyUsage(models.Model):
    month = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING)
    
    used_this_month = models.FloatField(default=0)
   
    used_till_date = models.FloatField(default=0, null=True)

    def __str__(self):
        available_time = self.company.allotted - self.used_this_month
        return str(self.company) + " " + str(self.used_this_month) + " TIME LEFT= " + str(available_time)


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=2000, null=True, default="000")
    meeting_room = models.ForeignKey('MeetingRoom', on_delete=models.DO_NOTHING)
    invoice_file = models.FileField(upload_to='invoices/')
