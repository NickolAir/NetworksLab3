import datetime as dt
import requests

BASE_URL1 = "https://graphhopper.com/api/1/geocode"
BASE_URL2 = "http://api.openweathermap.org/data/2.5/weather?"

API_KEY_WEATHER = open('api_key_weather', 'r').read()
API_KEY_LOCATIONS = open('api_key_locations', 'r').read()

CITY = input()

url1 = BASE_URL1 + "?key=" + API_KEY_LOCATIONS + "&q=" + CITY + "&limit=" + "10"

# Выполняем запрос
response = requests.get(url1)

# Проверяем успешность запроса
if response.status_code == 200:
    data = response.json()
    if 'hits' in data:
        for hit in data['hits']:
            print(f'Место: {hit["name"]}, Координаты: ({hit["point"]["lat"]}, {hit["point"]["lng"]})')
    else:
        print('Результаты не найдены.')
else:
    print(f'Ошибка при выполнении запроса: {response.status_code}')

def KelvinToCelsius(kelvin):
    celsius = kelvin - 273.15
    fahrenheit = celsius * (9 / 5) + 32
    return celsius, fahrenheit

url2 = BASE_URL2 + "appid=" + API_KEY_WEATHER + "&q=" + CITY
response = requests.get(url2).json()

temp_kelvin = response['main']['temp']
temp_celsius, temp_fahrenheit = KelvinToCelsius(temp_kelvin)
feels_like_kelvin = response['main']['feels_like']
feels_like_celsius, feels_like_fahrenheit = KelvinToCelsius(feels_like_kelvin)
humidity = response['main']['humidity']
wind_speed = response['wind']['speed']
description = response['weather'][0]['description']
sunrise_time = dt.datetime.utcfromtimestamp(response['sys']['sunrise'] + response['timezone'])
sunset_time = dt.datetime.utcfromtimestamp(response['sys']['sunset'] + response['timezone'])

print()
print(f"Temperature in {CITY}: {temp_celsius:.2f}°C or {temp_fahrenheit}°F")
print(f"Temperature in {CITY} feels like: {feels_like_celsius:.2f}°C or {feels_like_fahrenheit:.2f}F")
print(f"Humidity in {CITY}: {humidity}%")
print(f"Wind Speed in {CITY}: {wind_speed}m/s")
print(f"General Weather in {CITY}: {description}")
print(f"Sun rises in {CITY} at {sunrise_time} local time.")
print(f"Sun sets in {CITY} at {sunset_time} local time.")
