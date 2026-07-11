import hmac
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.chatbot import generate_answer, get_welcome_message, is_greeting
from src.document_loader import csv_to_text, load_csv_data, load_pdf_text
from src.knowledge_base import (
    find_course_catalog_answer,
    generate_chunk_embeddings,
    load_embedding_model,
    search_relevant_chunks_semantic,
    split_text_into_chunks,
)


# Carga las variables del archivo .env durante el desarrollo local.
load_dotenv()


UPLOAD_DIR = Path("data/uploads")
ALLOWED_EXTENSIONS = {".pdf", ".csv"}


st.set_page_config(
    page_title="EduBot Knowledge Agent",
    page_icon="📚",
    layout="wide",
)


@st.cache_resource
def get_embedding_model():
    """
    Carga el modelo de embeddings una sola vez durante la ejecución.
    """
    return load_embedding_model()


def initialize_session_state():
    """
    Inicializa las variables utilizadas para conservar la sesión
    administrativa entre las recargas de Streamlit.
    """
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False


def is_admin_authenticated() -> bool:
    """
    Indica si el administrador inició sesión correctamente.
    """
    return bool(st.session_state.get("admin_authenticated", False))


def authenticate_admin(password: str) -> bool:
    """
    Compara la contraseña enviada con ADMIN_PASSWORD.

    Se utiliza hmac.compare_digest para evitar una comparación directa
    entre cadenas.
    """
    configured_password = os.getenv("ADMIN_PASSWORD", "")

    if not configured_password:
        return False

    return hmac.compare_digest(
        password.encode("utf-8"),
        configured_password.encode("utf-8"),
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
        file
        for file in UPLOAD_DIR.iterdir()
        if file.is_file() and file.suffix.lower() in ALLOWED_EXTENSIONS
    ]

    return sorted(files)


