import os
from typing import List, Tuple

import cohere
from dotenv import load_dotenv


load_dotenv()


def build_prompt(question: str, relevant_chunks: List[Tuple[int, str]]) -> str:
    """
    Construye el prompt que se enviará al modelo de IA.
    """
    context = "\n\n".join([chunk for _, chunk in relevant_chunks])

    prompt = f"""
Eres EduBot Knowledge Agent, un asistente de soporte académico de EduNova Academy.

Tu tarea es responder preguntas usando únicamente la información encontrada en la base de conocimiento proporcionada.

Reglas:
- Responde en español.
- Sé claro, directo y útil.
- No inventes información.
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
    if not question.strip():
        return "Escribe una pregunta para que pueda buscar información en la documentación."

    if not relevant_chunks:
        return (
            "No encontré información suficiente en la base de conocimiento para responder esa pregunta. "
            "Puedes intentar preguntar sobre certificados, cursos, becas, reembolsos, soporte técnico, pagos o evaluaciones."
        )

    api_key = os.getenv("COHERE_API_KEY")

    if not api_key:
        return (
            "No se encontró la variable COHERE_API_KEY. "
            "Agrega tu clave de Cohere en un archivo .env para activar las respuestas con IA."
        )

    try:
        co = cohere.Client(api_key)

        prompt = build_prompt(question, relevant_chunks)

        response = co.chat(
            model="command-r-08-2024",
            message=prompt,
            temperature=0.2
        )

        return response.text.strip()

    except Exception as error:
        return (
            "Ocurrió un error al generar la respuesta con IA. "
            f"Detalle técnico: {error}"
        )