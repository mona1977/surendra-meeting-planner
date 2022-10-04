#Developer : SURENDRA 
#date : 2-Oct-2022
from rest_framework import generics, permissions, viewsets, status, mixins
from rest_framework.response import Response
import os
# Import to send email
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives

from requests.exceptions import HTTPError

from django.contrib.auth import login
from rest_framework.exceptions import PermissionDenied
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from .models import MeetingRoom, MonthlyUsage, Invoice
from LocalUser.models import LocalUser, UserProfile, Company
from .serializers import MeetingRoomSerializer

from datetime import datetime, timezone, date, timedelta

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from rest_framework.exceptions import ValidationError

from django.core.files import File
from io import BytesIO

from . import my_payment
from . import makeinvoice, makeinvoice2

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from django.http import HttpResponse
from .utils import render_to_pdf

emailer = '''
    surendra
'''

class MeetingRoomAPIView(
                    viewsets.GenericViewSet,
                    viewsets.mixins.ListModelMixin,
                    # viewsets.mixins.UpdateModelMixin,
                    viewsets.mixins.RetrieveModelMixin,
                    viewsets.mixins.DestroyModelMixin):

    serializer_class = MeetingRoomSerializer
    queryset = MeetingRoom.objects.all()

    def get_queryset(self):
        now = datetime.now(timezone.utc)
        
        check_date = self.request.query_params.get('checkdate', None)

        if check_date:
            new_date = datetime.strptime(check_date, '%Y-%m-%d').date()
        else:
            new_date = now

        check_month = new_date.strftime("%m")
        check_year = new_date.strftime("%Y")
        check_day = new_date.strftime("%d")

        print(
            "CHECK_MONTH = " + str(check_month) + " " +
            "CHECK_YEAR = " + str(check_year) + " " +
            "CHECK_DAY = " + str(check_day) + " "
        )

        qs = MeetingRoom.objects.filter(
            start__year__gte=check_year,
            start__month__gte=check_month,
            start__day__gte=check_day,
            end__year__lte=check_year,
            end__month__lte=check_month,
            end__day__lte=check_day
        )
        print("QS = " + str(qs))
        if not qs:
            raise ValidationError("No bookings")
        return qs

    def perform_destroy(self, instance, from_admin=False):
        print("FROM ADMIN = " + str(from_admin))
        if self.request.user.is_admin:
            # self.perform_destroy(instance)
            super().perform_destroy(instance)
        elif from_admin:
            instance.delete(instance)
            # self.perform_destroy(instance)
        else:
            raise ValidationError("You cannot delete the booking")

    def create(self, request, *args, **kwargs):
        print("IN CREATE")
        print(request.data)
        # now = datetime.now(timezone.utc)
        start = request.data.get("start")
        end = request.data.get("end")
        print("RECEIVED START AND END AS "+ str(start) + " and " + str(end))
        if start == ":00" :
            raise ValidationError("The start date or time is incorrect")
        elif end == ":00":
            raise ValidationError("The end date or time is incorrect")
        new_start = self.convert_to_date(start)
        new_end = self.convert_to_date(end)

        now = datetime.now(timezone.utc)

        # qs = self.get_queryset()
        qs = my_queryset()
        # print("qs = " + str(qs))

        if not qs:
            print("NO QS!!")

        new_start2 = new_start.astimezone(timezone.utc)
        new_end2 = new_end.astimezone(timezone.utc)

       
        if new_start2 < now:
            raise ValidationError("Invalid time")
        if new_end2 < now:
            raise ValidationError("End time cannot be of the past")
        if new_end2 < new_start2:
            raise ValidationError("end time cannot be less than start time")

        for booked in qs:
          
            if new_start2 >= booked.start:
                if new_start2 <= booked.end:
                    raise ValidationError("From start Already booked")

            if new_end2 >= booked.start:
                if new_end2 <= booked.end:
                    raise ValidationError("From end Already booked ")

            if new_start2 <= booked.start:
                if new_end2 >= booked.start:
                    raise ValidationError("Again already end booked ")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking_month = new_start2.strftime("%m")
        booking_year = new_start2.strftime("%Y")
        booking_month_year = booking_month+"-"+booking_year
        print("THE BOOKING MONTH AND YEAR ARE = " + str(booking_month) + "-" + str(booking_year))

        print("request.data['company'] = " + str(request.data['company']))
        # print("The value is = " + (request.user.profile_id.company_name))

        try:
            print(str(request.user))
            myprofile_id = request.user.profile_id
        except:
            raise ValidationError("Cannot make the booking!!")

        if request.data['company'] != (request.user.profile_id.company_name.id):
            if request.user.is_admin:
                pass
            else:
                raise PermissionDenied("You cannot make bookings for other companies!")

        allotted = request.user.profile_id.company_name.allotted
        tdelta = new_end2 - new_start2
        minutes = tdelta.total_seconds() / 60

        print("THE ALLOTTED TIME IS : " + str(allotted))
        print("MINTUES = " + str(minutes))

        # GET COMPANY AND USER DETAILS
        company_name = request.user.profile_id.company_name
        company_address = request.user.profile_id.company_name.address
        gst = request.user.profile_id.company_name.gst
        hourly_rate = request.user.profile_id.company_name.hourly_rate
        email = request.user.profile_id.email
        user_first_name = request.user.profile_id.first_name


        try:
            monthly_query = MonthlyUsage.objects.get(
                company=company_name,
                month__iexact=booking_month_year
            )
        except MonthlyUsage.DoesNotExist:

            monthly_query = MonthlyUsage.objects.create(
                month=booking_month_year,
                company=company_name,
                used_this_month=0,
                used_till_date=0
            )
        current_invoice_number = Invoice.objects.last().invoice_number
        current_invoice_number = int(current_invoice_number)

        count = 0

        new_current_invoice_number = current_invoice_number + 1
        new_current_invoice_number2 = new_current_invoice_number
        while (new_current_invoice_number > 0):
            count = count + 1
            new_current_invoice_number = new_current_invoice_number // 10

        zeroes = "00000"
        new_zeroes = zeroes[count:]
        print("NEW ZEROES = " + new_zeroes)
        print("NEW INVOCE NUMBER BEFORE ADDING = " + str(new_current_invoice_number2))
        new_invoice_number = new_zeroes + str(new_current_invoice_number2)
        print("NEW INVOCE NUMBER AFTER ADDING = " + str(new_current_invoice_number2))

        if monthly_query.used_this_month > allotted:
            monthly_usage_object = update_monthly_usage_object(monthly_query, minutes)
            if monthly_usage_object:
                instance = serializer.save()
                print("serailizer data = " + str(serializer.data))



                try:
                    today_date = now.date()
                    due_date = today_date + timedelta(5)

                    print("TDAY DATE = " + str(today_date))
                    print("DUE DATE = " + str(due_date))

                    total_amount = (minutes/60) * hourly_rate

                    # Do payment
                    my_payment.do_payment(company_name.company_name, email, total_amount)

                    # raise ValueError("HEYEYYYYY WAITTTT")

                    res_attach = letscreate3(mydata={
                        "company": company_name,
                        "company_address": company_address,
                        "gst": gst,
                        "hourly_rate": hourly_rate,
                        "start": start,
                        "end": end,
                        "hours": minutes/60,
                        "total_amount": total_amount,
                        "invoice_number": new_invoice_number,
                        "id": instance,
                        "today_date": datetime.strftime(today_date, '%d %B, %Y'),
                        "due_date": datetime.strftime(due_date, '%d %B, %Y')
                    })

                    # The process of sending emails

                    subject = "Welcome to FootBuys!!"
                    message = "Hi " + user_first_name + ", \nThank you for registering with us. Glad to have you with us.\n\n\n\n\n\n\n\n This is an autogenerated email. Please do not try to revert back"
                    # message = emailer.replace(" ''' ", "")

                    from_mail = settings.EMAIL_HOST_USER
                    to_list = [email, settings.EMAIL_HOST_USER]

                    draft_mail = EmailMessage(subject, message, from_mail, to_list)
                    draft_mail.attach_file(res_attach)
                    check_mail = draft_mail.send()


                except ValueError:
                    # self.perform_destroy(serializer, from_admin=True)
                    print("DELTEDD!!!! VALUE ERROR!!")
                    instance.delete()
                    # serializer.delete()
            else:
                raise ValidationError("MONHTLY USAGE OBJECT IN PDF")
        else:
            avaialable_time = allotted - monthly_query.used_this_month
            print("AVAILABLE TIME = " + str(avaialable_time))

            if avaialable_time >= minutes:
                # monthly_usage_object = create_monthly_usage_object(booking_month_year, minutes, company_name)
                monthly_usage_object = update_monthly_usage_object(monthly_query, minutes)
                if monthly_usage_object:
                    serializer.save(allowed=True)
                else:
                    raise ValidationError("MONHTLY USAGE OBJECT ERROR NO PDF")
            else:
                print("IN INVOICE CREATION PHASE")

                today_date = now.date()
                due_date = today_date + timedelta(5)

                print("TDAY DATE = " + str(today_date))
                print("DUE DATE = " + str(due_date))


                monthly_usage_object = update_monthly_usage_object(monthly_query, minutes)
                if monthly_usage_object:
                    instance = serializer.save()
                    print("serailizer data = " + str(serializer.data))
                    try:
                        total_amount = ((minutes - avaialable_time) / 60) * hourly_rate

                        # Do payment
                        my_payment.do_payment(company_name.company_name, email, total_amount)

                        res_attach = letscreate3(mydata={
                            "company": company_name,
                            "start": start,
                            "end": end,
                            "hours": (minutes - avaialable_time)/60,
                            "total_amount": total_amount,
                            "invoice_number": new_invoice_number,
                            "id": instance,
                            "today_date": datetime.strftime(today_date, '%d %b, %Y'),
                            "due_date": datetime.strftime(due_date, '%d %b, %Y')
                        })

                        # The process of sending emails
                        subject = "Welcome to FootBuys!!"
                        message = "Hi " + user_first_name + ", \nThank you for registering with us. Glad to have you with us.\n\n\n\n\n\n\n\n This is an autogenerated email. Please do not try to revert back"
                        from_mail = settings.EMAIL_HOST_USER
                        to_list = [email, settings.EMAIL_HOST_USER]

                        draft_mail = EmailMessage(subject, message, from_mail, to_list)
                        draft_mail.attach_file(res_attach)
                        check_mail = draft_mail.send()
                        print(str(check_mail))

                    except ValueError:
                        # self.perform_destroy(serializer, from_admin=True)
                        print("DELTEDD!!!! VALUE ERROR!!")
                        instance.delete()
                        # serializer.delete()
                else:
                    raise ValidationError("MONHTLY USAGE OBJECT IN PDF")


                # monthly_usage_object = create_monthly_usage_object(booking_month_year, minutes, company_name)

                # raise ValidationError("You will have to pay first for the booking")
            # serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def convert_to_date(self, init_date):
        # datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        return datetime.strptime(init_date, '%Y-%m-%d %H:%M:%S')




