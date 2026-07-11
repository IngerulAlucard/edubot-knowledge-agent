# Arquitectura de EduBot Knowledge Agent

## 1. Descripción general

EduBot Knowledge Agent es una aplicación web desarrollada en Python que permite consultar información educativa mediante preguntas en lenguaje natural.

La solución utiliza documentos PDF y un catálogo CSV como base de conocimiento. Su arquitectura combina procesamiento estructurado con Pandas, recuperación semántica mediante embeddings y generación de respuestas con Cohere.

El chatbot es público. Cualquier visitante puede realizar preguntas sin crear una cuenta. Las funciones para gestionar documentos están restringidas mediante contraseña administrativa.

---

## 2. Tipo de arquitectura

EduBot utiliza una arquitectura modular e híbrida.

Es modular porque separa responsabilidades en distintos archivos.

Es híbrida porque utiliza dos mecanismos de respuesta:

1. Consultas estructuradas mediante Pandas.
2. Consultas documentales mediante embeddings y Cohere.

---

## 3. Diagrama general

```text
Usuario público
   ↓
Interfaz Streamlit
   ↓
Pregunta
   ↓
Clasificación
   ├── Consulta del catálogo
   │      ↓
   │   DataFrame de Pandas
   │      ↓
   │   Aplicación de filtros
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

Administrador
   ↓
Contraseña administrativa
   ↓
Sesión autenticada
   ├── Subir documentos
   ├── Eliminar documentos
   ├── Recargar base
   └── Ver catálogo completo
```

---

## 4. Capas de la solución

### 4.1 Capa de presentación

Archivo:

```text
app.py
```

Responsabilidades:

* Mostrar la interfaz Streamlit.
* Recibir preguntas.
* Mostrar respuestas.
* Mostrar ejemplos de consultas.
* Gestionar la sesión administrativa.
* Mostrar errores y advertencias.
* Ocultar las funciones administrativas al público.

### 4.2 Capa de procesamiento documental

Archivo:

```text
src/document_loader.py
```

Responsabilidades:

* Leer archivos PDF.
* Extraer texto.
* Cargar archivos CSV.
* Convertir el catálogo a texto.
* Validar archivos.

### 4.3 Capa de recuperación

Archivo:

```text
src/knowledge_base.py
```

Responsabilidades:

* Dividir documentos en fragmentos.
* Normalizar texto.
* Cargar el modelo de embeddings.
* Generar embeddings.
* Comparar vectores.
* Seleccionar fragmentos relevantes.
* Resolver consultas del catálogo.

### 4.4 Capa de generación

Archivo:

```text
src/chatbot.py
```

Responsabilidades:

* Detectar saludos.
* Construir el contexto.
* Validar la clave de Cohere.
* Generar la respuesta.
* Informar cuando falta información.

---

## 5. Control de acceso

La aplicación tiene dos niveles funcionales.

### Acceso público

No requiere inicio de sesión.

Los visitantes pueden:

* Escribir preguntas.
* Consultar la base de conocimiento.
* Ver respuestas.
* Ver ejemplos de preguntas.

### Acceso administrativo

Requiere la variable:

```text
ADMIN_PASSWORD
```

El administrador puede:

* Subir documentos.
* Eliminar documentos.
* Recargar la base.
* Ver la vista previa del catálogo.

La sesión administrativa se conserva mediante:

```python
st.session_state.admin_authenticated
```

La contraseña se compara utilizando:

```python
hmac.compare_digest()
```

---

## 6. Gestión de documentos

Los documentos se almacenan en:

```text
data/uploads/
```

Los formatos permitidos son:

```text
.pdf
.csv
```

El flujo es:

```text
Administrador autenticado
   ↓
Selección del archivo
   ↓
Validación de extensión
   ↓
Normalización del nombre
   ↓
Guardado en data/uploads/
   ↓
Limpieza de caché
   ↓
Recarga de la interfaz
```

La aplicación utiliza:

