# Arquitectura de EduBot Knowledge Agent

## 1. Descripción general

EduBot Knowledge Agent es una aplicación desarrollada en Python que permite responder preguntas en lenguaje natural utilizando documentos institucionales en formato PDF y un catálogo de cursos en formato CSV.

La solución fue diseñada para una plataforma educativa ficticia llamada EduNova Academy. Su objetivo es centralizar información relacionada con cursos, certificados, becas, pagos, reembolsos, evaluaciones, soporte técnico y reglamento académico.

La aplicación utiliza una arquitectura híbrida que combina:

* Procesamiento estructurado de datos con Pandas.
* Recuperación de información desde documentos.
* Generación de respuestas mediante Cohere.
* Interfaz web desarrollada con Streamlit.

---

## 2. Arquitectura general

El sistema está compuesto por cuatro capas principales:

1. Capa de presentación.
2. Capa de procesamiento de documentos.
3. Capa de recuperación de información.
4. Capa de generación de respuestas.

El flujo general es el siguiente:

```text
Usuario
   ↓
Interfaz web con Streamlit
   ↓
Carga y gestión de archivos PDF y CSV
   ↓
Extracción y transformación de información
   ↓
Clasificación de la consulta
   ├── Consulta estructurada sobre cursos
   │      ↓
   │   Filtrado directo con Pandas
   │
   └── Consulta documental
          ↓
       División del contenido en fragmentos
          ↓
       Recuperación de fragmentos relevantes
          ↓
       Construcción del contexto
          ↓
       Envío de contexto y pregunta a Cohere
          ↓
       Generación de respuesta
   ↓
Respuesta mostrada al usuario
```

---

## 3. Componentes principales

### 3.1 Interfaz de usuario

La interfaz se encuentra implementada en el archivo:

```text
app.py
```

Este componente utiliza Streamlit y se encarga de:

* Mostrar la interfaz principal.
* Permitir la carga de archivos PDF y CSV.
* Mostrar los documentos disponibles.
* Eliminar archivos cargados.
* Recargar la base de conocimiento.
* Recibir preguntas del usuario.
* Mostrar respuestas generadas por EduBot.
* Presentar una vista previa de los archivos CSV.
* Mostrar métricas de archivos y fragmentos procesados.

La interfaz también controla validaciones básicas, como:

* Verificar que existan documentos cargados.
* Evitar consultas vacías.
* Detectar saludos.
* Mostrar mensajes de error controlados.
* Limpiar la caché cuando se agregan o eliminan archivos.

---

### 3.2 Procesamiento de documentos

El procesamiento de archivos se encuentra en:

```text
src/document_loader.py
```

Este módulo se encarga de cargar y transformar los documentos utilizados como base de conocimiento.

#### Procesamiento de archivos PDF

Los documentos PDF se procesan mediante PyPDF.

El flujo es:

```text
Archivo PDF
   ↓
Lectura de páginas
   ↓
Extracción de texto
   ↓
Unión del contenido
   ↓
Texto listo para recuperación
```

Los PDF contienen información institucional sobre:

* Certificados.
* Reembolsos.
* Becas.
* Soporte técnico.
* Pagos.
* Evaluaciones.
* Reglamento.
* Preguntas frecuentes.

#### Procesamiento de archivos CSV

Los archivos CSV se cargan mediante Pandas.

El flujo es:

```text
Archivo CSV
   ↓
Carga como DataFrame
   ↓
Validación de columnas
   ↓
Uso como tabla estructurada
   ↓
Conversión adicional a texto
```

El catálogo de cursos incluye información como:

* Identificador del curso.
* Nombre.
* Categoría.
* Nivel.
* Duración.
* Modalidad.
* Costo.
* Requisitos previos.
* Tipo de certificado.
* Estado.

---

### 3.3 Base de conocimiento

La lógica principal de recuperación se encuentra en:

```text
src/knowledge_base.py
```

Este módulo tiene dos responsabilidades:

1. Recuperar información desde documentos de texto.
2. Resolver consultas estructuradas sobre el catálogo de cursos.

---

## 4. Recuperación de información documental

Los documentos PDF se convierten en texto y posteriormente se dividen en fragmentos.

### 4.1 División en fragmentos

La función de fragmentación divide el texto completo en bloques de tamaño definido.

El objetivo es evitar enviar toda la documentación al modelo de lenguaje en cada consulta.

```text
Texto completo
   ↓
Normalización de espacios
   ↓
División en fragmentos
   ↓
Lista de bloques de texto
```

Cada fragmento funciona como una unidad independiente de búsqueda.

---

### 4.2 Normalización del texto

Antes de comparar la pregunta con los fragmentos, el sistema normaliza el texto.

La normalización incluye:

* Conversión a minúsculas.
* Eliminación de acentos.
* Eliminación de signos.
* Reducción de espacios repetidos.
* Conversión a una representación comparable.

Por ejemplo:

```text
¿Qué requisitos necesito para una beca?
```

se transforma internamente en:

```text
que requisitos necesito para una beca
```

Esto mejora las coincidencias entre preguntas y documentos.

---

