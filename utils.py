# Importación de bibliotecas y módulos necesarios
import pandas as pd
from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, PHONE_NUMBER, API_KEY_WAPI
from datetime import datetime
import requests
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

# Función para obtener la fecha actual en el formato "YYYY-MM-DD"
def get_date():
    """
    Obtiene la fecha actual en el formato "YYYY-MM-DD".
    Returns:
    - input_date (str): Fecha actual en el formato "YYYY-MM-DD".
    """
    input_date = datetime.now()
    input_date = input_date.strftime("%Y-%m-%d")
    return input_date

# Función para realizar la solicitud a la API del clima y obtener la respuesta
def request_wapi(api_key, query):
    """
    Realiza una solicitud a la API del clima y devuelve la respuesta.
    Args:
    - api_key (str): Clave de la API para acceder a los datos meteorológicos.
    - query (str): Ubicación para la consulta meteorológica.
    Returns:
    - response (object): Objeto de respuesta de la solicitud meteorológica.
    """
    url_clima = 'http://api.weatherapi.com/v1/forecast.json?key='+api_key+'&q='+query+'&days=1&aqi=no&alerts=no'
    try:
        response = requests.get(url_clima).json()
    except Exception as e:
        print(e)
    return response

# Función para obtener datos específicos del pronóstico meteorológico
def get_forecast(response, i):
    """
    Obtiene datos específicos del pronóstico meteorológico para una hora específica.
    Args:
    - response (object): Objeto de respuesta de la solicitud meteorológica.
    - i (int): Índice de la hora en el pronóstico.
    Returns:
    - Tuple: Información de fecha, hora, condición, temperatura, si lloverá, probabilidad de lluvia.
    """
    fecha = response['forecast']['forecastday'][0]['hour'][i]['time'].split()[0]
    hora = int(response['forecast']['forecastday'][0]['hour'][i]['time'].split()[1].split(':')[0])
    condicion = response['forecast']['forecastday'][0]['hour'][i]['condition']['text']
    tempe = response['forecast']['forecastday'][0]['hour'][i]['temp_c']
    rain = response['forecast']['forecastday'][0]['hour'][i]['will_it_rain']
    prob_rain = response['forecast']['forecastday'][0]['hour'][i]['chance_of_rain']
    return fecha, hora, condicion, tempe, rain, prob_rain

# Función para crear un DataFrame a partir de los datos del pronóstico meteorológico
def create_df(data):
    """
    Crea un DataFrame a partir de los datos del pronóstico meteorológico.
    Args:
    - data (list): Lista de datos del pronóstico meteorológico.
    Returns:
    - df_rain (DataFrame): DataFrame creado a partir de los datos.
    """
    col = ['Fecha', 'Hora', 'Condicion', 'Temperatura', 'Lluvia', 'prob_lluvia']
    df = pd.DataFrame(data, columns=col)
    df = df.sort_values(by='Hora', ascending=True)
    df_rain = df[(df['Lluvia'] == 1) & (df['Hora'] > 6) & (df['Hora'] < 22)]
    df_rain = df_rain[['Hora', 'Condicion']]
    df_rain.set_index('Hora', inplace=True)
    return df_rain

# Función para enviar un mensaje a través de Twilio con los datos meteorológicos
def send_message(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, input_date, df, query, TO):
    """
    Envía un mensaje a través de Twilio con los datos meteorológicos.
    Args:
    - TWILIO_ACCOUNT_SID (str): SID de la cuenta de Twilio.
    - TWILIO_AUTH_TOKEN (str): Token de autenticación de Twilio.
    - input_date (str): Fecha actual en el formato "YYYY-MM-DD".
    - df (DataFrame): DataFrame con datos meteorológicos.
    - query (str): Ubicación para la consulta meteorológica.
    - TO (str): Número de teléfono del destinatario.
    Returns:
    - message_id (str): ID del mensaje enviado.
    """
    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    message = client.messages \
                    .create(
                        body='\nHola! \n\n\n El pronóstico de lluvia hoy '+ input_date +' en ' + query +' es : \n\n\n ' + str(df),
                        from_=PHONE_NUMBER,
                        to= TO
                    )
    return message.sid
