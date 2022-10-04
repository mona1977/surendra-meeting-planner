#Developer : SURENDRA 
#date : 2-Oct-2022
from django.db import models
from LocalUser.models import UserProfile


# Create your models here.
class Invoice(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING)
    invoice_number = models.CharField(max_length=2000, null=True, default="000")
   
    invoice_file = models.FileField(upload_to='invoices/')
