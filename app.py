'''
Файл основы Flask приложения. Обрабатывает методы GET и POST к сервису
'''

from flask import Flask, render_template, request
import json
import asyncio
import threading
from dash import Dash, html

from config import api_key
from functs import get_weather_for_multiple_points, create_weather_charts
from bot import main


app = Flask(__name__) # Инициализируем Flask приложение

dash_app = Dash(__name__, server=app, url_base_pathname='/dash/') # Инициализируем Dash приложение на сервере app (Flask)



dash_app.layout = html.Div([                   
    html.H2("Dash Weather Forecast Viewer"),
    html.Div(id='weather-charts')
])

# Основна функция для работы Flask приложения
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        points = request.form.getlist('points')  # Получаем список точек
        forecast_days = 3 if request.form['forecast'] == '3_days' else 5  # Определяем количество дней

        try:
            weather_data = get_weather_for_multiple_points(points, forecast_days, api_key)
            dash_app.layout = create_weather_charts(weather_data)  # Передача данных в Dash layout
            return render_template('index.html', dash_url='/dash/')  # Ссылка на Dash
        
        # Обработка ошибок. Стоит отметить, что в функциях из файла functs.py большинство ошибок уже обработаны.
        except json.JSONDecodeError:  # Обработка ошибок декодирования JSON
            return render_template('index.html', error="Ошибка обработки данных о погоде.")
        
        except Exception as e:  # Общая обработка ошибок
            return render_template('index.html', error=f"Ошибка: {e}. Данные недоступны")

    return render_template('index.html')

def run_flask():
    app.run(debug=False)

if __name__ == "__main__":
    try:
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.start()
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')
    # app.run(debug=False)
