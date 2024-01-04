Envio diario del pronóstico del tiempo con Weather API mediante mensajería de Twilio desde una instancia de AWS EC2.

El script de python hace request pasándole una ciudad a Weather API y la API devuelve un JSON con los datos del pronóstico, se hace una transformación de los datos y en un dataframe de pandas se guarda información relevante que posteriormente es enviada desde el script de python por medio del proveedor de comunicaciones cloud Twilio y finalmente recibo un SMS en mi móvil con dicho pronóstico.

Todo se ejecuta sobre Ubuntu que corre sobre una instancia de AWS EC2, el pronóstico se envia diario, la configuración respectiva del horario se realiza en Crontab.