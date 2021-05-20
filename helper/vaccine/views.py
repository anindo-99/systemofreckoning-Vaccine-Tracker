from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
from django.shortcuts import render, HttpResponse
import requests
import json
import time

from datetime import datetime, timedelta
import ast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.conf import settings
from django.core.mail import send_mail

from django.contrib import messages
from vaccine.models import VaccineSlot


# Email settings

from django.conf import settings
from django.core.mail import send_mail


# Create your views here.
@login_required(login_url='login')
def vaccineHome(request):
    return render(request, 'vaccine/vaccine_home.html')


def handleVaccine(request):
    # Write your STATE here!

    STATE_ID = 0
    # Write your DISTRICT here!
    DISTRICT_ID = 0
    # Setting AGE = 45 here in order to show the live notification demo
    AGE = 45  # Write the minimum age group for which you wanna get notified!
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    }
    STATE_ID_ENDPOINT = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
    DISTRICT_ID_ENDPOINT = "https://cdn-api.co-vin.in/api/v2/admin/location/districts"
    ENDPOINT = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
    todays_date = datetime.now()
    DATE = f"{todays_date.day}-{todays_date.month}-{todays_date.year}"

    response = requests.get(f"{STATE_ID_ENDPOINT}", headers=headers)
    states = response.json()["states"]

    if request.method == 'POST':
        STATE = request.POST['state_name']
        DISTRICT = request.POST['district_name']
        email = request.POST['email']
        AGE = request.POST['age']

        if len(STATE) < 2 or len(DISTRICT) < 2 or len(email) < 4 or isinstance(int(AGE), int) == False:
            messages.error(request, "Please fill up the form correctly!")
            return redirect('vaccine')

        else:

            # print(states)
            for state in states:

                if state["state_name"] == STATE:
                    STATE_ID = state["state_id"]
                    print(STATE_ID)
                    break

            if STATE_ID == 0:
                messages.error(request, f"There is no state named {STATE}")
                # print(f"There is no state named {STATE}")
                return redirect('vaccine')

            response = requests.get(
                f"{DISTRICT_ID_ENDPOINT}/{STATE_ID}", headers=headers)
            districts = response.json()["districts"]

            for district in districts:
                if district["district_name"] == DISTRICT:
                    DISTRICT_ID = district["district_id"]
                    print(DISTRICT_ID)
                    break

            if DISTRICT_ID == 0:
                messages.error(
                    request, f"There is no district named {DISTRICT} in state {STATE}")
                # print(f"There is no district named {DISTRICT} in state {STATE}")
                # exit()
                return redirect('vaccine')
            vaccine_enquiry = VaccineSlot(
                state_name=STATE, district_name=DISTRICT, age=int(AGE), email_notification=email)
            vaccine_enquiry.save()
            messages.success(
                request, "Your request has been successfully sent.")
    if check_vaccine(ENDPOINT, DISTRICT_ID, DATE,
                     headers, int(AGE), vaccine_enquiry, request):
        messages.info(
            request, f"HURRY! Vaccine is availabe for age {AGE}.Details of the centers has been sent to your mail id.")
    else:
        messages.warning(
            request, f"\nNO Slot Available in the district {DISTRICT} for age {AGE} in this week as of {DATE}.")

    return redirect('vaccine')

# Function for getting center names


