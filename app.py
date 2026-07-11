import hmac
import html
import os
from pathlib import Path
from textwrap import dedent

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
ASSETS_DIR = Path("assets")
NOX_IMAGE_PATH = ASSETS_DIR / "nox_edubot.png"

WELCOME_MESSAGE = (
    "¡Hola! Soy EduBot Knowledge Agent, tu asistente inteligente de "
    "EduNova Academy. Estoy aquí para ayudarte a consultar información "
    "sobre cursos, certificados, becas, pagos, reembolsos, evaluaciones, "
    "soporte técnico y reglamento académico. Escribe tu pregunta y buscaré "
    "la respuesta en la base de conocimiento cargada."
)


def compact_html(content: str) -> str:
    """
    Elimina líneas vacías e indentación de bloques HTML para evitar
    que Streamlit Markdown los interprete como bloques de código.
    """
    return "".join(
        line.strip()
        for line in dedent(content).splitlines()
        if line.strip()
    )


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
    Inicializa el estado persistente de la aplicación.
    """
    defaults = {
        "admin_authenticated": False,
        "last_question": "",
        "last_answer": "",
        "question_input": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


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
    Muestra ejemplos y métricas de la base de conocimiento.
    """
    st.sidebar.divider()
    st.sidebar.markdown("### 💡 Ejemplos de preguntas")

    examples = [
        "¿Cómo puedo obtener mi certificado?",
        "¿Cuánto tiempo tengo para pedir un reembolso?",
        "¿Qué cursos son de nivel principiante?",
        "¿Cuánto cuesta Python Básico?",
        "¿Qué requisitos necesito para solicitar una beca?",
    ]

    examples_html = "".join(
        (
            '<div style="display:flex; gap:10px; margin:14px 0; '
            'line-height:1.45;">'
            '<span style="color:#a85cff;">●</span>'
            f'<span>{html.escape(example)}</span>'
            "</div>"
        )
        for example in examples
    )

    st.sidebar.markdown(
        examples_html,
        unsafe_allow_html=True,
    )

    knowledge_note_html = compact_html(
        """
        <div style="
            margin-top: 1.4rem;
            padding: 1rem;
            border-radius: 14px;
            border: 1px solid rgba(156, 77, 255, 0.18);
            background: rgba(255,255,255,0.025);
            color: rgba(235,232,255,0.78);
            line-height: 1.5;
        ">
            ✨ EduBot utiliza la base de conocimiento oficial
            de EduNova Academy.
        </div>
        """
    )

    st.sidebar.markdown(
        knowledge_note_html,
        unsafe_allow_html=True,
    )

    if uploaded_file_paths:
        st.sidebar.divider()

        metric_col_1, metric_col_2 = st.sidebar.columns(2)

        with metric_col_1:
            st.metric(
                "Documentos",
                len(uploaded_file_paths),
            )

        with metric_col_2:
            st.metric(
                "Fragmentos",
                len(chunks) if chunks is not None else 0,
            )


def show_admin_csv_preview(csv_tables):
    """
    Muestra la vista previa del catálogo únicamente al administrador.
    """
    if not is_admin_authenticated() or not csv_tables:
        return

    title_html = compact_html(
        """
        <div class="admin-section-title">
            <h2>🔐 Vista administrativa de archivos CSV</h2>
        </div>
        """
    )

    st.markdown(
        title_html,
        unsafe_allow_html=True,
    )

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


