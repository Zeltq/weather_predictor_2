"""Файл с основными функциями для нашего приложения."""
import requests
import json
import plotly.graph_objects as go
from dash import dcc, html


async def split_cities(text: str):
    """Возвращает список из городов."""
    return text.split(', ')


async def get_weather_description_by_cities(cities, api_key, days):
    """Функция принимает список из названия городов и возвращает словарь.

    где ключ - название города, а значение - это текст,
    который нужно отправить пользователю
    """
    answer = {}

    for el in cities:
        try:
            location_key = get_location_key_by_city(el, api_key=api_key)
        except Exception as e:
            return e

        weather_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}"
        params = {
            'apikey': api_key,
            'language': 'ru-RU',
            'details': 'true',
            'metric': 'true'
        }

        weather_response = requests.get(weather_url, params=params)

        if weather_response.status_code != 200:
            print(weather_response.json())
            raise Exception(f"Ошибка при получении данных о погоде: {weather_response.json()['Message']}")

        weather_data = json.loads(json.dumps(weather_response.json()))  # Преобразуем в json для удобной дальнейшей работы

        try:
            text_to_user = f'Погода в городе {el} на {days} дней вперёд:\n\n'

            day_counter = 1
            for day in weather_data['DailyForecasts'][:days]:
                max_t = day['Temperature']['Maximum']['Value']
                min_t = day['Temperature']['Minimum']['Value']
                probability = day['Day']['PrecipitationProbability']
                wind_speed = day['Day']['Wind']['Speed']['Value']
                text_to_user = text_to_user + f'День: {day_counter}\nТемпература от {min_t} °C до {max_t} °C.\n\Вероятность осадков: {probability} %.\nСкорость ветра: {wind_speed}.\n\n'
                day_counter += 1
            answer[el] = text_to_user

        except KeyError:
            raise Exception("Ошибка при попытке извлечь данные о погоде.")
    return answer


def get_weather_for_multiple_points(points, days, api_key):
    """Получает данные о погоде по каждой введённой точке (Названию города) на {days} дней вперёд."""
    weather_data = {}

    for point in points:
        location_key = get_location_key_by_city(point, api_key)
        forecast = get_forecast_by_days(location_key, api_key, days)
        weather_data[point] = json.loads(str(forecast))

    return weather_data


def create_weather_charts(weather_data):
    """Создаёт графики с помощью Dash и Plotly."""
    layout = html.Div([
        html.H1("Погода по дням в выбранных городах"),
        dcc.Tabs(id='city-tabs', children=[
            dcc.Tab(label=city, children=[
                dcc.Graph(
                    id=f'weather-graph-{city}',
                    figure=go.Figure([
                        go.Scatter(x=[f"Day {i+1}" for i in range(len(data))], y=[day[1] for day in data], mode='lines+markers', name='Min Temperature (°C)'),
                        go.Scatter(x=[f"Day {i+1}" for i in range(len(data))], y=[day[0] for day in data], mode='lines+markers', name='Max Temperature (°C)'),
                        go.Bar(x=[f"Day {i+1}" for i in range(len(data))], y=[day[2] for day in data], name='Precipitation Chance (%)'),
                        go.Scatter(x=[f"Day {i+1}" for i in range(len(data))], y=[day[3] for day in data], mode='lines+markers', name='Wind Speed (km/h)')
                    ])
                )
            ]) for city, data in weather_data.items()
        ])
    ])
    return layout


def get_location_key_by_city(city: str, api_key: str) -> str:
    """Эта функцию принимает название города и возвращает его location_key."""
    location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={api_key}&q={city}"
    location_response = requests.get(location_url)

    if location_response.status_code != 200:
        raise Exception(f"Ошибка при получении ключа местоположения: {location_response.json()['Message']}")

    location_data = location_response.json()
    if not location_data:
        raise Exception(f"Город '{city}' не найден")

    location_key = location_data[0]['Key']
    return str(location_key)


def get_forecast_by_days(location_key, api_key, num_days):
    """Запрашивает прогноз погоды на заданное количество дней."""
    weather_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}"
    params = {
        'apikey': api_key,
        'language': 'ru-RU',
        'details': 'true',
        'metric': 'true'
    }

    weather_response = requests.get(weather_url, params=params)

    if weather_response.status_code != 200:
        print(weather_response.json())
        raise Exception(f"Ошибка при получении данных о погоде: {weather_response.json()['Message']}")

    weather_data = json.loads(json.dumps(weather_response.json()))  # Преобразуем в json для удобной дальнейшей работы
    try:
        forecasts = []
        for day in weather_data['DailyForecasts'][:num_days]:
            forecast = [day['Temperature']['Maximum']['Value'],
                        day['Temperature']['Minimum']['Value'],
                        day['Day']['PrecipitationProbability'],
                        day['Day']['Wind']['Speed']['Value'],
                        ]
            forecasts.append(forecast)

    except KeyError:
        raise Exception("Ошибка при попытке извлечь данные о погоде.")
    return forecasts


if __name__ == "__main__":
    print('Запущено')
