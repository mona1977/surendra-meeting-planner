#Developer : SURENDRA 
#date : 2-Oct-2022
from django.shortcuts import render, HttpResponseRedirect
from .forms import MeetingRoomForm, ContactForm
from .models import MeetingRoom, MonthlyUsage
from django.contrib.auth import get_user_model
from LocalUser.models import UserProfile, Company, LocalUser
from datetime import datetime, timezone, date

from django.db.models.functions import TruncMonth
from django.db.models import Count


# Create your views here.
def meeting_room_add(request):
    User = get_user_model()
    form = MeetingRoomForm(request.POST or None)
    print(str(request.POST))
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month
    day = now.day

    # qs = month_view(year, month)
    qs = MeetingRoom.objects.filter(start__year__gte=year, start__month__gte=month, start__day__gte=day, start__year__lte=year, start__month__lte=month, start__day__lte=day)

    context = {"qs": qs, "form": form, "datenow": now}
    if form.is_valid():
        print(request.POST)
        company_name = LocalUser.objects.get(id=request.user.id)
        profile_id = get_profile_id(request.user.id)

        company_name = get_company_name(profile_id)

        start = str(form.cleaned_data['start_date']) + " " + str(form.cleaned_data['start_time'])
        end = str(form.cleaned_data['end_date']) + " " + str(form.cleaned_data['end_time'])

        now = datetime.now(timezone.utc)

        print("QS = " + str(qs))

        print("START BEFORE STRPTIME: "+start)
        print("END BEFOER STRPTIME: "+end)

        new_start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        new_end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')

        new_start2 = new_start.astimezone(timezone.utc)
        new_end2 = new_end.astimezone(timezone.utc)
        # new_now = datetime.timestamp()
        if new_start2 < now:
            raise ValueError("Invalid time")
        if new_end2 < now:
            raise ValueError("End time cannot be of the past")
        if new_end2 < new_start2:
            raise ValueError("end time cannot be less than start time")

        for booked in qs:
            if new_start2 >= booked.start:
                if new_start2 <= booked.end:
                    raise ValueError("From start Already booked")

            if new_end2 >= booked.start:
                if new_end2 <= booked.end:
                    raise ValueError("From end Already booked ")

            if new_start2 <= booked.start:
                if new_end2 >= booked.start:
                    raise ValueError("Again already end booked ")

        obj = MeetingRoom.objects.create(company=company_name, start=start, end=end)

        month_from_start = new_start.strftime('%B')
        year_from_start = new_start.year

        print("Year booked = "+str(year_from_start))
        print("Month booked = "+str(month_from_start))

        form = MeetingRoomForm()

        if obj:
            print(obj)

        context = {"qs": qs, "form": form}
        return HttpResponseRedirect("/meeting/add")

    return render(request, "form.html", context)


def get_profile_id(user_id):
    qs = LocalUser.objects.get(id=user_id)
    profile_id = qs.profile_id
    return profile_id


def get_company_name(profile_id):
    qs = UserProfile.objects.get(id=profile_id.id)
    return qs.company_name


def month_view(year, month):
    qs = MeetingRoom.objects.annotate(month=TruncMonth('start')).values('month')
    year = 2020
    month = 3
    qs2 = MeetingRoom.objects.filter(start__year__gte=year, start__month__gte=month, start__year__lte=year, start__month__lte=month)

    context = {"qs": qs2}
    return render(request, "form.html", context)


# LIST ONLY TODAY'S
def meeting_room_list(request):
    now = datetime.now(timezone.utc)

    now_month = now.strftime("%m")
    now_year = now.strftime("%Y")
    now_day = now.strftime("%d")
    year = 2020
    month = 4
    day = 19



    try:
        profile = request.user.profile_id
        print("PROFILE IS " + str(profile.id))
  
        print("COMPANY IS " + str(profile.company_name.company_name))


        qs = MeetingRoom.objects.filter(start__year__gte=now_year,
                                        start__month__gte=now_month,
                                        start__day__gte=now_day,
                                        end__year__lte=now_year,
                                        end__month__lte=now_month,
                                        end__day__lte=now_day
                                        )
        context = {"qs": qs}
    except:
        raise Exception("Please login")

    return render(request, "list.html", context)

