import flet
from flet import Page, TextField, ElevatedButton, Column, Text, Container, Colors, alignment, Dropdown, dropdown 
from openai import OpenAI
import requests
from dotenv import load_dotenv
import os 

load_dotenv()

# Configuración de OpenRouter (o servicio compatible)
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
WEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

# Configurar cliente OpenAI para OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def get_weather(city):
    """Obtener información del clima para una ciudad"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=es"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            return f"El clima en {city} es {description} con una temperatura de {temp}°C"
        else:
            return f"Error al obtener el clima: {data.get('message', 'Ciudad no encontrada')}"  
    except Exception as e:
        return f"Error al consultar el clima: {str(e)}"
    
def get_ai_response(prompt):
    """Obtener respuesta del modelo AI"""
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",  # Modelo correcto para OpenRouter
            messages=[
                {"role": "system", "content": "Eres un asistente amigable y útil."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al consultar la IA: {str(e)}"
    
def main(page: Page):
    page.title = "Chatbot con Flet"
    page.bgcolor = Colors.BLUE_GREY_900
    page.theme_mode = "dark"

    input_box = TextField(
        label="Escribe tu mensaje",
        border_color=Colors.BLUE_200,
        focused_border_color=Colors.BLUE_400,
        text_style=flet.TextStyle(color=Colors.WHITE),
        expand=True
    )

    mode_dropdown = Dropdown(
        options=[
            dropdown.Option("chat", "Chat con IA"),
            dropdown.Option("weather", "Consultar clima")       
        ],
        value="chat",
        label="Modo",
        border_color=Colors.BLUE_200,
        color=Colors.WHITE
     )
    
    chat_area = Column(scroll='auto', expand=True)
    
    send_button = ElevatedButton(
        text="Enviar",   
        bgcolor=Colors.BLUE_700,
        color=Colors.WHITE
    )

    chat_container = Container(
        content=chat_area,
        bgcolor=Colors.BLUE_GREY_800,
        padding=10,
        border_radius=10,
        expand=True
    )

    input_container = Container(
        content=flet.Row(
            controls=[
                mode_dropdown,
                input_box,
                send_button
            ],
            spacing=10 
        )
    )

    def send_message(e):
        user_message = input_box.value
        if not user_message:
            return
        
        # Mostrar mensaje del usuario
        chat_area.controls.append(Text(f"Usuario: {user_message}", color=Colors.WHITE))

        # Procesar según el modo seleccionado
        if mode_dropdown.value == "weather":
            response = get_weather(user_message)
        else: # modo chat
            response = get_ai_response(user_message)

        # Mostrar respuesta
        chat_area.controls.append(Text(f"Chatbot: {response}", color=Colors.BLUE_200))

        # Limpiar input y actualizar UI
        input_box.value = ""
        page.update()

    send_button.on_click = send_message

    page.add(
        chat_container,
        input_container
    )

    page.window_width = 800
    page.window_height = 600
    page.update()

if __name__ == "__main__":
    flet.app(target=main)