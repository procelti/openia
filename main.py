import openai
import time
import sys
import os
import io
import requests
from colorama import Fore, Style, init
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

# Inicializa colorama para el manejo de colores en consola
init(autoreset=True)

# Coloca aquí tu API Key de OpenAI
openai.api_key = "sk-proj--"

# -------------------------------------------------------------------
#                      FUNCIONES AUXILIARES
# -------------------------------------------------------------------

def menu_principal():
    """Despliega el menú principal en consola."""
    print(Fore.GREEN + "\n===== MENÚ PRINCIPAL =====")
    print("1) Generar imagen con DALL·E a partir de un prompt")
    print("2) Chatbot (pregunta-respuesta)")
    print("3) Imprimir curso (emitir certificado)")
    print("4) Salir")

def animacion_cargando(texto="Cargando", puntos=3, delay=0.5):
    """Simula una animación de 'Cargando...' en consola."""
    for i in range(puntos):
        sys.stdout.write(f"\r{Fore.YELLOW}{texto}{'.' * (i + 1)}{' ' * (puntos - i)}")
        sys.stdout.flush()
        time.sleep(delay)
    print(Style.RESET_ALL)

def escribir_texto(texto, delay=0.02):
    """Simula que el texto se escribe carácter por carácter."""
    for char in texto:
        sys.stdout.write(Fore.CYAN + char)
        sys.stdout.flush()
        time.sleep(delay)
    print(Style.RESET_ALL)

# -------------------------------------------------------------------
#        1) GENERAR IMAGEN CON DALL·E A PARTIR DE UN PROMPT
# -------------------------------------------------------------------

def generar_imagen_dalle():
    """
    Genera una imagen usando la API de DALL·E (openai.Image.create)
    y la guarda en el directorio actual.
    """
    print(Fore.BLUE + "\n--- GENERAR IMAGEN CON DALL·E ---")
    prompt = input("Ingresa la descripción (prompt) para la imagen: ")
    if not prompt.strip():
        print(Fore.RED + "El prompt está vacío. Regresando al menú principal...")
        return

    animacion_cargando()

    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,           # Genera 1 imagen
            size="512x512" # Tamaño de la imagen
        )
        # La respuesta trae una lista de URLs
        image_url = response['data'][0]['url']
        
        # Descarga la imagen y la guarda
        nombre_archivo = f"imagen_generada_{int(time.time())}.png"
        with open(nombre_archivo, "wb") as f:
            imagen_bytes = requests.get(image_url).content
            f.write(imagen_bytes)
        
        escribir_texto(f"\n¡Imagen generada con éxito!\nSe guardó como: {nombre_archivo}")
        escribir_texto(f"URL de la imagen: {image_url}")
    except Exception as e:
        print(Fore.RED + "Ocurrió un error al llamar a la API de OpenAI para generar la imagen:")
        print(e)

# -------------------------------------------------------------------
#             2) CHATBOT (PREGUNTA-RESPUESTA) TRADICIONAL
# -------------------------------------------------------------------

def chatbot_tradicional():
    """
    Implementa un chatbot usando ChatCompletion con gpt-3.5-turbo.
    El usuario puede interactuar hasta escribir 'salir'.
    """
    print(Fore.BLUE + "\n--- CHATBOT TRADICIONAL ---")
    print(Fore.YELLOW + "Escribe 'salir' para volver al menú principal.\n")

    # Historial de la conversación
    messages = [
        {"role": "system", "content": "Eres un asistente virtual. Responde de forma clara y concisa."}
    ]

    while True:
        user_input = input(Fore.GREEN + "Tú: " + Style.RESET_ALL)
        if user_input.lower() in ["salir", "exit"]:
            print(Fore.YELLOW + "Regresando al menú principal...\n")
            break

        messages.append({"role": "user", "content": user_input})
        animacion_cargando()

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            respuesta = response.choices[0].message.content
            messages.append({"role": "assistant", "content": respuesta})
            escribir_texto("Asistente: " + respuesta)
        except Exception as e:
            print(Fore.RED + "Ocurrió un error al llamar a la API de OpenAI:")
            print(e)
            break

