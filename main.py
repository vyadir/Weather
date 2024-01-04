# Importación de bibliotecas y módulos necesarios
import os
from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, PHONE_NUMBER, API_KEY_WAPI, TO
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from utils import request_wapi, get_forecast, create_df, send_message, get_date

# Definición de la clase WeatherApp que encapsula la funcionalidad de la aplicación del clima
class WeatherApp:
    def __init__(self, api_key, query, to_phone):
        """
        Inicializa la instancia de WeatherApp con la clave de la API, la consulta de ubicación y el número de teléfono del destinatario.
        Args:
        - api_key (str): Clave de la API para acceder a los datos meteorológicos.
        - query (str): Ubicación para la consulta meteorológica.
        - to_phone (str): Número de teléfono del destinatario para enviar mensajes.
        """
        self.api_key = api_key
        self.query = query
        self.to_phone = to_phone

    def run(self):
        """
        Método principal que ejecuta la aplicación del clima.
        """
        # Obtiene la respuesta de la consulta meteorológica
        response = self.request_weather_data()
        # Obtiene los datos de pronóstico meteorológico
        datos = self.get_forecast_data(response)
        # Crea un DataFrame con los datos de pronóstico meteorológico
        df_rain = self.create_dataframe(datos)
        # Envía un mensaje con los datos meteorológicos
        message_id = self.send_weather_message(df_rain)
        print('Mensaje Enviado con exito ' + message_id)

    def request_weather_data(self):
        """
        Realiza una solicitud para obtener datos meteorológicos y devuelve la respuesta.
        Returns:
        - response (object): Objeto de respuesta de la solicitud meteorológica.
        """
        return request_wapi(self.api_key, self.query)

    def get_forecast_data(self, response):
        """
        Obtiene los datos de pronóstico meteorológico para las próximas 24 horas.
        Args:
        - response (object): Objeto de respuesta de la solicitud meteorológica.
        Returns:
        - datos (list): Lista de datos de pronóstico meteorológico.
        """
        datos = []
        for i in tqdm(range(24), colour='green'):
            datos.append(get_forecast(response, i))
        return datos

    def create_dataframe(self, datos):
        """
        Crea un DataFrame a partir de los datos de pronóstico meteorológico.
        Args:
        - datos (list): Lista de datos de pronóstico meteorológico.
        Returns:
        - df_rain (DataFrame): DataFrame creado a partir de los datos.
        """
        return create_df(datos)

    def send_weather_message(self, df_rain):
        """
        Envía un mensaje con los datos meteorológicos al destinatario.
        Args:
        - df_rain (DataFrame): DataFrame con datos meteorológicos.
        Returns:
        - message_id (str): ID del mensaje enviado.
        """
        input_date = get_date()
        return send_message(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, input_date, df_rain, self.query, self.to_phone)

# Bloque principal que se ejecuta solo cuando el script se ejecuta directamente
if __name__ == "__main__":
    # Configuración de parámetros para la aplicación del clima
    query_location = 'San Jose, Costa Rica'
    api_key_wapi = API_KEY_WAPI
    recipient_phone_number = TO
    # Creación de una instancia de la clase WeatherApp y ejecución de la aplicación
    weather_app = WeatherApp(api_key_wapi, query_location, recipient_phone_number)
    weather_app.run()