def save_uploaded_files(uploaded_files):
    """
    Guarda archivos PDF o CSV subidos por el administrador.

    Path(...).name elimina posibles rutas incluidas en el nombre
    y conserva únicamente el nombre final del archivo.
    """
    ensure_upload_dir()

    saved_files = []

    for uploaded_file in uploaded_files:
        safe_filename = Path(uploaded_file.name).name
        extension = Path(safe_filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            continue

        file_path = UPLOAD_DIR / safe_filename

        with open(file_path, "wb") as file:
            file.write(uploaded_file.getbuffer())

        saved_files.append(safe_filename)

    return saved_files


def delete_file(file_path: Path) -> bool:
    """
    Elimina un archivo de la base de conocimiento.
    """
    try:
        resolved_upload_dir = UPLOAD_DIR.resolve()
        resolved_file = file_path.resolve()

        # Impide eliminar archivos fuera de data/uploads.
        if resolved_file.parent != resolved_upload_dir:
            return False

        if (
            resolved_file.exists()
            and resolved_file.is_file()
            and resolved_file.suffix.lower() in ALLOWED_EXTENSIONS
        ):
            resolved_file.unlink()
            return True

        return False

    except OSError:
        return False


@st.cache_data(max_entries=10)
def load_knowledge_base(file_paths):
    """
    Carga y procesa los archivos PDF y CSV disponibles.

    Devuelve:
    - Fragmentos de texto.
    - Embeddings de los fragmentos.
    - Tablas CSV.
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

    embedding_model = get_embedding_model()
    chunk_embeddings = generate_chunk_embeddings(
        chunks,
        embedding_model,
    )

    return chunks, chunk_embeddings, csv_tables


def show_admin_login():
    """
    Muestra un acceso administrativo discreto en la barra lateral.

    El chatbot continúa siendo público. La contraseña solo protege
    las funciones de gestión documental.
    """
    with st.sidebar.expander("🔐 Acceso administrativo"):
        if is_admin_authenticated():
            st.success("Sesión administrativa activa.")

            if st.button(
                "Cerrar sesión administrativa",
                key="admin_logout",
                width="stretch",
            ):
                st.session_state.admin_authenticated = False
                st.rerun()

            return

        with st.form("admin_login_form", clear_on_submit=True):
            password = st.text_input(
                "Contraseña de administrador",
                type="password",
                placeholder="Escribe la contraseña",
            )

            submitted = st.form_submit_button(
                "Ingresar",
                width="stretch",
            )

        if submitted:
            if not os.getenv("ADMIN_PASSWORD"):
                st.error(
                    "No se configuró ADMIN_PASSWORD en el servidor."
                )

            elif authenticate_admin(password):
                st.session_state.admin_authenticated = True
                st.success("Acceso autorizado.")
                st.rerun()

            else:
                st.error("Contraseña incorrecta.")


def show_document_management():
    """
    Muestra las funciones exclusivas del administrador:
    subir, listar, eliminar y recargar documentos.
    """
    if not is_admin_authenticated():
        return

    st.sidebar.divider()
    st.sidebar.header("📂 Gestión de documentos")

    uploaded_files = st.sidebar.file_uploader(
        "Subir archivos PDF o CSV",
        type=["pdf", "csv"],
        accept_multiple_files=True,
        key="admin_file_uploader",
    )

    if uploaded_files:
        if st.sidebar.button(
            "Guardar archivos subidos",
            key="save_uploaded_files",
            width="stretch",
        ):
            saved_files = save_uploaded_files(uploaded_files)

            if saved_files:
                st.cache_data.clear()

                st.sidebar.success(
                    f"Se guardaron {len(saved_files)} archivo(s)."
                )

                st.rerun()

            else:
                st.sidebar.warning(
                    "No se encontró ningún archivo PDF o CSV válido."
                )

    available_files = list_uploaded_files()

    st.sidebar.subheader("Archivos disponibles")

    if not available_files:
        st.sidebar.warning("No hay archivos cargados.")

    else:
        for file_path in available_files:
            name_column, delete_column = st.sidebar.columns([5, 1])

            with name_column:
                st.caption(file_path.name)

            with delete_column:
                if st.button(
                    "🗑️",
                    key=f"delete_{file_path.name}",
                    help=f"Eliminar {file_path.name}",
                ):
                    if delete_file(file_path):
                        st.cache_data.clear()
                        st.sidebar.success(
                            f"Archivo eliminado: {file_path.name}"
                        )
                        st.rerun()

                    else:
                        st.sidebar.error(
                            "No fue posible eliminar el archivo."
                        )

    if st.sidebar.button(
        "Recargar base de conocimiento",
        key="reload_knowledge_base",
        width="stretch",
    ):
        st.cache_data.clear()
        st.sidebar.success(
            "Base de conocimiento recargada."
        )
        st.rerun()


def show_public_sidebar_information(
    uploaded_file_paths,
    chunks=None,
):
    """
    Muestra información útil para cualquier visitante,
    sin exponer controles administrativos.
    """
    st.sidebar.divider()
    st.sidebar.header("💡 Ejemplos de preguntas")

    st.sidebar.write(
        "• ¿Cómo puedo obtener mi certificado?"
    )
    st.sidebar.write(
        "• ¿Cuánto tiempo tengo para pedir un reembolso?"
    )
    st.sidebar.write(
        "• ¿Qué cursos son de nivel principiante?"
    )
    st.sidebar.write(
        "• ¿Cuánto cuesta Python Básico?"
    )
    st.sidebar.write(
        "• ¿Qué requisitos necesito para solicitar una beca?"
    )

    if uploaded_file_paths:
        st.sidebar.divider()
        st.sidebar.metric(
            "Documentos disponibles",
            len(uploaded_file_paths),
        )

        if chunks is not None:
            st.sidebar.metric(
                "Fragmentos procesados",
                len(chunks),
            )


def show_admin_csv_preview(csv_tables):
    """
    Muestra la vista previa del catálogo únicamente al administrador.
    """
    if not is_admin_authenticated() or not csv_tables:
        return

    st.divider()
    st.subheader("🔐 Vista administrativa de archivos CSV")

    for file_name, dataframe in csv_tables:
        with st.expander(f"Ver contenido de {file_name}"):
            st.dataframe(
                dataframe,
                width="stretch",
            )


def answer_question(
    question,
    chunks,
    chunk_embeddings,
    csv_tables,
):
    """
    Resuelve una pregunta utilizando primero el catálogo estructurado
    y después la búsqueda semántica.
    """
    if is_greeting(question):
        return get_welcome_message()

    catalog_answer = find_course_catalog_answer(
        question,
        csv_tables,
    )

    if catalog_answer:
        return catalog_answer

    embedding_model = get_embedding_model()

    relevant_chunks = search_relevant_chunks_semantic(
        question=question,
        chunks=chunks,
        chunk_embeddings=chunk_embeddings,
        model=embedding_model,
        top_k=4,
        minimum_score=0.25,
    )

    return generate_answer(
        question,
        relevant_chunks,
    )


def main():
    """
    Punto de entrada principal de EduBot.
    """
    initialize_session_state()
    ensure_upload_dir()

    st.title("📚 EduBot Knowledge Agent")
    st.success(get_welcome_message())

    # El acceso administrativo es opcional.
    # Cualquier visitante puede usar el chatbot sin iniciar sesión.
    show_admin_login()
    show_document_management()

    uploaded_file_paths = list_uploaded_files()

    question = st.text_input(
        "Escribe tu pregunta:",
        placeholder="Ejemplo: ¿Qué cursos pertenecen a Cloud Computing?",
    )

    if not uploaded_file_paths:
        show_public_sidebar_information(
            uploaded_file_paths=uploaded_file_paths,
        )

        st.warning(
            "La base de conocimiento no contiene documentos disponibles. "
            "Por favor, inténtalo nuevamente más tarde."
        )

        if st.button("Consultar", width="content"):
            if not question.strip():
                st.warning(
                    "Escribe una pregunta antes de consultar. "
                    "El bot no lee mentes, todavía."
                )

            elif is_greeting(question):
                st.subheader("Respuesta de EduBot")
                st.write(get_welcome_message())

            else:
                st.warning(
                    "EduBot no puede responder porque la base "
                    "de conocimiento está vacía."
                )

        return

    try:
        file_paths_as_strings = [
            str(path)
            for path in uploaded_file_paths
        ]

        chunks, chunk_embeddings, csv_tables = load_knowledge_base(
            file_paths_as_strings
        )

        show_public_sidebar_information(
            uploaded_file_paths=uploaded_file_paths,
            chunks=chunks,
        )

        if st.button("Consultar"):
            if not question.strip():
                st.warning(
                    "Escribe una pregunta antes de consultar. "
                    "El bot no lee mentes, todavía."
                )

            else:
                with st.spinner(
                    "EduBot está consultando la base de conocimiento..."
                ):
                    answer = answer_question(
                        question=question,
                        chunks=chunks,
                        chunk_embeddings=chunk_embeddings,
                        csv_tables=csv_tables,
                    )

                st.subheader("Respuesta de EduBot")
                st.write(answer)

        # La tabla completa no se muestra al público.
        show_admin_csv_preview(csv_tables)

    except ValueError as error:
        st.error(str(error))

    except FileNotFoundError as error:
        st.error(str(error))

    except Exception as error:
        st.error(
            "Ocurrió un error al ejecutar la aplicación."
        )

        # Solo el administrador ve el detalle técnico completo.
        if is_admin_authenticated():
            st.exception(error)
        else:
            st.info(
                "Inténtalo nuevamente o contacta al administrador."
            )


if __name__ == "__main__":
    main()
