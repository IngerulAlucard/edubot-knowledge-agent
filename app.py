import streamlit as st

from src.document_loader import load_pdf_text, load_csv_data, csv_to_text
from src.knowledge_base import split_text_into_chunks, search_relevant_chunks
from src.chatbot import generate_answer


PDF_PATH = "data/manual_edunova_academy.pdf"
CSV_PATH = "data/catalogo_cursos.csv"


st.set_page_config(
    page_title="EduBot Knowledge Agent",
    page_icon="📚",
    layout="wide"
)


@st.cache_data
def load_knowledge_base():
    """
    Carga y procesa el PDF y el CSV de la base de conocimiento.
    """
    pdf_text = load_pdf_text(PDF_PATH)
    courses_df = load_csv_data(CSV_PATH)
    csv_text = csv_to_text(courses_df)

    full_text = f"""
    DOCUMENTACIÓN INSTITUCIONAL DE EDUNOVA ACADEMY:

    {pdf_text}

    CATÁLOGO DE CURSOS:

    {csv_text}
    """

    chunks = split_text_into_chunks(full_text)

    return chunks, courses_df


def main():
    st.title("📚 EduBot Knowledge Agent")
    st.write(
        "Agente inteligente para consultar la documentación interna de EduNova Academy."
    )

    st.info(
        "Puedes hacer preguntas sobre cursos, certificados, becas, reembolsos, "
        "soporte técnico, pagos, evaluaciones y reglamento académico."
    )

    try:
        chunks, courses_df = load_knowledge_base()

        with st.sidebar:
            st.header("📂 Base de conocimiento")
            st.write("Documento PDF cargado:")
            st.code(PDF_PATH)

            st.write("Catálogo CSV cargado:")
            st.code(CSV_PATH)

            st.metric("Cursos registrados", len(courses_df))
            st.metric("Fragmentos procesados", len(chunks))

            st.subheader("Ejemplos de preguntas")
            st.write("• ¿Cómo puedo obtener mi certificado?")
            st.write("• ¿Cuánto tiempo tengo para pedir un reembolso?")
            st.write("• ¿Qué cursos son de nivel principiante?")
            st.write("• ¿Cuánto cuesta Python Básico?")
            st.write("• ¿Qué requisitos necesito para solicitar una beca?")

        question = st.text_input(
            "Escribe tu pregunta:",
            placeholder="Ejemplo: ¿Qué cursos pertenecen a Cloud Computing?"
        )

        if st.button("Consultar"):
            if question.strip():
                relevant_chunks = search_relevant_chunks(question, chunks)
                answer = generate_answer(question, relevant_chunks)

                st.subheader("Respuesta de EduBot")
                st.write(answer)

                with st.expander("Ver fragmentos consultados"):
                    for index, (score, chunk) in enumerate(relevant_chunks, start=1):
                        st.markdown(f"**Fragmento {index} | Puntuación: {score}**")
                        st.write(chunk)
            else:
                st.warning("Escribe una pregunta antes de consultar. El bot no lee mentes, todavía.")

        st.subheader("Vista previa del catálogo de cursos")
        st.dataframe(courses_df)

    except FileNotFoundError as error:
        st.error(str(error))
        st.warning(
            "Verifica que los archivos manual_edunova_academy.pdf y catalogo_cursos.csv "
            "existan dentro de la carpeta data."
        )

    except Exception as error:
        st.error("Ocurrió un error al ejecutar la aplicación.")
        st.exception(error)


if __name__ == "__main__":
    main()