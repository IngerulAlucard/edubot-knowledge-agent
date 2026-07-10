import unicodedata
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
    Quita acentos, signos y espacios repetidos.
    """
    text = str(text).lower()

    text = unicodedata.normalize("NFD", text)
    text = "".join(
        character for character in text
        if unicodedata.category(character) != "Mn"
    )

    text = re.sub(r"[^\w\s]", " ", text)
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
        "que", "como", "cual", "cuando", "donde", "para", "por", "con",
        "los", "las", "una", "uno", "del", "de", "la", "el", "en", "y",
        "o", "si", "mi", "mis", "un"
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
    Responde preguntas estructuradas sobre el catálogo de cursos usando el CSV cargado.

    Esta función evita que el modelo de IA tenga que "adivinar" filtros de tabla.
    Para consultas de cursos por precio, categoría, nivel, modalidad, certificado,
    estado, duración, requisitos o nombre, se usa pandas directamente.
    """
    question_normalized = normalize_text(question)
    question_words = set(question_normalized.split())

    asks_for_courses = (
        "curso" in question_words
        or "cursos" in question_words
        or "catalogo" in question_words
        or "catalogo" in question_normalized
    )

    if not csv_tables:
        return None

    required_columns = {
        "id_curso",
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

    catalog_dataframe = None

    for _, dataframe in csv_tables:
        if required_columns.issubset(set(dataframe.columns)):
            catalog_dataframe = dataframe.copy()
            break

    if catalog_dataframe is None:
        return None

    df = catalog_dataframe.copy()
    df["costo_mxn"] = df["costo_mxn"].astype(int)
    df["duracion_horas"] = df["duracion_horas"].astype(int)

    def contains_any(phrases: list[str]) -> bool:
        return any(normalize_text(phrase) in question_normalized for phrase in phrases)

    def has_word(word: str) -> bool:
        return normalize_text(word) in question_words

    def format_course_rows(courses, title: str) -> str:
        """
        Formatea varios cursos encontrados en una lista clara.
        """
        if courses.empty:
            return "No encontré cursos que coincidan con esa búsqueda en el catálogo."

        response = f"{title}\n\n"

        for _, row in courses.iterrows():
            response += (
                f"- {row['nombre_curso']} "
                f"({row['categoria']}, {row['nivel']}, "
                f"{row['duracion_horas']} horas, {row['modalidad']}, "
                f"{row['costo_mxn']} MXN, {row['tipo_certificado']})\n"
            )

        return response.strip()

    # =========================
    # 1. Curso más barato
    # =========================
    if asks_for_courses and contains_any([
        "mas barato",
        "mas economico",
        "menor costo",
        "menor precio",
        "curso barato",
        "curso economico"
    ]):
        min_cost = df["costo_mxn"].min()
        courses = df[df["costo_mxn"] == min_cost]

        return format_course_rows(
            courses,
            f"Según el catálogo, el curso más barato cuesta {min_cost} MXN:"
        )

    # =========================
    # 2. Curso más caro
    # =========================
    if asks_for_courses and contains_any([
        "mas caro",
        "mayor costo",
        "mayor precio",
        "curso caro"
    ]):
        max_cost = df["costo_mxn"].max()
        courses = df[df["costo_mxn"] == max_cost]

        return format_course_rows(
            courses,
            f"Según el catálogo, el curso más caro cuesta {max_cost} MXN:"
        )

    # =========================
    # 3. Filtros por precio/costo
    # =========================
    less_than_match = re.search(
        r"(menos de|menor a|menores a|menor que|por debajo de|debajo de)\s+(\d+)",
        question_normalized
    )

    if asks_for_courses and less_than_match:
        max_price = int(less_than_match.group(2))
        courses = df[df["costo_mxn"] < max_price]

        return format_course_rows(
            courses,
            f"Según el catálogo, estos son los cursos con costo menor a {max_price} MXN:"
        )

    greater_than_match = re.search(
        r"(mas de|mayor a|mayores a|mayor que|por encima de|encima de)\s+(\d+)",
        question_normalized
    )

    if asks_for_courses and greater_than_match:
        min_price = int(greater_than_match.group(2))
        courses = df[df["costo_mxn"] > min_price]

        return format_course_rows(
            courses,
            f"Según el catálogo, estos son los cursos con costo mayor a {min_price} MXN:"
        )

    between_match = re.search(
        r"entre\s+(\d+)\s+y\s+(\d+)",
        question_normalized
    )

    if asks_for_courses and between_match:
        min_price = int(between_match.group(1))
        max_price = int(between_match.group(2))

        courses = df[
            (df["costo_mxn"] >= min_price)
            & (df["costo_mxn"] <= max_price)
        ]

        return format_course_rows(
            courses,
            f"Según el catálogo, estos son los cursos con costo entre {min_price} y {max_price} MXN:"
        )

    # =========================
    # 4. Filtro especial por modalidad asincrónica / sincrónica
    # IMPORTANTE:
    # Se evalúa asincrónica antes que sincrónica porque "asincronica"
    # contiene la palabra "sincronica" como subcadena.
    # Además se usan palabras completas, no substring.
    # =========================
    if asks_for_courses and (
        "asincronica" in question_words
        or "asincronico" in question_words
        or "asincronicas" in question_words
        or "asincronicos" in question_words
    ):
        courses = df[
            df["modalidad"].astype(str).apply(
                lambda value: normalize_text(value) in ["asincronica", "asincronico"]
            )
        ]

        if courses.empty:
            return "Según el catálogo actual, no hay cursos con modalidad asincrónica disponibles."

        return format_course_rows(
            courses,
            "Según el catálogo, estos son los cursos con modalidad asincrónica:"
        )

    if asks_for_courses and (
        "sincronica" in question_words
        or "sincronico" in question_words
        or "sincronicas" in question_words
        or "sincronicos" in question_words
    ):
        courses = df[
            df["modalidad"].astype(str).apply(
                lambda value: normalize_text(value) in ["sincronica", "sincronico"]
            )
        ]

        if courses.empty:
            return (
                "Según el catálogo actual, no hay cursos con modalidad sincrónica disponibles.\n\n"
                "Actualmente los cursos registrados en el catálogo tienen modalidad asincrónica."
            )

        return format_course_rows(
            courses,
            "Según el catálogo, estos son los cursos con modalidad sincrónica:"
        )

    # =========================
    # 5. Preguntas por nombre exacto/parcial de curso
    # =========================
    for _, row in df.iterrows():
        course_name = str(row["nombre_curso"])
        course_name_normalized = normalize_text(course_name)

        if course_name_normalized in question_normalized:
            if contains_any(["cuanto cuesta", "precio", "costo", "vale"]):
                return f"El curso {row['nombre_curso']} cuesta {row['costo_mxn']} MXN."

            if contains_any(["cuanto dura", "duracion", "horas"]):
                return f"El curso {row['nombre_curso']} dura {row['duracion_horas']} horas."

            return (
                f"Según el catálogo, el curso {row['nombre_curso']} tiene estos datos:\n\n"
                f"- ID: {row['id_curso']}\n"
                f"- Categoría: {row['categoria']}\n"
                f"- Nivel: {row['nivel']}\n"
                f"- Duración: {row['duracion_horas']} horas\n"
                f"- Modalidad: {row['modalidad']}\n"
                f"- Costo: {row['costo_mxn']} MXN\n"
                f"- Requisitos previos: {row['requisitos_previos']}\n"
                f"- Tipo de certificado: {row['tipo_certificado']}\n"
                f"- Estado: {row['estado']}"
            )

    # =========================
    # 6. Filtro por categoría
    # =========================
    categories = df["categoria"].dropna().unique()

    for category in categories:
        category_normalized = normalize_text(str(category))

        if asks_for_courses and category_normalized in question_normalized:
            courses = df[
                df["categoria"].astype(str).apply(
                    lambda value: normalize_text(value) == category_normalized
                )
            ]

            return format_course_rows(
                courses,
                f"Según el catálogo, estos son los cursos de {category}:"
            )

    category_aliases = {
        "base de datos": "Bases de Datos",
        "bases de datos": "Bases de Datos",
        "programacion": "Programación",
        "cloud": "Cloud Computing",
        "oracle cloud": "Cloud Computing",
        "oci": "Cloud Computing",
        "inteligencia artificial": "Inteligencia Artificial",
        "analisis de datos": "Análisis de Datos",
        "backend": "Desarrollo Backend",
        "desarrollo backend": "Desarrollo Backend",
        "internet de las cosas": "Internet de las Cosas",
        "gestion de proyectos": "Gestión de Proyectos",
        "ingenieria de software": "Ingeniería de Software",
    }

    short_category_aliases = {
        "ia": "Inteligencia Artificial",
        "iot": "Internet de las Cosas",
    }

    for alias, category in category_aliases.items():
        if asks_for_courses and normalize_text(alias) in question_normalized:
            category_normalized = normalize_text(category)
            courses = df[
                df["categoria"].astype(str).apply(
                    lambda value: normalize_text(value) == category_normalized
                )
            ]

            return format_course_rows(
                courses,
                f"Según el catálogo, estos son los cursos de {category}:"
            )

    for alias, category in short_category_aliases.items():
        if asks_for_courses and has_word(alias):
            category_normalized = normalize_text(category)
            courses = df[
                df["categoria"].astype(str).apply(
                    lambda value: normalize_text(value) == category_normalized
                )
            ]

            return format_course_rows(
                courses,
                f"Según el catálogo, estos son los cursos de {category}:"
            )

    # =========================
    # 7. Filtro por nivel
    # =========================
    levels = df["nivel"].dropna().unique()

    for level in levels:
        level_normalized = normalize_text(str(level))

        if asks_for_courses and (
            level_normalized in question_words
            or f"nivel {level_normalized}" in question_normalized
        ):
            courses = df[
                df["nivel"].astype(str).apply(
                    lambda value: normalize_text(value) == level_normalized
                )
            ]

            return format_course_rows(
                courses,
                f"Según el catálogo, estos son los cursos de nivel {level}:"
            )

    # =========================
    # 8. Filtro por modalidad general
    # =========================
    modalities = df["modalidad"].dropna().unique()

    for modality in modalities:
        modality_normalized = normalize_text(str(modality))

        if asks_for_courses and modality_normalized in question_words:
            courses = df[
                df["modalidad"].astype(str).apply(
                    lambda value: normalize_text(value) == modality_normalized
                )
            ]

            return format_course_rows(
                courses,
                f"Según el catálogo, estos son los cursos con modalidad {modality}:"
            )

    # =========================
    # 9. Filtro por tipo de certificado
    # =========================
    if asks_for_courses and ("constancia" in question_words or "constancias" in question_words):
        courses = df[
            df["tipo_certificado"].astype(str).apply(
                lambda value: "constancia" in normalize_text(value).split()
            )
        ]

        return format_course_rows(
            courses,
            "Según el catálogo, estos son los cursos que ofrecen constancia digital:"
        )

    if asks_for_courses and (
        "certificado" in question_words
        or "certificados" in question_words
    ):
        courses = df[
            df["tipo_certificado"].astype(str).apply(
                lambda value: "certificado" in normalize_text(value).split()
            )
        ]

        return format_course_rows(
            courses,
            "Según el catálogo, estos son los cursos que ofrecen certificado digital:"
        )

    # =========================
    # 10. Filtro por estado
    # =========================
    if asks_for_courses and ("activo" in question_words or "activos" in question_words):
        courses = df[
            df["estado"].astype(str).apply(
                lambda value: normalize_text(value) == "activo"
            )
        ]

        return format_course_rows(
            courses,
            "Según el catálogo, estos son los cursos activos:"
        )

    if asks_for_courses and ("inactivo" in question_words or "inactivos" in question_words):
        courses = df[
            df["estado"].astype(str).apply(
                lambda value: normalize_text(value) == "inactivo"
            )
        ]

        return format_course_rows(
            courses,
            "Según el catálogo, estos son los cursos inactivos:"
        )

    # =========================
    # 11. Filtro por requisitos previos
    # =========================
    if asks_for_courses and contains_any(["requieren", "requisito", "requisitos", "necesitan", "piden"]):
        requirement_aliases = {
            "python": ["python"],
            "sql": ["sql"],
            "linux": ["linux"],
            "docker": ["docker"],
            "java": ["java"],
            "javascript": ["javascript"],
            "html": ["html"],
            "css": ["css"],
            "cloud": ["cloud"],
            "programación": ["programacion"],
            "estadística": ["estadistica"],
            "electrónica": ["electronica"],
        }

        for label, aliases in requirement_aliases.items():
            if any(alias in question_words for alias in aliases):
                courses = df[
                    df["requisitos_previos"].astype(str).apply(
                        lambda value: any(
                            alias in normalize_text(value).split()
                            for alias in aliases
                        )
                    )
                ]

                return format_course_rows(
                    courses,
                    f"Según el catálogo, estos cursos tienen como requisito {label}:"
                )

    return None
