from typing import List, Tuple


def generate_answer(question: str, relevant_chunks: List[Tuple[int, str]]) -> str:
    """
    Genera una respuesta basada en los fragmentos encontrados.

    Esta versión no depende de una API externa.
    Para el Challenge funciona como agente básico basado en recuperación de información.
    """
    if not question.strip():
        return "Escribe una pregunta para que pueda buscar información en la documentación."

    if not relevant_chunks:
        return (
            "No encontré información suficiente en la base de conocimiento para responder esa pregunta. "
            "Intenta preguntar sobre certificados, cursos, becas, reembolsos, soporte técnico, pagos o evaluaciones."
        )

    context = "\n\n".join([chunk for _, chunk in relevant_chunks])

    answer = (
        "Según la documentación de EduNova Academy, encontré esta información relevante:\n\n"
        f"{context}\n\n"
        "Respuesta generada con base en los documentos cargados."
    )

    return answer