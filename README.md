# 📚 EduBot Knowledge Agent

EduBot Knowledge Agent es un chatbot desarrollado en Python para responder preguntas sobre la documentación interna de una plataforma educativa ficticia llamada **EduNova Academy**.

La aplicación utiliza documentos PDF y un catálogo de cursos en formato CSV como base de conocimiento. Cualquier visitante puede utilizar el chatbot sin registrarse. Las funciones para subir, eliminar y recargar documentos están protegidas mediante una contraseña administrativa.

---

## 🎯 Objetivo

Desarrollar un agente de inteligencia artificial capaz de procesar documentos educativos para responder preguntas frecuentes de estudiantes y visitantes de forma clara, rápida y basada en información documentada.

---

## 📌 Descripción general del proyecto

EduNova Academy maneja información distribuida en políticas, reglamentos, manuales, guías y catálogos.

Buscar respuestas manualmente en estos documentos puede resultar lento y poco práctico. EduBot centraliza la información y permite consultarla mediante preguntas en lenguaje natural.

El agente puede responder preguntas relacionadas con:

* Cursos disponibles.
* Precio, duración, nivel y modalidad.
* Certificados y constancias.
* Becas.
* Reembolsos.
* Pagos y facturación.
* Evaluaciones.
* Proyectos finales.
* Soporte técnico.
* Reglamento académico.

---

## 🧠 Arquitectura de la solución

EduBot utiliza una arquitectura híbrida con dos mecanismos de respuesta.

### Consultas estructuradas

Las preguntas relacionadas con el catálogo de cursos se procesan directamente con Pandas.

Ejemplos:

* ¿Cuánto cuesta Python Básico?
* ¿Qué cursos son de nivel principiante?
* ¿Qué cursos pertenecen a Cloud Computing?
* ¿Cuál es el curso más barato?
* ¿Hay cursos sincrónicos?

Estas consultas se resuelven aplicando filtros al archivo CSV.

### Consultas documentales

Las preguntas relacionadas con políticas, procedimientos y reglamentos utilizan recuperación semántica mediante embeddings.

```text
Usuario
   ↓
Interfaz Streamlit
   ↓
Pregunta
   ↓
Clasificación de la consulta
   ├── Consulta del catálogo
   │      ↓
   │   Filtros con Pandas
   │      ↓
   │   Respuesta directa
   │
   └── Consulta documental
          ↓
       Embedding de la pregunta
          ↓
       Comparación semántica
          ↓
       Fragmentos relevantes
          ↓
       Construcción del contexto
          ↓
       Cohere
          ↓
       Respuesta generada
```

La documentación técnica ampliada se encuentra en:

```text
docs/arquitectura.md
```

---

## 🔎 Recuperación semántica

EduBot utiliza el modelo:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Este modelo convierte las preguntas y los fragmentos de documentos en vectores numéricos llamados embeddings.

Esto permite encontrar información por significado y no únicamente por coincidencia exacta de palabras.

Por ejemplo:

```text
¿Cómo recupero el dinero que pagué?
```

puede relacionarse con información sobre:

```text
Política de reembolsos
```

aunque la pregunta no incluya exactamente la palabra `reembolso`.

La configuración actual recupera hasta cuatro fragmentos con una puntuación mínima de similitud de `0.25`.

---

## 🔐 Acceso público y administración

El chatbot es público y no requiere inicio de sesión.

Cualquier visitante puede:

* Escribir preguntas.
* Consultar la base de conocimiento.
* Ver respuestas generadas por EduBot.

El panel administrativo está protegido mediante contraseña.

Solo el administrador puede:

* Subir documentos PDF o CSV.
* Eliminar documentos.
* Recargar la base de conocimiento.
* Ver la vista previa completa del catálogo.

La contraseña administrativa se configura mediante la variable de entorno:

```env
ADMIN_PASSWORD=tu_contraseña_administrativa
```

---

## 🛠️ Tecnologías y herramientas utilizadas

| Tecnología                  | Uso                                     |
| --------------------------- | --------------------------------------- |
| Python                      | Lenguaje principal                      |
| Streamlit                   | Interfaz web                            |
| Pandas                      | Procesamiento estructurado del catálogo |
| PyPDF                       | Extracción de texto desde PDF           |
| Sentence Transformers       | Generación de embeddings                |
| NumPy                       | Comparación de vectores                 |
| Cohere                      | Generación de respuestas                |
| python-dotenv               | Carga de variables de entorno           |
| Git                         | Control de versiones                    |
| GitHub                      | Repositorio del proyecto                |
| Oracle Cloud Infrastructure | Plataforma prevista para despliegue     |

---

## 📂 Estructura del repositorio

```text
edubot-knowledge-agent/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── uploads/
├── src/
│   ├── __init__.py
│   ├── document_loader.py
│   ├── knowledge_base.py
│   └── chatbot.py
├── docs/
│   ├── arquitectura.md
│   ├── ejemplos_preguntas.md
│   └── evidencia_deploy.md
└── screenshots/
```

---

## 📄 Componentes principales

### `app.py`

Contiene la interfaz Streamlit y coordina el flujo general.

Se encarga de:

* Mostrar el chatbot.
* Recibir preguntas.
* Gestionar el acceso administrativo.
* Subir y eliminar archivos.
* Cargar la base de conocimiento.
* Mostrar respuestas y errores.

### `src/document_loader.py`

Se encarga de:

* Leer archivos PDF.
* Extraer texto.
* Cargar archivos CSV.
* Convertir el catálogo a texto.

### `src/knowledge_base.py`

Se encarga de:

