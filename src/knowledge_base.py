import re
from typing import List, Tuple


def split_text_into_chunks(text: str, chunk_size: int = 900) -> List[str]:
    """
    Divide un texto largo en fragmentos para facilitar la búsqueda de información.
    """
    clean_text = re.sub(r"\s+", " ", text).strip()

    chunks = []
    start = 0

    while start < len(clean_text):
        end = start + chunk_size
        chunk = clean_text[start:end]
        chunks.append(chunk)
        start = end

    return chunks


def normalize_text(text: str) -> str:
    """
    Normaliza texto para comparar preguntas contra la base de conocimiento.
    """
    text = text.lower()
    text = re.sub(r"[^\wáéíóúñü\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def calculate_score(question: str, chunk: str) -> int:
    """
    Calcula una puntuación simple según palabras coincidentes.
    No es magia, es conteo de palabras. Triste, pero efectivo para empezar.
    """
    question_words = set(normalize_text(question).split())
    chunk_words = set(normalize_text(chunk).split())

    ignored_words = {
        "que", "qué", "como", "cómo", "cual", "cuál", "cuando", "cuándo",
        "donde", "dónde", "para", "por", "con", "los", "las", "una", "uno",
        "del", "de", "la", "el", "en", "y", "o", "si", "mi", "mis", "un"
    }

    question_words = question_words - ignored_words

    return len(question_words.intersection(chunk_words))


def search_relevant_chunks(
    question: str,
    chunks: List[str],
    top_k: int = 4
) -> List[Tuple[int, str]]:
    """
    Busca los fragmentos más relacionados con la pregunta del usuario.
    """
    scored_chunks = []

    for chunk in chunks:
        score = calculate_score(question, chunk)

        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(reverse=True, key=lambda item: item[0])

    return scored_chunks[:top_k]


def build_context(relevant_chunks: List[Tuple[int, str]]) -> str:
    """
    Une los fragmentos relevantes en un solo contexto.
    """
    if not relevant_chunks:
        return ""

    return "\n\n".join([chunk for _, chunk in relevant_chunks])

def find_course_catalog_answer(question: str, csv_tables) -> str | None:
    """
    Responde preguntas estructuradas sobre el catálogo de cursos usando los CSV cargados.

    Devuelve None si la pregunta no parece ser sobre el catálogo.
    """
    question_normalized = normalize_text(question)

    if not csv_tables:
        return None

    catalog_dataframe = None

    for file_name, dataframe in csv_tables:
        required_columns = {
            "nombre_curso",
            "categoria",
            "nivel",
            "duracion_horas",
            "modalidad",
            "costo_mxn",
            "requisitos_previos",
            "tipo_certificado",
            "estado"
        }

        if required_columns.issubset(set(dataframe.columns)):
            catalog_dataframe = dataframe
            break

    if catalog_dataframe is None:
        return None

    # Preguntas sobre cursos de nivel principiante
    beginner_keywords = [
        "nivel principiante",
        "cursos principiantes",
        "cursos de principiante",
        "para principiantes",
        "principiante"
    ]

    if "curso" in question_normalized and any(keyword in question_normalized for keyword in beginner_keywords):
        courses = catalog_dataframe[
            catalog_dataframe["nivel"].astype(str).str.lower().str.strip() == "principiante"
        ]

        if courses.empty:
            return "No encontré cursos de nivel principiante en el catálogo."

        course_names = courses["nombre_curso"].tolist()

        response = "Según el catálogo, estos son los cursos de nivel principiante:\n\n"

        for course_name in course_names:
            response += f"- {course_name}\n"

        return response.strip()

    # Preguntas sobre cursos de nivel intermedio
    intermediate_keywords = [
        "nivel intermedio",
        "cursos intermedios",
        "cursos de intermedio",
        "intermedio"
    ]

    if "curso" in question_normalized and any(keyword in question_normalized for keyword in intermediate_keywords):
        courses = catalog_dataframe[
            catalog_dataframe["nivel"].astype(str).str.lower().str.strip() == "intermedio"
        ]

        if courses.empty:
            return "No encontré cursos de nivel intermedio en el catálogo."

        course_names = courses["nombre_curso"].tolist()

        response = "Según el catálogo, estos son los cursos de nivel intermedio:\n\n"

        for course_name in course_names:
            response += f"- {course_name}\n"

        return response.strip()

    # Preguntas sobre cursos de nivel avanzado
    advanced_keywords = [
        "nivel avanzado",
        "cursos avanzados",
        "cursos de avanzado",
        "avanzado"
    ]

    if "curso" in question_normalized and any(keyword in question_normalized for keyword in advanced_keywords):
        courses = catalog_dataframe[
            catalog_dataframe["nivel"].astype(str).str.lower().str.strip() == "avanzado"
        ]

        if courses.empty:
            return "No encontré cursos de nivel avanzado en el catálogo."

        course_names = courses["nombre_curso"].tolist()

        response = "Según el catálogo, estos son los cursos de nivel avanzado:\n\n"

        for course_name in course_names:
            response += f"- {course_name}\n"

        return response.strip()

    # Preguntas sobre Cloud Computing
    if "curso" in question_normalized and "cloud" in question_normalized:
        courses = catalog_dataframe[
            catalog_dataframe["categoria"].astype(str).str.lower().str.contains("cloud computing", na=False)
        ]

        if courses.empty:
            return "No encontré cursos de Cloud Computing en el catálogo."

        response = "Según el catálogo, estos son los cursos de Cloud Computing:\n\n"

        for _, row in courses.iterrows():
            response += (
                f"- {row['nombre_curso']} "
                f"({row['nivel']}, {row['duracion_horas']} horas, {row['costo_mxn']} MXN)\n"
            )

        return response.strip()

    # Pregunta específica sobre Python Básico
    if "python basico" in question_normalized or "python básico" in question.lower():
        course = catalog_dataframe[
            catalog_dataframe["nombre_curso"].astype(str).str.lower().str.strip() == "python básico"
        ]

        if not course.empty:
            row = course.iloc[0]
            return (
                f"El curso Python Básico cuesta {row['costo_mxn']} MXN. "
                f"Tiene una duración de {row['duracion_horas']} horas, "
                f"es de nivel {row['nivel']} y su modalidad es {row['modalidad']}."
            )

    return None