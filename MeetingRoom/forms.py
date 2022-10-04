#Developer : SURENDRA 
#date : 2-Oct-2022
from django import forms
from datetime import datetime


class ContactForm(forms.Form):
    full_name = forms.CharField()
    email = forms.EmailField()
    content = forms.CharField(widget=forms.Textarea)


class MyDateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"


class MeetingRoomForm(forms.Form):
    # company = models.TextField(max_length=200)

    # start = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': "datetime-local"}))
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': "date"}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': "time"}))

    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': "date"}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': "time"}))
    # end = forms.DateTimeField(widget=MyDateTimeInput)
    # newend = forms.DateTimeInput(widget=DateTimeInput(attrs={'type': 'datetime-local'}))
    # allowed = models.BooleanField(default=False)

    def clean_start(self):
        start = self.cleaned_data.get("start")
        print("Start is " + str(start))
        newstart = start.sub('T', ' ', start)
        return newstart
