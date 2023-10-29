import asyncio
import httpx
import datetime as dt

BASE_URL1 = "https://graphhopper.com/api/1/geocode"
BASE_URL2 = "http://api.openweathermap.org/data/2.5/weather"
BASE_URL3 = "https://api.yelp.com/v3/businesses/search"

API_KEY_WEATHER = open('api_key_weather', 'r').read()
API_KEY_LOCATIONS = open('api_key_locations', 'r').read()
API_KEY_PLACES = open('api_key_nearly_places', 'r').read()


async def fetch_geocoding_data(city):
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL1}?key={API_KEY_LOCATIONS}&q={city}&limit=10"
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'hits' in data:
                locations = []
                for hit in data['hits']:
                    locations.append({
                        "Место": hit["name"],
                        "Координаты": f"({hit['point']['lat']}, {hit['point']['lng']})"
                    })
                return locations
    return []


async def fetch_weather_data(city):
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL2}?appid={API_KEY_WEATHER}&q={city}"
        response = await client.get(url)
        if 'main' in response.json():
            temp_kelvin = response.json()['main']['temp']
            temp_celsius, temp_fahrenheit = KelvinToCelsius(temp_kelvin)
            feels_like_kelvin = response.json()['main']['feels_like']
            feels_like_celsius, feels_like_fahrenheit = KelvinToCelsius(feels_like_kelvin)
            humidity = response.json()['main']['humidity']
            wind_speed = response.json()['wind']['speed']
            description = response.json()['weather'][0]['description']
            sunrise_time = dt.datetime.utcfromtimestamp(response.json()['sys']['sunrise'] + response.json()['timezone'])
            sunset_time = dt.datetime.utcfromtimestamp(response.json()['sys']['sunset'] + response.json()['timezone'])

            return {
                "Temperature": f"{temp_celsius:.2f}°C or {temp_fahrenheit}°F",
                "Temperature feels like": f"{feels_like_celsius:.2f}°C or {feels_like_fahrenheit:.2f}°F",
                "Humidity": f"{humidity}%",
                "Wind Speed": f"{wind_speed}m/s",
                "General Weather": description,
                "Sunrise Time": f"{sunrise_time} local time",
                "Sunset Time": f"{sunset_time} local time"
            }
    return []


def KelvinToCelsius(kelvin):
    celsius = kelvin - 273.15
    fahrenheit = celsius * (9 / 5) + 32
    return celsius, fahrenheit


async def search_restaurants(city, term="restaurant", limit=10):
    async with httpx.AsyncClient() as client:
        base_url = BASE_URL3
        headers = {
            "Authorization": f"Bearer {API_KEY_PLACES}"
        }
        params = {
            "location": city,
            "term": term,
            "limit": limit
        }
        response = await client.get(base_url, headers=headers, params=params)
        data = response.json()
        if "businesses" in data:
            restaurants = []
            for i, business in enumerate(data["businesses"]):
                restaurants.append({
                    "Название": business['name'],
                    "Адрес": business['location']['address1'],
                    "Рейтинг": business['rating'],
                    "Отзывов": business['review_count']
                })
            return restaurants
    return []


async def main():
    city = input("Введите город: ")
    geocoding_data = await fetch_geocoding_data(city)

    if geocoding_data:
        print("Найдены следующие местоположения:")
        for i, location in enumerate(geocoding_data):
            print(f"{i + 1}. {location['Место']}: {location['Координаты']}")

        choice = int(input("Выберите номер местоположения для получения дополнительной информации: ")) - 1
        selected_location = geocoding_data[choice]["Место"]

        print()
        weather_data = await fetch_weather_data(selected_location)
        if weather_data:
            print("Погода в выбранном местоположении:")
            for key, value in weather_data.items():
                print(f"{key}: {value}")
        else:
            print(f"Информация о погоде для {selected_location} не найдена.")

        print()
        restaurants = await search_restaurants(selected_location)
        if restaurants:
            print("Рестораны в выбранном местоположении:")
            for i, restaurant in enumerate(restaurants):
                print(f"{i + 1}. {restaurant['Название']}")
                print(f"   Адрес: {restaurant['Адрес']}")
                print(f"   Рейтинг: {restaurant['Рейтинг']}")
                print(f"   Отзывов: {restaurant['Отзывов']}")
        else:
            print(f"Рестораны в {selected_location} не найдены.")
    else:
        print("Местоположения не найдены.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