def get_profile_id(user_id):
    qs = LocalUser.objects.get(id=user_id)
    profile_id = qs.profile_id
    return profile_id


def get_company_name(profile_id):
    qs = UserProfile.objects.get(id=profile_id.id)
    return qs.company_name


def my_queryset():
    now = datetime.now(timezone.utc)

    new_date = now

    check_month = new_date.strftime("%m")
    check_year = new_date.strftime("%Y")
    check_day = new_date.strftime("%d")

    qs = MeetingRoom.objects.filter(
        start__year__gte=check_year,
        start__month__gte=check_month,
        start__day__gte=check_day,
        end__year__lte=check_year,
        end__month__lte=check_month,
        end__day__lte=check_day
    )

    return qs


def create_monthly_usage_object(booking_month_year, minutes, company_name):
    try:
        monthly_query = MonthlyUsage.objects.get(
            company=company_name,
            month__iexact=booking_month_year
        )
        if monthly_query:
            print("MONTHLY QUERY = " + str(monthly_query.used_this_month))
            monthly_query.used_this_month = monthly_query.used_this_month + minutes
            monthly_query.used_till_date = monthly_query.used_till_date + minutes
            monthly_query.save()
            print(" IN CREATE NOW MONTHLY QUERY = " + str(monthly_query.used_this_month))
            return True
    except MonthlyUsage.DoesNotExist:

        monthly_query2 = MonthlyUsage.objects.create(
            month=booking_month_year,
            company=company_name,
            used_this_month=minutes,
            used_till_date=minutes
        )
        if monthly_query2:
            print("now created")
            return True
        else:
            return False


