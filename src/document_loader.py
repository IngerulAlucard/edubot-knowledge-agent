from pathlib import Path
import pandas as pd
from pypdf import PdfReader


def load_pdf_text(pdf_path: str) -> str:
    """
    Lee un archivo PDF y extrae todo el texto disponible.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo PDF: {pdf_path}")

    reader = PdfReader(str(path))
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text.strip()


def load_csv_data(csv_path: str) -> pd.DataFrame:
    """
    Lee el catálogo de cursos desde un archivo CSV.
    """
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo CSV: {csv_path}")

    return pd.read_csv(path)


def csv_to_text(dataframe: pd.DataFrame) -> str:
    """
    Convierte el contenido del CSV en texto legible para usarlo como base de conocimiento.
    """
    rows = []

    for _, row in dataframe.iterrows():
        course_info = (
            f"ID del curso: {row.get('id_curso', '')}. "
            f"Nombre: {row.get('nombre_curso', '')}. "
            f"Categoría: {row.get('categoria', '')}. "
            f"Nivel: {row.get('nivel', '')}. "
            f"Duración: {row.get('duracion_horas', '')} horas. "
            f"Modalidad: {row.get('modalidad', '')}. "
            f"Costo: {row.get('costo_mxn', '')} MXN. "
            f"Requisitos previos: {row.get('requisitos_previos', '')}. "
            f"Tipo de certificado: {row.get('tipo_certificado', '')}. "
            f"Estado: {row.get('estado', '')}."
        )
        rows.append(course_info)

    return "\n".join(rows)