### 4.3 Cálculo de relevancia

La recuperación utiliza un sistema de puntuación basado en coincidencias de palabras.

El proceso es:

1. Se normaliza la pregunta.
2. Se normaliza cada fragmento.
3. Se eliminan palabras comunes.
4. Se comparan las palabras relevantes.
5. Se asigna una puntuación.
6. Se seleccionan los fragmentos con mayor puntuación.

```text
Pregunta del usuario
   ↓
Palabras relevantes
   ↓
Comparación con cada fragmento
   ↓
Puntuación por coincidencias
   ↓
Ordenamiento
   ↓
Selección de los mejores fragmentos
```

Por defecto, el sistema recupera los fragmentos más relacionados con la pregunta.

Este enfoque corresponde a una recuperación léxica simple. No utiliza embeddings ni una base de datos vectorial.

---

## 5. Consultas estructuradas del catálogo

Las preguntas relacionadas con cursos se procesan directamente con Pandas.

Esto evita que el modelo de lenguaje tenga que interpretar o calcular datos estructurados.

El sistema puede responder consultas sobre:

* Cursos por nivel.
* Cursos por categoría.
* Cursos por modalidad.
* Cursos por costo.
* Cursos por duración.
* Curso más barato.
* Curso más caro.
* Cursos con certificado.
* Cursos con constancia.
* Cursos activos.
* Requisitos previos.
* Nombre exacto o parcial de un curso.

Ejemplos:

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
¿Qué cursos cuestan menos de 1000 MXN?
```

```text
¿Hay cursos sincrónicos?
```

El flujo es:

```text
Pregunta sobre cursos
   ↓
Normalización de la consulta
   ↓
Detección del tipo de filtro
   ↓
Aplicación del filtro en el DataFrame
   ↓
Formateo de resultados
   ↓
Respuesta directa
```

Este procesamiento es determinista, ya que la respuesta se obtiene directamente de los datos del CSV.

---

## 6. Generación de respuestas con Cohere

La integración con el modelo de lenguaje se encuentra en:

```text
src/chatbot.py
```

Este módulo utiliza Cohere para redactar respuestas basadas en los fragmentos recuperados.

El modelo configurado es:

```text
command-r-08-2024
```

El flujo es:

```text
Pregunta del usuario
   ↓
Fragmentos relevantes
   ↓
Construcción del prompt
   ↓
Envío a Cohere
   ↓
Generación de respuesta
   ↓
Respuesta final
```

El prompt indica al modelo que:

* Responda en español.
* Use únicamente la información disponible.
* No invente datos.
* Sea claro y directo.
* No copie todo el contexto.
* Incluya plazos, porcentajes, requisitos y excepciones.
* Indique cuando no existe información suficiente.

---

## 7. Clasificación de consultas

EduBot decide cómo responder según el tipo de pregunta.

### Consultas de saludo

Los saludos simples se responden sin utilizar Cohere.

Ejemplos:

```text
Hola
```

```text
Buenas tardes
```

Esto evita llamadas innecesarias al modelo.

### Consultas del catálogo

Las preguntas sobre cursos se procesan mediante Pandas.

Ejemplos:

```text
¿Qué cursos son avanzados?
```

```text
¿Cuánto cuesta Agentes de IA con Python?
```

### Consultas institucionales

Las preguntas sobre políticas o procedimientos se resuelven mediante recuperación documental y Cohere.

Ejemplos:

```text
¿Cómo obtengo mi certificado?
```

```text
¿Cuánto tiempo tengo para pedir un reembolso?
```

```text
¿Qué requisitos necesito para solicitar una beca?
```

### Consultas sin información suficiente

Si no se encuentran fragmentos relevantes, el sistema responde que no existe información suficiente en la base de conocimiento.

---

## 8. Gestión de archivos

Los archivos utilizados por la aplicación se almacenan en:

```text
data/uploads/
```

La aplicación permite:

* Subir archivos.
* Guardarlos en el servidor.
* Listarlos.
* Eliminarlos.
* Recargar la base de conocimiento.

Los formatos aceptados son:

```text
.pdf
.csv
```

Cuando se agrega o elimina un archivo, la aplicación limpia la caché para evitar respuestas basadas en información desactualizada.

---

## 9. Uso de caché

Streamlit utiliza caché para evitar reprocesar todos los archivos en cada interacción.

La base de conocimiento se almacena temporalmente después de ser procesada.

La caché se limpia cuando:

* Se guarda un archivo nuevo.
* Se elimina un archivo.
* El usuario selecciona la opción de recargar la base de conocimiento.

Esto mejora el rendimiento de la aplicación.

---

## 10. Manejo de errores

La aplicación incluye manejo de errores para distintos escenarios:

* Archivo inexistente.
* Documento inválido.
* Error al leer un PDF.
* Error al cargar un CSV.
* Falta de documentos.
* Consulta vacía.
* Falta de la variable `COHERE_API_KEY`.
* Error de conexión con Cohere.
* Error inesperado durante la ejecución.

Los errores se muestran mediante mensajes de Streamlit para evitar que la aplicación termine abruptamente.

---

## 11. Seguridad y configuración

La clave de Cohere no debe almacenarse directamente en el código.

Se utiliza una variable de entorno:

```env
COHERE_API_KEY=tu_clave_de_cohere
```

Durante el desarrollo local, esta variable puede colocarse en un archivo:

```text
.env
```

El archivo `.env` debe estar excluido del repositorio mediante `.gitignore`.

En un despliegue en Oracle Cloud Infrastructure, la variable debe configurarse directamente en el entorno del servidor.

---

## 12. Estructura del repositorio

```text
edubot-knowledge-agent/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── uploads/
│       ├── 00_manual_general_edunova.pdf
│       ├── 01_politica_certificados.pdf
│       ├── 02_politica_reembolsos.pdf
│       ├── 03_guia_soporte_tecnico.pdf
│       ├── 04_programa_becas.pdf
│       ├── 05_guia_pagos_facturacion.pdf
│       ├── 06_guia_evaluaciones.pdf
│       ├── 07_reglamento_estudiantes.pdf
│       ├── 08_faq_general.pdf
│       ├── 10_manual_docentes.pdf
│       └── catalogo_cursos.csv
├── src/
│   ├── __init__.py
│   ├── document_loader.py
│   ├── knowledge_base.py
│   └── chatbot.py
├── docs/
│   ├── arquitectura.md
│   ├── ejemplos_preguntas.md
│   ├── evidencia_deploy.md
│   └── base_conocimiento/
└── screenshots/
    └── app_funcionando.png
