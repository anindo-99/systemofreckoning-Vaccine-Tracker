from django.shortcuts import render, redirect
from django.contrib import messages
# Create your views here.
from django.shortcuts import render, HttpResponse
import requests
from datetime import datetime
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


@login_required(login_url='login')
def weatherHome(request):
    city_name = request.GET.get('cityname')
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid=83b215f96295e9bc0c7e4f34837325d4'
    data = requests.get(url, city_name).json()
    print(data)
    if data['cod'] == '404':
        messages.error(request, f"There is no City named {city_name}")
        return redirect('weather')
    if data['cod'] == '400':
        messages.error(request, f"We have nothing to show")
        return redirect('weather')

    payload = {'city': data['name'],
               'weather': data['weather'][0]['main'],
               'icon': data['weather'][0]['icon'],
               'K_temperature': data['main']['temp'],
               'F_temperature': round((data['main']['temp']-273.15)*1.8+32, 2),
               'C_temperature': round((data['main']['temp']-273.15), 2),
               'pressure': data['main']['pressure'],
               'humidity': data['main']['humidity'],
               'description': data['weather'][0]['description'],
               'maxtemp_C': round((data['main']['temp_max']-273.15), 2),
               'mintemp_C': round((data['main']['temp_min']-273.15), 2),
               'maxtemp_F': round((data['main']['temp_max']-273.15)*1.8+32, 2),
               'mintemp_F': round((data['main']['temp_min']-273.15)*1.8+32, 2),
               'wind': data['wind']['speed'],
               'longitude': data['coord']['lon'],
               'latitude': data['coord']['lat'],
               }
    date_time = datetime.now()
    # date_time = date_time.strftime('%m' '%d')
    print(date_time)
    context = {'data': payload, 'date': date_time}

    return render(request, "weather/weather_home.html", context)
