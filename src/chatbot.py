import os
from typing import List, Tuple

import cohere
from dotenv import load_dotenv


# Carga las variables definidas en el archivo .env, como COHERE_API_KEY.
load_dotenv()


def is_greeting(message: str) -> bool:
    """
    Detecta si el usuario envió un saludo simple.
    """
    # Lista de saludos aceptados para responder sin consultar la IA.
    greetings = {
        "hola",
        "hola :D",
        "hola :)",
        "holaa",
        "holaaa",
        "buenos días",
        "buenos dias",
        "buen día",
        "buen dia",
        "buenas tardes",
        "buenas noches",
        "hey",
        "hello",
        "hi",
        "qué tal",
        "que tal",
        "cómo estás",
        "como estas",
        "saludos",
        "qué onda",
        "que onda"
    }

    # Normaliza el texto para comparar saludos aunque tengan mayúsculas o signos.
    clean_message = message.lower().strip()
    clean_message = clean_message.replace("¿", "").replace("?", "")
    clean_message = clean_message.replace("¡", "").replace("!", "")
    clean_message = clean_message.replace(".", "").replace(",", "")

    return clean_message in greetings


def get_welcome_message() -> str:
    """
    Devuelve el mensaje de bienvenida de EduBot.
    """
    return (
        "¡Hola! Soy EduBot Knowledge Agent, tu asistente inteligente de EduNova Academy. "
        "Estoy aquí para ayudarte a consultar información sobre cursos, certificados, becas, "
        "pagos, reembolsos, evaluaciones, soporte técnico y reglamento académico. "
        "Escribe tu pregunta y buscaré la respuesta en la base de conocimiento cargada."
    )


def build_prompt(question: str, relevant_chunks: List[Tuple[int, str]]) -> str:
    """
    Construye el prompt que se enviará al modelo de IA.
    """
    # Une los fragmentos relevantes recuperados para dar contexto al modelo.
    context = "\n\n".join([chunk for _, chunk in relevant_chunks])

    # Define instrucciones, pregunta y contexto para controlar la respuesta de EduBot.
    prompt = f"""
Eres EduBot Knowledge Agent, un asistente de soporte académico de EduNova Academy.

Tu tarea es responder preguntas usando únicamente la información encontrada en la base de conocimiento proporcionada.

Reglas:
- Responde en español.
- Sé claro, directo y útil.
- No inventes información.
- Si el usuario solo saluda o no hace una pregunta concreta, responde con un saludo breve y menciona los temas sobre los que puedes ayudar.
- No uses información del catálogo o documentos institucionales si el usuario no preguntó por un tema específico.
- No recomiendes cursos, precios o políticas si el usuario solo saluda.
- Si el contexto no contiene la respuesta, indica que no encontraste información suficiente.
- Si la pregunta trata sobre cursos, precios, duración, nivel o requisitos, usa la información del catálogo.
- Si la pregunta trata sobre certificados, becas, reembolsos, soporte, pagos, evaluaciones o reglamento, usa la documentación institucional.
- No pegues todo el contexto.
- Resume la respuesta de forma natural.

Pregunta del usuario:
{question}

Contexto encontrado en la base de conocimiento:
{context}

Respuesta:
"""
    return prompt


def generate_answer(question: str, relevant_chunks: List[Tuple[int, str]]) -> str:
    """
    Genera una respuesta usando Cohere con base en los fragmentos recuperados.
    """
    # Evita llamar a la IA si el usuario no escribió una pregunta.
    if not question.strip():
        return "Escribe una pregunta para que pueda buscar información en la documentación."

    # Responde saludos directamente para no gastar una llamada al modelo.
    if is_greeting(question):
        return get_welcome_message()

    # Si no hay fragmentos recuperados, no hay contexto confiable para responder.
    if not relevant_chunks:
        return (
            "No encontré información suficiente en la base de conocimiento para responder esa pregunta. "
            "Puedes intentar preguntar sobre certificados, cursos, becas, reembolsos, soporte técnico, pagos o evaluaciones."
        )

    # Obtiene la clave de Cohere desde las variables de entorno cargadas con load_dotenv().
    api_key = os.getenv("COHERE_API_KEY")

    if not api_key:
        return (
            "No se encontró la variable COHERE_API_KEY. "
            "Agrega tu clave de Cohere en un archivo .env para activar las respuestas con IA."
        )

    try:
        # Crea el cliente de Cohere usando la clave configurada.
        co = cohere.Client(api_key)

        # Genera el prompt final con la pregunta y los fragmentos relevantes.
        prompt = build_prompt(question, relevant_chunks)

        # Envía el prompt al modelo y configura baja temperatura para respuestas más estables.
        response = co.chat(
            model="command-r-08-2024",
            message=prompt,
            temperature=0.2
        )

        # Devuelve el texto limpio que responde el modelo.
        return response.text.strip()

    except Exception as error:
        # Muestra un mensaje controlado si falla la conexión o la generación de Cohere.
        return (
            "Ocurrió un error al generar la respuesta con IA. "
            f"Detalle técnico: {error}"
        )
