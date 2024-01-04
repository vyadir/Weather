# Librerias necesarias
import os
from twilio.rest import Client
import time
import requests
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from bs4 import BeautifulSoup
from dotenv import load_dotenv
# Cargo variables de entorno
load_dotenv()

class WeatherForecast:
    """Clase para obtener el pronóstico del clima a partir de la API WeatherAPI."""
    def __init__(self, query, api_key):
        self.query = query
        self.api_key = api_key
        self.url_clima = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={query}&days=1&aqi=no&alerts=no'
        self.response = self.get_weather_data()

    def get_weather_data(self):
        """Obtiene datos meteorológicos de la API y devuelve la respuesta en formato JSON."""
        try:
            response = requests.get(self.url_clima).json()
            return response
        except requests.RequestException as e:
            print(f"Error al obtener datos meteorológicos: {e}")
            return None

    def get_forecast(self, i):
        """Obtiene los datos del pronóstico para una hora específica."""
        hour_data = self.response['forecast']['forecastday'][0]['hour'][i]
        fecha = hour_data['time'].split()[0]
        hora = int(hour_data['time'].split()[1].split(':')[0])
        condicion = hour_data['condition']['text']
        temp_c = float(hour_data['temp_c'])
        will_it_rain = hour_data['will_it_rain']
        chance_of_rain = hour_data['chance_of_rain']
        return fecha, hora, condicion, temp_c, will_it_rain, chance_of_rain

    def generate_forecast_df(self):
        """Genera un DataFrame a partir de los datos del pronóstico."""
        datos = [self.get_forecast(i) for i in range(len(self.response['forecast']['forecastday'][0]['hour']))]
        col = ['Fecha', 'Hora', 'Condicion', 'Temperatura', 'Lluvia', 'prob_lluvia']
        df = pd.DataFrame(datos, columns=col)
        df = df.sort_values(by='Hora', ascending=True)
        return df

    def filter_rain_hours(self, df):
        """Filtra las horas de lluvia del DataFrame."""
        df_rain = df[(df['Lluvia'] == 1) & (df['Hora'] > 6) & (df['Hora'] < 22)]
        return df_rain[['Hora', 'Condicion']]

class TwilioMessageSender:
    """Clase para enviar mensajes a través de Twilio."""
    def __init__(self, account_sid, auth_token, phone_number):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.phone_number = phone_number
        self.client = Client(account_sid, auth_token)

    def send_message(self, mensaje):
        """Envía un mensaje utilizando la API de Twilio."""
        try:
            message = self.client.messages.create(
                body=mensaje,
                from_=self.phone_number,
                to=os.getenv('TO')
            )
            print('Mensaje Enviado ' + message.sid)
        except Exception as e:
            print(f"Error al enviar el mensaje a través de Twilio: {e}")

def main():
    query = 'San José, San Pedro, Montes de Oca'
    api_key = os.getenv('API_KEY_WAPI')
    twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN') 
    phone_number = os.getenv('PHONE_NUMBER') 
    weather_forecast = WeatherForecast(query, api_key)
    df_forecast = weather_forecast.generate_forecast_df()
    df_rain = weather_forecast.filter_rain_hours(df_forecast)
    mensaje = f'\n¡Hola!\n\n\nEl pronóstico de lluvia hoy {df_forecast["Fecha"].iloc[0]} en {query} es:\n\n\n{str(df_rain)}'
    time.sleep(2)
    twilio_sender = TwilioMessageSender(twilio_account_sid, twilio_auth_token, phone_number)
    twilio_sender.send_message(mensaje)
# Inicio de aplicacion
if __name__ == "__main__":
    main()
