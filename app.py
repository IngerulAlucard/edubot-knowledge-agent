from pathlib import Path

import streamlit as st

from src.document_loader import load_pdf_text, load_csv_data, csv_to_text
from src.knowledge_base import (
    split_text_into_chunks,
    search_relevant_chunks,
    find_course_catalog_answer
)

from src.chatbot import generate_answer, is_greeting, get_welcome_message


UPLOAD_DIR = Path("data/uploads")
ALLOWED_EXTENSIONS = [".pdf", ".csv"]


st.set_page_config(
    page_title="EduBot Knowledge Agent",
    page_icon="📚",
    layout="wide"
)


def ensure_upload_dir():
    """
    Crea la carpeta de archivos si no existe.
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def list_uploaded_files():
    """
    Lista los archivos PDF y CSV disponibles en la carpeta de uploads.
    """
    ensure_upload_dir()

    files = [
        file for file in UPLOAD_DIR.iterdir()
        if file.is_file() and file.suffix.lower() in ALLOWED_EXTENSIONS
    ]

    return sorted(files)


def save_uploaded_files(uploaded_files):
    """
    Guarda los archivos subidos por el usuario en la carpeta de uploads.
    """
    ensure_upload_dir()

    for uploaded_file in uploaded_files:
        file_path = UPLOAD_DIR / uploaded_file.name

        with open(file_path, "wb") as file:
            file.write(uploaded_file.getbuffer())


def delete_file(file_path: Path):
    """
    Elimina un archivo seleccionado.
    """
    if file_path.exists() and file_path.is_file():
        file_path.unlink()


@st.cache_data
def load_knowledge_base(file_paths):
    """
    Carga y procesa los archivos PDF y CSV disponibles.
    """
    full_text_parts = []
    csv_tables = []

    for file_path_str in file_paths:
        file_path = Path(file_path_str)
        extension = file_path.suffix.lower()

        if extension == ".pdf":
            pdf_text = load_pdf_text(str(file_path))
            full_text_parts.append(
                f"\nDOCUMENTO PDF: {file_path.name}\n{pdf_text}"
            )

        elif extension == ".csv":
            dataframe = load_csv_data(str(file_path))
            csv_text = csv_to_text(dataframe)

            full_text_parts.append(
                f"\nCATÁLOGO CSV: {file_path.name}\n{csv_text}"
            )

            csv_tables.append((file_path.name, dataframe))

    full_text = "\n\n".join(full_text_parts)
    chunks = split_text_into_chunks(full_text)

    return chunks, csv_tables


def main():
    ensure_upload_dir()

    st.title("📚 EduBot Knowledge Agent")

    st.success(get_welcome_message())

    st.sidebar.header("📂 Gestión de documentos")

    uploaded_files = st.sidebar.file_uploader(
        "Subir archivos PDF o CSV",
        type=["pdf", "csv"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.sidebar.button("Guardar archivos subidos"):
            save_uploaded_files(uploaded_files)
            st.cache_data.clear()
            st.sidebar.success("Archivos guardados correctamente.")
            st.rerun()

    uploaded_file_paths = list_uploaded_files()

    st.sidebar.subheader("Archivos disponibles")

    if not uploaded_file_paths:
        st.sidebar.warning("No hay archivos cargados.")
    else:
        for file_path in uploaded_file_paths:
            col1, col2 = st.sidebar.columns([3, 1])

            with col1:
                st.write(file_path.name)

            with col2:
                if st.button("🗑️", key=f"delete_{file_path.name}"):
                    delete_file(file_path)
                    st.cache_data.clear()
                    st.sidebar.success(f"Archivo eliminado: {file_path.name}")
                    st.rerun()

    if st.sidebar.button("Recargar base de conocimiento"):
        st.cache_data.clear()
        st.sidebar.success("Base de conocimiento recargada.")
        st.rerun()

    uploaded_file_paths = list_uploaded_files()

    question = st.text_input(
        "Escribe tu pregunta:",
        placeholder="Ejemplo: ¿Qué cursos pertenecen a Cloud Computing?"
    )

    if not uploaded_file_paths:
        st.warning(
            "No hay documentos disponibles. Sube al menos un archivo PDF o CSV "
            "para que EduBot pueda responder preguntas sobre la base de conocimiento."
        )

        if st.button("Consultar"):
            if question.strip():
                if is_greeting(question):
                    st.subheader("Respuesta de EduBot")
                    st.write(get_welcome_message())
                else:
                    st.warning(
                        "Primero debes subir documentos para que EduBot pueda consultar información."
                    )
            else:
                st.warning("Escribe una pregunta antes de consultar. El bot no lee mentes, todavía.")

        return

    try:
        file_paths_as_strings = [str(path) for path in uploaded_file_paths]
        chunks, csv_tables = load_knowledge_base(file_paths_as_strings)

        with st.sidebar:
            st.metric("Archivos cargados", len(uploaded_file_paths))
            st.metric("Fragmentos procesados", len(chunks))

            st.subheader("Ejemplos de preguntas")
            st.write("• ¿Cómo puedo obtener mi certificado?")
            st.write("• ¿Cuánto tiempo tengo para pedir un reembolso?")
            st.write("• ¿Qué cursos son de nivel principiante?")
            st.write("• ¿Cuánto cuesta Python Básico?")
            st.write("• ¿Qué requisitos necesito para solicitar una beca?")

        if st.button("Consultar"):
            if question.strip():
                if is_greeting(question):
                    answer = get_welcome_message()
                else:
                    with st.spinner("EduBot está consultando la base de conocimiento..."):
                        catalog_answer = find_course_catalog_answer(question, csv_tables)

                        if catalog_answer:
                            answer = catalog_answer
                        else:
                            relevant_chunks = search_relevant_chunks(question, chunks)
                            answer = generate_answer(question, relevant_chunks)

                st.subheader("Respuesta de EduBot")
                st.write(answer)

            else:
                st.warning("Escribe una pregunta antes de consultar. El bot no lee mentes, todavía.")

        if csv_tables:
            st.subheader("Vista previa de archivos CSV")

            for file_name, dataframe in csv_tables:
                with st.expander(f"Ver contenido de {file_name}"):
                    st.dataframe(dataframe)

    except ValueError as error:
        st.error(str(error))

    except FileNotFoundError as error:
        st.error(str(error))

    except Exception as error:
        st.error("Ocurrió un error al ejecutar la aplicación.")
        st.exception(error)


if __name__ == "__main__":
    main()