def check_vaccine(ENDPOINT, DISTRICT_ID, DATE, headers, AGE, vaccine_enquiry, request):
    response = requests.get(
        f"{ENDPOINT}?district_id={DISTRICT_ID}&date={DATE}", headers=headers)

    vaccine_slots = response.json()
    print(vaccine_slots)

    slot_available = False
    center_count = 1
    slots_data = ""
    for center in vaccine_slots["centers"]:
        # print(center)
        for session in center["sessions"]:
            if session["min_age_limit"] <= AGE and len(session["slots"]) > 0 and session["available_capacity"] > 0:
                slot_available = True
                slots_data += f"\n{center_count}) {str(center['name'])} on {str(session['date'])}\nOpening Time:{str(center['from'])}\tClosing time: {str(center['to'])}\nCENTER ADDRESS: {str(center['address'])}\nSTATE NAME: {str(center['state_name'])}\nDISTRICT NAME: {str(center['district_name'])}\nPINCODE: {str(center['pincode'])}\nVACCINE: {session['vaccine']}\nAVAILABLE CAPACITY: DOSE 1 = {str(session['available_capacity_dose1'])}\tDOSE 2 = {str(session['available_capacity_dose2'])}\nMinimum Age Limit: {str(session['min_age_limit'])}\nFee Type: {str(center['fee_type'])}\n------------------------------------------------------------------------------------------------------------------------------"
                center_count += 1
                # print(f"Center Name\t{center['name']}")
                # print(f"Slots available\t{session['slots']}")
                # print("-----------------------------------")
                break

    if slot_available:
        notification_data = f"   HURRY! Vaccine is availabe for age {AGE} at these centers: {slots_data}"

        print(notification_data)
        context = {'slots': slots_data}
        subject = 'welcome to TASK world\'s Vaccine Notification '
        message = notification_data
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [vaccine_enquiry.email_notification]
        send_mail(subject, message, email_from, recipient_list)
        return True
    # notify.send(notification_data)
    else:

        notification_data = f"\nNO Slot Available in the district {vaccine_enquiry.district_name} for age {AGE} in this week as of {DATE}."
        print(notification_data)
        subject = 'welcome to TASK world\'s Vaccine Notification '
        message = notification_data
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [vaccine_enquiry.email_notification]
        send_mail(subject, message, email_from, recipient_list)
        return False

    # Registration mail

    # if __name__ == "__main__":
    # while True:
    # if check_vaccine():
    #     break
    # time.sleep(900)  # Check for vaccine availability every 15 mins

    # with open('vaccine/district_dict.txt') as f:
    #     data = f.read()
    #     districts = ast.literal_eval(data)
    #     f.close()
    # default_dist = 'bikaner'
    # district_name = request.GET.get('district', default_dist)
    # default_dist = district_name

    # district_code = districts[district_name.lower()]

    # for i in range(0, 1):
    #     date = datetime.today() + timedelta(days=i)
    #     date = date.strftime("%d-%m-%Y")

    # # pinCode = 110001
    #     URL = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={0}&date={1}'.format(
    #         district_code, date)
    # # This is chrome, you can set whatever browser you like
    #     headers = {
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    #     response = requests.get(URL, headers=headers)

    #     if response.ok:
    #         json_data = response.json()
    #         # json_data = json.loads(response.text)
    #         print(json_data)

    #     if len(json_data['centers']) == 0:
    #         print("No slots available")
    #     centers_list = {}
    #     key = 1
    #     for slots in json_data['centers']:
    #         print(
    #             '-----------------------------------------------------------------------------')
    #         center = {'center_id': str(
    #             slots['center_id']), 'Name': str(slots['name']), 'Address': str(slots['address']), 'State Name': str(slots['state_name']), 'District Name': str(slots['district_name']), 'Pincode': str(slots['pincode']), 'Opening Time': str(slots['from']), 'Closing Time': str(slots['to']), 'Fee Type': str(slots['fee_type']), }

    #         centers_list[key] = center
    #         key += 1

    #         print("\nCenter ID: "+str(slots['center_id']) + '\n'
    #               + "Name: "+str(slots['name']) + '\n'
    #               + "Address: "+str(slots['address']) + '\n'
    #               + "State Name: "+str(slots['state_name']) + '\n'
    #               + "District Name: "+str(slots['district_name']) + '\n'
    #               + "Pincode: "+str(slots['pincode']) + '\n'
    #               + "Opening time: "+str(slots['from']) + '\n'
    #               + "Closing Time: "+str(slots['to']) + '\n'
    #               + "fee type: "+str(slots['fee_type']))
    #         print(
    #             '-----------------------------------------------------------------------------')

    #         for info in slots['sessions']:
    #             print("session_id: "+str(info['session_id'])+'\n'
    #                   + "date: "+str(info['date'])+'\n'
    #                   + "available capacity: " +
    #                   str(info['available_capacity'])+'\n'
    #                   + "min age limit: "+str(info['min_age_limit'])+'\n'
    #                   + "vaccine: "+str(info['vaccine'])+'\n')
    #             print('Timings')
    #             for time in info['slots']:
    #                 print(time)
    #             print('......................................................')
    #     # print(resp_json)

    # # dist_id = 12
    # # url = 'https://cdn-api.co-vin.in/api/v2/admin/location/states'
    # # data = requests.get(url).json()
    # # print(data)

    # # payload = {'city': data['name'],
    # #            'weather': data['weather'][0]['main'],
    # #            'icon': data['weather'][0]['icon'],
    # #            'K_temperature': data['main']['temp'],
    # #            'C_temperature': round((data['main']['temp']-273), 2),
    # #            'pressure': data['main']['pressure'],
    # #            'humidity': data['main']['humidity'],
    # #            }
    # date_time = datetime.now()
    # # date_time = date_time.strftime('%m' '%d')
    # # print(date_time)

    # context = {'data': centers_list}
    # print(context)
    # return render(request, "vaccine/vaccine_home.html", context)