# -------------------------------------------------------------------
#             3) IMPRIMIR CURSO (CERTIFICADO)
# -------------------------------------------------------------------

def imprimir_curso():
    """
    Solicita el nombre del estudiante, pregunta si desea emitir su certificado.
    Si se acepta y se valida el PIN 9826, genera un PDF con el nombre centrado en mayúsculas,
    con un margen superior de 8 cm y con una imagen de fondo que cubra la hoja (tamaño carta).
    El documento se nombra como: [NOMBRE]_constancia_taller_aprendiendo_de_la_ia.pdf
    """
    print(Fore.MAGENTA + "\n--- EMISIÓN DE CERTIFICADO ---\n")
    student_name = input("Por favor, ingresa tu nombre completo: ").strip()
    if not student_name:
        print(Fore.RED + "Nombre vacío. Regresando al menú principal.")
        return

    print(Fore.CYAN + f"Hola {student_name}, se emitirá el certificado de validación.")
    generar_cert = input("¿Desea emitir su certificado de validación? (si generar, no generar): ").strip().lower()
    if generar_cert != "si":
        print(Fore.YELLOW + "Certificado no generado. Regresando al menú principal.")
        return

    pin = input("Ingrese la clave de validación: ").strip()
    if pin != "9826":
        print(Fore.RED + "Clave incorrecta. Regresando al menú principal.")
        return

    # Descargar la imagen de fondo
    bg_url = "https://hpgwhbeumsrcmprseibr.supabase.co/storage/v1/object/public/app//sello.png"
    try:
        response = requests.get(bg_url)
        if response.status_code != 200:
            print(Fore.RED + "No se pudo obtener la imagen de fondo. Certificado no generado.")
            return
        bg_image_data = response.content
    except Exception as e:
        print(Fore.RED + "Error al descargar la imagen de fondo. Certificado no generado.")
        print(e)
        return

    # Crear el PDF con ReportLab
    pdf_filename = f"{student_name.upper().replace(' ', '_')}_constancia_taller_aprendiendo_de_la_ia.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    # Rellena la página con un fondo blanco
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, width, height, stroke=0, fill=1)

    # Establecer la imagen de fondo cubriendo toda la página
    bg_image = ImageReader(io.BytesIO(bg_image_data))
    c.drawImage(bg_image, 0, 0, width=width, height=height)

    # Configurar fuente y color para el nombre
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 20)
    # Calcular posición para centrar el nombre, con margen superior de 8 cm
    y_position = height - 8.5 * cm
    text = student_name.upper()
    text_width = c.stringWidth(text, "Helvetica-Bold", 24)
    x_position = ((width - text_width) / 2) + 27
    c.drawString(x_position, y_position, text)
    c.showPage()
    c.save()

    print(Fore.GREEN + f"Certificado generado exitosamente: {pdf_filename}")

# -------------------------------------------------------------------
#                          PROGRAMA PRINCIPAL
# -------------------------------------------------------------------

def main():
    print(Fore.MAGENTA + "======================================")
    ascii_art = Fore.MAGENTA + """
  ______ _______ ______        __     _ __  ______ 
 / _____|_______|____  \      / /    | /  |/ __   |
| /      _____   ____)  )    / /_   / /_/ | | //| |
| |     |  ___) |  __  (    / __ \ / /  | | |// | |
| \_____| |_____| |__)  )  ( (__) ) /   | |  /__| |
 \______)_______)______/    \____/_|    |_|\_____/ 
"""
    print(ascii_art)


    print(Fore.MAGENTA + "   TALLER - APRENDIENDO DE LA IA  ")
    print(Fore.MAGENTA + "======================================")
    
    while True:
        menu_principal()
        opcion = input(Fore.CYAN + "\nSelecciona una opción: " + Style.RESET_ALL)

        if opcion == "1":
            generar_imagen_dalle()
        elif opcion == "2":
            chatbot_tradicional()
        elif opcion == "3":
            imprimir_curso()
        elif opcion == "4":
            print(Fore.YELLOW + "¡Hasta luego!")
            break
        else:
            print(Fore.RED + "Opción inválida. Intenta de nuevo.")

if __name__ == "__main__":
    main()

# pip install colorama requests
# pip install openai==0.28.0
# pip install reportlab