* Dividir documentos en fragmentos.
* Normalizar texto.
* Generar embeddings.
* Buscar fragmentos relevantes.
* Resolver consultas estructuradas del catálogo.

### `src/chatbot.py`

Se encarga de:

* Detectar saludos.
* Construir el contexto.
* Validar la clave de Cohere.
* Generar respuestas basadas en la documentación.

---

## ✅ Requisitos previos

Para ejecutar el proyecto se necesita:

* Python 3.10 o superior.
* Git.
* Una clave válida de Cohere.
* Conexión a internet.
* Al menos 2 GB de memoria RAM recomendados.

---

## 🚀 Instrucciones para ejecutar el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/IngerulAlucard/edubot-knowledge-agent.git
cd edubot-knowledge-agent
```

### 2. Crear un entorno virtual

```bash
python -m venv .venv
```

### 3. Activar el entorno virtual

En Linux o macOS:

```bash
source .venv/bin/activate
```

En Windows:

```powershell
.venv\Scripts\activate
```

### 4. Instalar las dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Crear el archivo `.env`

En la raíz del proyecto crea un archivo llamado `.env`:

```env
COHERE_API_KEY=tu_clave_de_cohere
ADMIN_PASSWORD=tu_contraseña_administrativa
```

El archivo `.env` no debe subirse a GitHub.

### 6. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación estará disponible normalmente en:

```text
http://localhost:8501
```

---

## 📥 Uso de la aplicación

### Uso público

1. Abrir EduBot en el navegador.
2. Escribir una pregunta.
3. Presionar **Consultar**.
4. Revisar la respuesta.

### Uso administrativo

1. Abrir la sección **Acceso administrativo**.
2. Escribir la contraseña configurada.
3. Subir, eliminar o recargar documentos.
4. Cerrar la sesión al terminar.

---

## 💬 Ejemplos de preguntas que el agente puede responder

### Certificados

```text
¿Cómo puedo obtener mi certificado?
```

```text
¿Cuánto tarda en aparecer mi certificado?
```

### Reembolsos

```text
¿Cuánto tiempo tengo para pedir un reembolso?
```

```text
¿Cómo recupero el dinero que pagué?
```

### Becas

```text
¿Qué requisitos necesito para solicitar una beca?
```

```text
¿Cuánto cubre una beca?
```

### Soporte técnico

```text
¿Qué hago si no puedo iniciar sesión?
```

```text
¿Cómo contacto a soporte técnico?
```

### Evaluaciones

```text
¿Qué calificación necesito para aprobar?
```

```text
¿Cuántos intentos tengo en una evaluación?
```

### Cursos

```text
¿Qué cursos son de nivel principiante?
```

```text
¿Cuánto cuesta Python Básico?
```

```text
¿Qué cursos pertenecen a Cloud Computing?
```

```text
¿Hay cursos sincrónicos?
```

---

## 🤖 Ejemplos de respuestas generadas

### Ejemplo 1: certificado

**Pregunta**

```text
¿Cómo puedo obtener mi certificado?
```

**Respuesta de ejemplo**

Para obtener tu certificado debes completar el contenido obligatorio del curso, aprobar las evaluaciones con la calificación mínima requerida, entregar el proyecto final si aplica, mantener tus datos actualizados y no tener pagos pendientes.

---

### Ejemplo 2: reembolso

**Pregunta**

```text
¿Cómo recupero el dinero que pagué?
```

**Respuesta de ejemplo**

Puedes solicitar un reembolso dentro del plazo establecido en la política. La aprobación depende del avance del curso, la descarga de materiales y la emisión previa de certificados o constancias.

---

### Ejemplo 3: beca

**Pregunta**

```text
¿Qué requisitos necesito para solicitar una beca?
```

**Respuesta de ejemplo**

Debes proporcionar tu nombre completo, correo registrado, curso de interés, motivo de la solicitud, objetivo de aprendizaje y comprobante de estudios o situación laboral si aplica.

---

### Ejemplo 4: curso

**Pregunta**

```text
¿Cuánto cuesta Python Básico?
```

**Respuesta de ejemplo**

El curso Python Básico cuesta 999 MXN.

---

### Ejemplo 5: modalidad

**Pregunta**

```text
¿Hay cursos sincrónicos?
```

**Respuesta de ejemplo**

Según el catálogo actual, no hay cursos con modalidad sincrónica disponibles.

---

## ✔️ Validaciones implementadas

La aplicación valida:

* Que existan documentos.
* Que la pregunta no esté vacía.
* Que los archivos sean PDF o CSV.
* Que el catálogo tenga las columnas necesarias.
* Que exista `COHERE_API_KEY`.
* Que exista `ADMIN_PASSWORD`.
* Que la contraseña administrativa sea correcta.
* Que los archivos se guarden dentro de `data/uploads/`.
* Que existan fragmentos relevantes.
* Que los errores se muestren de forma controlada.

---

## ⚠️ Limitaciones actuales

* No mantiene historial de conversación.
* No utiliza una base vectorial persistente.
* Los embeddings se almacenan en memoria.
* Los documentos se guardan localmente.
* Solo existe una contraseña administrativa compartida.
* No incluye pruebas automatizadas.
* Cohere requiere conexión a internet.

---

## ☁️ Ejecución en OCI

```bash
export COHERE_API_KEY="tu_clave_de_cohere"
export ADMIN_PASSWORD="tu_contraseña_administrativa"

streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port 8501
```

El puerto `8501` debe habilitarse en OCI y en el firewall del sistema operativo.

La evidencia del despliegue se documentará en:

```text
docs/evidencia_deploy.md
```

---

## 👤 Autor

**Îngerul Alucard**

Proyecto desarrollado con fines educativos.