def apply_custom_styles():
    """
    Aplica la apariencia visual de EduBot.
    """
    styles_html = dedent(
        """
        <style>
        :root {
            --edubot-bg: #0d1019;
            --edubot-surface: #141824;
            --edubot-surface-soft: #1b2030;
            --edubot-border: rgba(159, 110, 255, 0.24);
            --edubot-purple: #9c4dff;
            --edubot-purple-light: #c17cff;
            --edubot-cyan: #35d5e6;
            --edubot-cyan-dark: #1fb9cb;
            --edubot-lime: #9cff4f;
            --edubot-lime-soft: #c2ff78;
            --edubot-pink: #de3af2;
            --edubot-text: #f7f4ff;
            --edubot-muted: #aaa7c5;
        }

        html,
        body,
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(
                    circle at 82% 18%,
                    rgba(112, 45, 190, 0.15),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 42% 75%,
                    rgba(37, 208, 228, 0.08),
                    transparent 30%
                ),
                linear-gradient(
                    135deg,
                    #0b0e16 0%,
                    #111521 52%,
                    #0b0e16 100%
                );
            color: var(--edubot-text);
        }

        [data-testid="stMain"] {
            background: transparent;
        }

        .block-container {
            max-width: 1500px;
            padding-top: 2.4rem;
            padding-bottom: 3rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        footer {
            visibility: hidden;
        }

        [data-testid="stSidebar"] {
            min-width: 295px;
            max-width: 430px;
            background:
                linear-gradient(
                    180deg,
                    rgba(22, 25, 38, 0.98),
                    rgba(14, 17, 27, 0.98)
                );
            border-right: 1px solid rgba(156, 77, 255, 0.20);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.4rem;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #ffffff;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.10);
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(156, 77, 255, 0.22);
            border-radius: 16px;
            overflow: hidden;
        }

        [data-testid="stSidebar"] [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.035);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 0.8rem;
        }

        div[data-testid="stTextInput"] input {
            min-height: 58px;
            border-radius: 999px;
            border: 1px solid rgba(53, 213, 230, 0.45);
            background:
                linear-gradient(
                    90deg,
                    rgba(34, 187, 204, 0.28),
                    rgba(53, 213, 230, 0.18)
                );
            color: white;
            font-size: 1.03rem;
            padding-left: 1.45rem;
            box-shadow:
                inset 0 0 0 1px rgba(255, 255, 255, 0.025),
                0 10px 30px rgba(16, 190, 211, 0.08);
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: rgba(240, 252, 255, 0.62);
        }

        div[data-testid="stTextInput"] input:focus {
            border-color: var(--edubot-cyan);
            box-shadow:
                0 0 0 2px rgba(53, 213, 230, 0.12),
                0 10px 35px rgba(53, 213, 230, 0.12);
        }

        div[data-testid="stTextInput"] label {
            display: none;
        }

        div.stButton > button,
        div[data-testid="stFormSubmitButton"] > button {
            min-height: 54px;
            border: none;
            border-radius: 999px;
            padding-left: 1.8rem;
            padding-right: 1.8rem;
            font-weight: 800;
            color: white;
            background: linear-gradient(135deg, #a83bff, #e43cea);
            box-shadow: 0 12px 30px rgba(213, 50, 239, 0.22);
            transition:
                transform 0.18s ease,
                box-shadow 0.18s ease,
                filter 0.18s ease;
        }

        div.stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            border: none;
            color: white;
            transform: translateY(-2px);
            filter: brightness(1.08);
            box-shadow: 0 15px 38px rgba(213, 50, 239, 0.32);
        }

        div.stButton > button:active,
        div[data-testid="stFormSubmitButton"] > button:active {
            transform: translateY(0);
        }

        [data-testid="stSidebar"] div.stButton > button,
        [data-testid="stSidebar"]
        div[data-testid="stFormSubmitButton"] > button {
            border-radius: 11px;
            min-height: 44px;
            background: rgba(255, 255, 255, 0.035);
            border: 1px solid rgba(193, 124, 255, 0.40);
            box-shadow: none;
        }

        [data-testid="stSidebar"] div.stButton > button:hover,
        [data-testid="stSidebar"]
        div[data-testid="stFormSubmitButton"] > button:hover {
            background: rgba(156, 77, 255, 0.15);
            border: 1px solid rgba(193, 124, 255, 0.70);
        }

        .edubot-hero {
            margin-bottom: 1.35rem;
        }

        .edubot-logo {
            width: 48px;
            height: 48px;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            border-radius: 14px;
            background: linear-gradient(
                135deg,
                rgba(116, 255, 77, 0.9),
                rgba(53, 213, 230, 0.9) 50%,
                rgba(226, 52, 239, 0.95)
            );
            box-shadow: 0 12px 34px rgba(108, 58, 255, 0.25);
        }

        .edubot-title {
            font-size: clamp(2.55rem, 5vw, 5.1rem);
            line-height: 0.98;
            letter-spacing: -0.055em;
            margin: 0;
            color: #ffffff;
            font-weight: 760;
        }

        .edubot-title-gradient {
            background: linear-gradient(
                90deg,
                #3ee7f3 0%,
                #68eab0 42%,
                #ffffff 75%
            );
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }

        .edubot-subtitle {
            margin-top: 1.3rem;
            margin-bottom: 1rem;
            color: #aaa5d0;
            font-size: 1.25rem;
            font-weight: 600;
        }

        .edubot-chat-area {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin-top: 1.5rem;
            margin-bottom: 1.35rem;
        }

        .edubot-user-row {
            display: flex;
            justify-content: flex-end;
        }

        .edubot-user-bubble {
            width: min(61%, 650px);
            background: linear-gradient(135deg, #47dcea, #2bc4db);
            color: #06181b;
            padding: 1rem 1.5rem;
            border-radius: 999px;
            text-align: right;
            font-size: 1.05rem;
            font-weight: 650;
            box-shadow: 0 15px 40px rgba(38, 201, 219, 0.14);
        }

        .edubot-assistant-row {
            display: flex;
            align-items: flex-start;
            gap: 0.9rem;
        }

        .edubot-avatar {
            flex: 0 0 54px;
            width: 54px;
            height: 54px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 0.25rem;
            border-radius: 50%;
            border: 2px solid var(--edubot-lime);
            background: rgba(13, 18, 27, 0.96);
            box-shadow: 0 12px 30px rgba(156, 255, 79, 0.12);
            font-size: 1.65rem;
        }

        .edubot-assistant-bubble {
            width: min(84%, 880px);
            background: linear-gradient(135deg, #a4ff50, #c2ff78);
            color: #132006;
            padding: 1.45rem 1.7rem;
            border-radius: 28px;
            font-size: 1.07rem;
            line-height: 1.58;
            box-shadow: 0 18px 45px rgba(133, 255, 66, 0.13);
        }

        .edubot-source-note {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.45rem;
            margin-top: 0.8rem;
            color: rgba(205, 200, 234, 0.72);
            font-size: 0.83rem;
            text-align: center;
        }

        .nox-caption {
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
            margin-top: 0.2rem;
            margin-bottom: 1rem;
            padding: 0.6rem 0.95rem;
            border: 1px solid rgba(193, 124, 255, 0.24);
            border-radius: 999px;
            background: rgba(17, 21, 32, 0.78);
            color: rgba(238, 232, 255, 0.82);
            font-size: 0.8rem;
            text-align: center;
            backdrop-filter: blur(10px);
        }

        [data-testid="stImage"] {
            display: flex;
            justify-content: center;
            align-items: flex-start;
            margin-top: 0;
        }

        [data-testid="stImage"] img {
            display: block;
            width: 100%;
            max-width: 420px;
            height: auto;
            object-fit: contain;
            margin: 0 auto;
            filter:
                drop-shadow(0 26px 50px rgba(0, 0, 0, 0.48));
        }

        .admin-section-title {
            margin-top: 2rem;
            padding-top: 1.4rem;
            border-top: 1px solid rgba(255, 255, 255, 0.11);
        }

        [data-testid="stExpander"] {
            border-radius: 14px;
            border: 1px solid rgba(156, 77, 255, 0.19);
            background: rgba(255, 255, 255, 0.018);
        }

        @media (max-width: 1100px) {
            .block-container {
                padding-left: 1.5rem;
                padding-right: 1.5rem;
            }

            .edubot-user-bubble {
                width: 80%;
            }

            .edubot-assistant-bubble {
                width: 92%;
            }
        }

        @media (max-width: 760px) {
            .block-container {
                padding-top: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .edubot-title {
                font-size: 2.55rem;
            }

            .edubot-user-bubble {
                width: 95%;
            }

            .edubot-assistant-bubble {
                width: 100%;
                padding: 1.1rem 1.25rem;
            }

            .edubot-avatar {
                display: none;
            }

        }
        </style>
        """
    ).strip()

    st.markdown(
        styles_html,
        unsafe_allow_html=True,
    )