def update_monthly_usage_object(monthly_usage_object, minutes):
    monthly_usage_object.used_this_month = monthly_usage_object.used_this_month + minutes
    monthly_usage_object.used_till_date = monthly_usage_object.used_till_date + minutes
    monthly_usage_object.save()
    print(" IN UPDATE NOW MONTHLY QUERY = " + str(monthly_usage_object.used_this_month))
    return True


class MeetingRoomTest(viewsets.GenericViewSet,
                    viewsets.mixins.ListModelMixin,
                    # viewsets.mixins.UpdateModelMixin,
                    viewsets.mixins.RetrieveModelMixin,
                    viewsets.mixins.DestroyModelMixin):
    serializer_class = MeetingRoomSerializer
    queryset = MeetingRoom.objects.all()

    def get_queryset(self):



        makeinvoice2.letscreate2(self.request)

        now = datetime.now(timezone.utc)
        # ?checkdate=2020-04-10 is passed in url at the end
        check_date = self.request.query_params.get('checkdate', None)

        if check_date:
            new_date = datetime.strptime(check_date, '%Y-%m-%d').date()
        else:
            new_date = now

        check_month = new_date.strftime("%m")
        check_year = new_date.strftime("%Y")
        check_day = new_date.strftime("%d")

        qs = MeetingRoom.objects.filter(
            start__year__gte=check_year,
            start__month__gte=check_month,
            start__day__gte=check_day,
            end__year__lte=check_year,
            end__month__lte=check_month,
            end__day__lte=check_day
        )
        if not qs:
            raise ValidationError("No bookings")
        return qs