```

---

## 13. Responsabilidad de cada archivo

### `app.py`

Controla la interfaz, la carga de archivos, la recepción de preguntas y la presentación de respuestas.

### `src/document_loader.py`

Carga archivos PDF y CSV y transforma su contenido.

### `src/knowledge_base.py`

Divide los documentos en fragmentos, calcula relevancia y resuelve consultas estructuradas del catálogo.

### `src/chatbot.py`

Construye el prompt, valida la clave de Cohere y genera respuestas mediante el modelo.

### `requirements.txt`

Define las dependencias necesarias para ejecutar el proyecto.

### `data/uploads/`

Contiene los documentos utilizados como base de conocimiento.

### `docs/`

Contiene documentación técnica, ejemplos y evidencia del despliegue.

### `screenshots/`

Contiene capturas de pantalla de la aplicación en ejecución.

---

## 14. Tecnologías utilizadas

| Tecnología                  | Uso                            |
| --------------------------- | ------------------------------ |
| Python                      | Lenguaje principal             |
| Streamlit                   | Interfaz web                   |
| Pandas                      | Procesamiento del catálogo CSV |
| PyPDF                       | Extracción de texto desde PDF  |
| Cohere                      | Generación de respuestas       |
| python-dotenv               | Carga de variables de entorno  |
| GitHub                      | Control de versiones           |
| Oracle Cloud Infrastructure | Despliegue de la aplicación    |

---

## 15. Tipo de arquitectura

EduBot utiliza una arquitectura modular e híbrida.

Es modular porque cada responsabilidad se encuentra separada en un archivo distinto.

Es híbrida porque combina dos mecanismos de respuesta:

### Mecanismo estructurado

Se utiliza para consultar el catálogo CSV mediante filtros de Pandas.

### Mecanismo generativo

Se utiliza para responder preguntas institucionales mediante recuperación de fragmentos y generación con Cohere.

Esta separación reduce errores, mejora la precisión y evita depender del modelo de lenguaje para operaciones que pueden resolverse directamente con datos estructurados.

---

## 16. Limitaciones actuales

La versión actual presenta las siguientes limitaciones:

* No utiliza embeddings.
* No utiliza una base de datos vectorial.
* La recuperación depende de coincidencias de palabras.
* No mantiene historial de conversación.
* No conserva contexto entre preguntas.
* No incluye autenticación de usuarios.
* No registra consultas en una base de datos.
* No incluye pruebas automatizadas.
* La calidad de las respuestas depende de la documentación cargada.
* Requiere conexión a internet para consultar Cohere.

---

## 17. Posibles mejoras futuras

El proyecto puede ampliarse mediante:

* Implementación de embeddings.
* Uso de una base vectorial.
* Historial de conversación.
* Autenticación de usuarios.
* Registro de consultas.
* Panel administrativo.
* Citas de documentos fuente.
* Pruebas unitarias.
* Contenedorización con Docker.
* Automatización de despliegue.
* Monitoreo de errores.
* Clasificación más avanzada de consultas.
* Soporte para documentos Word y texto plano.
* Uso de almacenamiento persistente en la nube.

---

## 18. Conclusión

EduBot Knowledge Agent implementa una solución funcional para consultar información educativa desde documentos PDF y archivos CSV.

La arquitectura separa la interfaz, el procesamiento de documentos, la recuperación de información y la generación de respuestas.

El uso combinado de Pandas y Cohere permite responder tanto preguntas estructuradas sobre cursos como consultas abiertas sobre políticas institucionales.

Esta arquitectura facilita el mantenimiento, la ampliación y el despliegue del proyecto en Oracle Cloud Infrastructure.