def render_hero():
    """
    Renderiza el encabezado principal de EduBot.
    """
    hero_html = compact_html(
        """
        <section class="edubot-hero">
            <div class="edubot-logo">📚</div>

            <h1 class="edubot-title">
                Hola, soy<br>
                <span class="edubot-title-gradient">
                    EduBot Knowledge Agent
                </span>
            </h1>

            <p class="edubot-subtitle">
                Pregunta tus dudas, estoy aquí para ayudarte.
            </p>
        </section>
        """
    )

    st.markdown(
        hero_html,
        unsafe_allow_html=True,
    )


def render_chat_message(
    question: str = "",
    answer: str = "",
):
    """
    Renderiza las burbujas de conversación.
    """
    safe_question = html.escape(question.strip())
    safe_answer = html.escape(
        answer.strip() if answer else WELCOME_MESSAGE
    ).replace("\n", "<br>")

    question_html = ""

    if safe_question:
        question_html = compact_html(
            f"""
            <div class="edubot-user-row">
                <div class="edubot-user-bubble">
                    {safe_question}
                </div>
            </div>
            """
        )

    chat_html = compact_html(
        f"""
        <div class="edubot-chat-area">
            {question_html}

            <div class="edubot-assistant-row">
                <div class="edubot-avatar">🤖</div>

                <div class="edubot-assistant-bubble">
                    {safe_answer}
                </div>
            </div>
        </div>
        """
    )

    st.markdown(
        chat_html,
        unsafe_allow_html=True,
    )