def letscreate3(mydata):
    if mydata:
        data = mydata
    else:
        data = {
            'today': datetime.now(timezone.utc),
            'amount': 39.99,
            'customer_name': 'Cooper Mann',
            'order_id': 1233434,
        }
    pdf = render_to_pdf('template.html', data)
  

    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "MyInvoice_%s.pdf" % ("125")
        content = "attachment; filename='%s'" % (filename)
        response['Content-Length'] = len(response.content)
        print("AFTER DOWNLOAD")
       

        response['Content-Disposition'] = content
        last_meeting_roo = MeetingRoom.objects.last()

        new_qs = Invoice(
            invoice_number=data['invoice_number'],
            meeting_room=data['id'],
        )

        where = new_qs.invoice_file.save(filename, File(BytesIO(response.content)))
        # new_qs.save()
        print("WHERE = " + str(where))
        my_new_file_obj = (filename, File(BytesIO(response.content)))
        # return my_new_file_obj

        print("NEW QS = " + str(new_qs))
        for key, value in response.items():
            print("KEY=" + str(key))
            print("VALUE = " + str(value))
            print("\n")
        # print(*response)
        pdf.close()
        # response.close()
        # return response
        # return my_new_file_obj
        return str(new_qs.invoice_file.url)
    return HttpResponse("Not found")
    print("OUTSIDE IF PDF")


def sending_email(request):

    to_list = ["planner@gmail.com",]


    print(str(settings.DEFAULT_FROM_EMAIL))
    eamil_message = EmailMultiAlternatives(subject="new  linik", body=emailer, from_email="Planner<surendr@gmail.com>", to=to_list)
    eamil_message.content_subtype = 'html'
    eamil_message.send()
  
