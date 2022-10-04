#Developer : SURENDRA 
#date : 2-Oct-2022
from .models import MeetingRoom, MonthlyUsage, Invoice
from LocalUser.models import LocalUser, UserProfile, Company

def create(self, request, *args, **kwargs):
    allotted = request.user.profile_id.company_name.allotted
    tdelta = new_end2 - new_start2
    minutes = tdelta.total_seconds() / 60

    print("THE ALLOTTED TIME IS : " + str(allotted))
    print("MINTUES = " + str(minutes))

    if allotted >= minutes:
        try:
            monthly_query = MonthlyUsage.objects.get(
                    company=request.user.profile_id.company_name,
                    used_this_month__iexact=booking_month_year
                )
            if monthly_query:
                print("MONTHLY QUERY = " + str(monthly_query.used_this_month))
                monthly_query.used_this_month = monthly_query.used_this_month + minutes
                monthly_query.used_till_date = monthly_query.used_till_date + minutes
                monthly_query.save()
                print("NOW MONTHLY QUERY = " + str(monthly_query.used_this_month))

            except MonthlyUsage.DoesNotExist:
                monthly_query2 = MonthlyUsage.objects.create(
                    month=booking_month_year,
                    company=request.user.profile_id.company_name,
                    used_this_month=minutes,
                    used_till_date=minutes
                )
                print("now created")
            serializer.save()
    else:
        letscreate3(mydata={
                "company": request.user.profile_id.company_name,
                "start": start,
                "end": end
            })



def check_monthly_query(company_name, booking_month_year):
    try:
        monthly_query = MonthlyUsage.objects.get(
            company=company_name,
            used_this_month__iexact=booking_month_year
        )
        add_monthly_query(monthly_query, minutes)
    except MonthlyUsage.DoesNotExist:
        monthly_query2 = MonthlyUsage.objects.create(
            month=booking_month_year,
            company=request.user.profile_id.company_name,
            used_this_month=minutes,
            used_till_date=minutes
        )

def add_monthly_query(monthly_query, minutes):
    print("MONTHLY QUERY = " + str(monthly_query.used_this_month))
    monthly_query.used_this_month = monthly_query.used_this_month + minutes
    monthly_query.used_till_date = monthly_query.used_till_date + minutes
    monthly_query.save()
    print("NOW MONTHLY QUERY = " + str(monthly_query.used_this_month))