def render_nox():
    """
    Muestra a Nox en el panel derecho.
    """
    caption_html = compact_html(
        """
        <div class="nox-caption">
            Nox, asistente de EduBot ✨
        </div>
        """
    )

    st.markdown(
        caption_html,
        unsafe_allow_html=True,
    )

    if NOX_IMAGE_PATH.exists():
        st.image(
            str(NOX_IMAGE_PATH),
            width="stretch",
        )
    else:
        st.info(
            "Agrega la imagen de Nox en "
            "`assets/nox_edubot.png`."
        )


def render_source_note():
    """
    Indica que las respuestas proceden de los documentos cargados.
    """
    source_html = compact_html(
        """
        <div class="edubot-source-note">
            🔒 Las respuestas provienen de la base de conocimiento
            de EduNova Academy.
        </div>
        """
    )

    st.markdown(
        source_html,
        unsafe_allow_html=True,
    )


def main():
    """
    Punto de entrada principal de EduBot.
    """
    initialize_session_state()
    ensure_upload_dir()
    apply_custom_styles()

    # Sidebar pública y administrativa.
    show_admin_login()
    show_document_management()

    uploaded_file_paths = list_uploaded_files()

    chunks = []
    chunk_embeddings = []
    csv_tables = []

    knowledge_base_error = None

    if uploaded_file_paths:
        try:
            file_paths_as_strings = [
                str(path)
                for path in uploaded_file_paths
            ]

            (
                chunks,
                chunk_embeddings,
                csv_tables,
            ) = load_knowledge_base(file_paths_as_strings)

        except (
            ValueError,
            FileNotFoundError,
        ) as error:
            knowledge_base_error = str(error)

        except Exception as error:
            knowledge_base_error = (
                "Ocurrió un error al cargar la base de conocimiento."
            )

            if is_admin_authenticated():
                st.sidebar.exception(error)

    show_public_sidebar_information(
        uploaded_file_paths=uploaded_file_paths,
        chunks=chunks,
    )

    # Estructura principal:
    # izquierda = chatbot
    # derecha = Nox
    chatbot_column, nox_column = st.columns(
        [2.75, 1.25],
        gap="medium",
        vertical_alignment="top",
    )

    with chatbot_column:
        render_hero()

        render_chat_message(
            question=st.session_state.last_question,
            answer=st.session_state.last_answer,
        )

        with st.form(
            "edubot_question_form",
            clear_on_submit=True,
        ):
            input_column, button_column = st.columns(
                [4.6, 1.25],
                gap="small",
                vertical_alignment="bottom",
            )

            with input_column:
                question = st.text_input(
                    "Pregunta",
                    placeholder="💬 Ingresa tu pregunta",
                    key="question_input",
                )

            with button_column:
                submitted = st.form_submit_button(
                    "Consultar →",
                    width="stretch",
                )

        render_source_note()

        if knowledge_base_error:
            st.error(knowledge_base_error)

        if not uploaded_file_paths:
            st.warning(
                "La base de conocimiento no contiene documentos "
                "disponibles. El administrador debe cargar archivos "
                "PDF o CSV."
            )

        if submitted:
            clean_question = question.strip()

            if not clean_question:
                st.warning(
                    "Escribe una pregunta antes de consultar. "
                    "El bot no lee mentes, todavía."
                )

            elif is_greeting(clean_question):
                st.session_state.last_question = clean_question
                st.session_state.last_answer = get_welcome_message()
                st.rerun()

            elif not uploaded_file_paths:
                st.session_state.last_question = clean_question
                st.session_state.last_answer = (
                    "No puedo consultar información porque la base "
                    "de conocimiento está vacía."
                )
                st.rerun()

            elif knowledge_base_error:
                st.error(
                    "La base de conocimiento no pudo cargarse "
                    "correctamente."
                )

            else:
                with st.spinner(
                    "EduBot está consultando la base de conocimiento..."
                ):
                    try:
                        answer = answer_question(
                            question=clean_question,
                            chunks=chunks,
                            chunk_embeddings=chunk_embeddings,
                            csv_tables=csv_tables,
                        )

                    except Exception as error:
                        st.error(
                            "Ocurrió un error al generar la respuesta."
                        )

                        if is_admin_authenticated():
                            st.exception(error)

                    else:
                        st.session_state.last_question = clean_question
                        st.session_state.last_answer = answer
                        st.rerun()

        show_admin_csv_preview(csv_tables)

    with nox_column:
        render_nox()


if __name__ == "__main__":
    main()