```python
Path(uploaded_file.name).name
```

para evitar que el nombre contenga rutas externas.

La eliminación también valida que el archivo pertenezca directamente a `data/uploads/`.

---

## 7. Procesamiento de PDF

Los documentos PDF se procesan mediante PyPDF.

```text
PDF
   ↓
Lectura de páginas
   ↓
Extracción de texto
   ↓
Unión del contenido
   ↓
Texto completo
```

Los documentos contienen información sobre:

* Certificados.
* Reembolsos.
* Becas.
* Pagos.
* Facturación.
* Evaluaciones.
* Soporte técnico.
* Reglamento.
* Preguntas frecuentes.
* Manuales internos.

---

## 8. Procesamiento del CSV

El catálogo se carga como un DataFrame de Pandas.

Las columnas utilizadas incluyen:

```text
id_curso
nombre_curso
categoria
nivel
duracion_horas
modalidad
costo_mxn
requisitos_previos
tipo_certificado
estado
```

El CSV se utiliza de dos maneras:

1. Como DataFrame para consultas estructuradas.
2. Como texto dentro de la base documental.

---

## 9. División en fragmentos

La función:

```python
split_text_into_chunks()
```

divide el texto en fragmentos de aproximadamente 900 caracteres.

```text
Texto completo
   ↓
Normalización de espacios
   ↓
Fragmentos
   ↓
Lista de chunks
```

El objetivo es evitar enviar todos los documentos al modelo en cada consulta.

---

## 10. Modelo de embeddings

EduBot utiliza:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

El modelo se carga una sola vez mediante:

```python
@st.cache_resource
```

Esto evita volver a descargarlo o cargarlo en cada interacción.

---

## 11. Generación de embeddings

La función:

```python
generate_chunk_embeddings()
```

convierte cada fragmento en un vector numérico.

```text
Fragmentos
   ↓
Sentence Transformer
   ↓
Embeddings normalizados
   ↓
Matriz NumPy
```

Los vectores se generan con:

```python
normalize_embeddings=True
```

y se almacenan como:

```python
np.float32
```

---

## 12. Recuperación semántica

La función:

```python
search_relevant_chunks_semantic()
```

compara el embedding de la pregunta con los embeddings de los fragmentos.

```text
Pregunta
   ↓
Embedding
   ↓
Producto punto
   ↓
Puntuaciones
   ↓
Ordenamiento
   ↓
Fragmentos relevantes
```

La configuración actual es:

```python
top_k=4
minimum_score=0.25
```

Esto significa que se recuperan hasta cuatro fragmentos con una puntuación mínima de `0.25`.

---

## 13. Consultas estructuradas

La función:

```python
find_course_catalog_answer()
```

resuelve preguntas relacionadas con:

* Precio.
* Duración.
* Nivel.
* Categoría.
* Modalidad.
* Certificado.
* Constancia.
* Estado.
* Requisitos.
* Rangos de precio.
* Curso más barato.
* Curso más caro.
* Nombre exacto o parcial.

Flujo:

```text
Pregunta
   ↓
Normalización
   ↓
Detección del filtro
   ↓
Filtro sobre DataFrame
   ↓
Formateo
   ↓
Respuesta directa
```

Estas consultas no utilizan Cohere.

---

## 14. Clasificación de consultas

La aplicación sigue este orden:

```text
Pregunta
   ↓
¿Es un saludo?
   ├── Sí → Respuesta local
   └── No
        ↓
¿Corresponde al catálogo?
   ├── Sí → Pandas
   └── No
        ↓
Embeddings
   ↓
Cohere
```

Primero se detectan saludos. Después se intenta resolver la pregunta con el catálogo. Si no corresponde a una consulta estructurada, se ejecuta la recuperación semántica.

---

## 15. Generación de respuestas

La integración con Cohere se encuentra en:

```text
src/chatbot.py
```

El modelo configurado es:

```text
command-r-08-2024
```

El prompt indica que la respuesta debe:

* Estar en español.
* Utilizar únicamente la base de conocimiento.
* No inventar información.
* Incluir requisitos.
* Incluir plazos.
* Incluir porcentajes.
* Incluir excepciones.
* Informar cuando falta información.

---

## 16. Variables de entorno

La aplicación utiliza:

```env
COHERE_API_KEY=tu_clave_de_cohere
ADMIN_PASSWORD=tu_contraseña_administrativa
```

Durante el desarrollo local se cargan mediante `python-dotenv`.

En producción deben configurarse como variables de entorno del servidor.

---

## 17. Uso de caché

### Modelo de embeddings

```python
@st.cache_resource
```

Evita cargar nuevamente el modelo.

### Base de conocimiento

```python
@st.cache_data(max_entries=10)
```

Almacena temporalmente:

* Texto extraído.
* Fragmentos.
* Embeddings.
* DataFrames.

La caché se limpia cuando:

* Se guarda un archivo.
* Se elimina un archivo.
* Se recarga la base.

---

## 18. Interfaz de Streamlit

La aplicación utiliza:

```python
width="stretch"
```

para componentes que deben ocupar el ancho disponible.

También utiliza:

```python
width="content"
```

para botones ajustados al contenido.

El parámetro antiguo:

```python
use_container_width
```

ya no se utiliza.

---

## 19. Manejo de errores

La aplicación controla:

* Falta de documentos.
* Preguntas vacías.
* PDF inválidos.
* CSV inválidos.
* Archivos fuera del directorio permitido.
* Falta de clave de Cohere.
* Falta de contraseña administrativa.
* Contraseña incorrecta.
* Errores de conexión.
* Consultas sin resultados.
* Fallos inesperados.

Los detalles técnicos completos se muestran únicamente al administrador.

---

## 20. Tecnologías utilizadas

| Tecnología            | Uso                      |
| --------------------- | ------------------------ |
| Python                | Lenguaje principal       |
| Streamlit             | Interfaz web             |
| Pandas                | Consultas estructuradas  |
| PyPDF                 | Procesamiento de PDF     |
| Sentence Transformers | Embeddings               |
| NumPy                 | Similitud vectorial      |
| Cohere                | Generación de respuestas |
| python-dotenv         | Variables de entorno     |
| GitHub                | Control de versiones     |
| OCI                   | Despliegue               |

---

## 21. Estructura del repositorio

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

## 22. Despliegue en OCI

```text
GitHub
   ↓
Clonado en OCI
   ↓
Entorno virtual
   ↓
Dependencias
   ↓
Variables de entorno
   ↓
Descarga del modelo
   ↓
Streamlit
   ↓
Puerto 8501
```

Comando:

```bash
streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port 8501
```

Variables:

```bash
export COHERE_API_KEY="tu_clave_de_cohere"
export ADMIN_PASSWORD="tu_contraseña_administrativa"
```

---

## 23. Limitaciones actuales

* No mantiene historial de conversación.
* No utiliza una base vectorial persistente.
* Los embeddings se almacenan en memoria.
* Los documentos se guardan localmente.
* Solo existe una contraseña administrativa compartida.
* No incluye pruebas automatizadas.
* Cohere requiere conexión a internet.

---

## 24. Mejoras futuras

* Base vectorial persistente.
* Historial conversacional.
* Citas de documentos.
* Registro de actividad administrativa.
* Contraseñas con hash.
* Docker.
* Pruebas unitarias.
* GitHub Actions.
* Object Storage.
* Monitoreo.

---

## 25. Conclusión

EduBot Knowledge Agent utiliza una arquitectura híbrida que combina:

* Pandas para consultas estructuradas.
* Sentence Transformers para recuperación semántica.
* NumPy para similitud vectorial.
* Cohere para generación de respuestas.
* Streamlit para la interfaz.
* Un panel administrativo protegido para gestionar documentos.

Esta separación permite mantener el chatbot abierto al público sin exponer las funciones administrativas.
