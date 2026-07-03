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