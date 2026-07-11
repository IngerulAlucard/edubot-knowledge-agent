# Arquitectura de EduBot Knowledge Agent

## 1. Visión general

EduBot es una aplicación web modular que responde preguntas sobre la información institucional de EduNova Academy. Su base de conocimiento está formada por documentos PDF y un catálogo CSV almacenados en `data/uploads/`.

La solución separa la interfaz, la ingesta, la recuperación y la generación. Utiliza una estrategia híbrida: consulta datos estructurados con Pandas cuando reconoce una pregunta sobre cursos y usa un flujo RAG para las consultas documentales.

## 2. Diagrama de contexto

```text
                         +-----------------------+
Visitante -------------->| Interfaz pública      |
                         | Streamlit             |
                         +-----------+-----------+
                                     |
                                     v
                         +-----------------------+
                         | Motor de consultas    |
                         +-----+------------+----+
                               |            |
                      catálogo |            | documentos
                               v            v
                         +-----------+  +----------------+
                         | Pandas    |  | Recuperación   |
                         | CSV       |  | semántica      |
                         +-----+-----+  +--------+-------+
                               |                 |
                               |                 v
                               |          +--------------+
                               |          | Cohere       |
                               |          | Command R    |
                               |          +------+-------+
                               |                 |
                               +--------+--------+
                                        |
                                        v
                                  Respuesta final

Administrador --> Autenticación --> Gestión de PDF/CSV --> data/uploads/
```

## 3. Componentes

### `app.py`: presentación y orquestación

- Presenta el campo de consulta y las respuestas.
- Mantiene público el chatbot.
- Gestiona la autenticación administrativa en `st.session_state`.
- Permite subir, listar, eliminar y recargar archivos.
- Coordina las rutas estructurada y semántica.
- Muestra métricas públicas y la vista del CSV solo al administrador.
- Aplica caché con `st.cache_resource` y `st.cache_data`.

### `src/document_loader.py`: ingesta

- `load_pdf_text()` extrae texto mediante PyPDF.
- `load_csv_data()` carga el catálogo como `DataFrame`.
- `csv_to_text()` convierte las filas en texto para la ruta semántica.

### `src/knowledge_base.py`: recuperación

- Carga `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- Divide el contenido en fragmentos de aproximadamente 900 caracteres.
- Genera embeddings normalizados en `float32`.
- Calcula similitud mediante producto punto con NumPy.
- Recupera hasta 4 fragmentos con puntuación mínima de `0.25`.
- Resuelve consultas del catálogo por nombre, categoría, nivel, modalidad, precio, duración, estado, certificado y requisitos.

### `src/chatbot.py`: generación

- Detecta saludos y responde localmente.
- Construye un prompt restringido al contexto.
- Valida `COHERE_API_KEY`.
- Consulta `command-r-08-2024` con temperatura `0.2`.
- Controla la ausencia de contexto y los errores de API.

## 4. Flujo de carga

```text
Inicio o cambio de archivos
          |
          v
Listado de data/uploads/
          |
          +-----------------------+
          |                       |
          v                       v
       Archivos PDF            Archivos CSV
          |                       |
          v                       v
Extracción con PyPDF      DataFrame con Pandas
          |                       |
          |                +------+------+
          |                |             |
          |                v             v
          |          Consulta directa  Conversión a texto
          |                              |
          +---------------+--------------+
                          |
                          v
                 Unión y fragmentación
                          |
                          v
                 Embeddings normalizados
                          |
                          v
                    Caché en memoria
```

El modelo se conserva con `@st.cache_resource`. Los fragmentos, embeddings y tablas se almacenan mediante `@st.cache_data(max_entries=10)`. La caché de datos se invalida al guardar, eliminar o recargar documentos.

## 5. Flujo de consulta

```text
Pregunta
   |
   +--> ¿Está vacía? --------> Advertencia
   |
   +--> ¿Es un saludo? ------> Mensaje local
   |
   +--> ¿Es una consulta reconocida del catálogo?
   |         |
   |         v
   |     Filtro Pandas ------> Respuesta estructurada
   |
   +--> Búsqueda semántica
             |
             v
       Embedding de pregunta
             |
             v
       Similitud con chunks
             |
             +--> Sin contexto suficiente --> Mensaje controlado
             |
             v
       Contexto + prompt
             |
             v
       Cohere Command R -----> Respuesta en español
```

La ruta estructurada tiene prioridad porque evita delegar al modelo generativo datos tabulares que pueden obtenerse de forma exacta.

## 6. Esquema del catálogo

El CSV necesita estas columnas para habilitar la ruta estructurada:

| Columna | Contenido |
| --- | --- |
| `id_curso` | Identificador |
| `nombre_curso` | Nombre visible |
| `categoria` | Área temática |
| `nivel` | Dificultad |
| `duracion_horas` | Duración total |
| `modalidad` | Forma de impartición |
| `costo_mxn` | Precio en MXN |
| `requisitos_previos` | Conocimientos requeridos |
| `tipo_certificado` | Certificado o constancia |
| `estado` | Disponibilidad |

Si ningún CSV contiene el esquema completo, la aplicación omite esta ruta y continúa con recuperación semántica.

## 7. Seguridad

Perfiles:

- **Visitante:** consulta el agente sin iniciar sesión.
- **Administrador:** gestiona documentos y puede ver detalles técnicos.

Controles implementados:

- La contraseña proviene de `ADMIN_PASSWORD`.
- La comparación usa `hmac.compare_digest`.
- La autenticación solo se conserva en la sesión de Streamlit.
- `Path(...).name` elimina rutas incluidas en nombres subidos.
- Solo se aceptan extensiones `.pdf` y `.csv`.
- La eliminación valida que el archivo esté en `data/uploads/`.
- Los secretos se cargan desde `.env`, que no debe versionarse.

Este mecanismo es adecuado para una demostración educativa, pero no reemplaza identidad, roles y auditoría para producción.

## 8. Tecnologías por capa

| Capa | Tecnologías |
| --- | --- |
| Presentación | Streamlit |
| Ingesta | PyPDF, Pandas |
| Recuperación | Sentence Transformers, NumPy |
| Generación | Cohere |
| Configuración | python-dotenv, variables de entorno |
| Persistencia | Sistema de archivos local |
| Despliegue | OCI Compute |

## 9. Estructura física

```text
edubot-knowledge-agent/
├── app.py
├── requirements.txt
├── .env.example
├── data/
│   └── uploads/
├── src/
│   ├── chatbot.py
│   ├── document_loader.py
│   └── knowledge_base.py
└── docs/
    ├── arquitectura.md
    ├── ejemplos_preguntas.md
    ├── evidencia_deploy.md
    └── base_conocimiento/
```

## 10. Ejecución y despliegue

Desarrollo:

```bash
streamlit run app.py
```

OCI:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Se deben configurar `COHERE_API_KEY` y `ADMIN_PASSWORD`. En OCI también debe permitirse el puerto `8501` en la red y el firewall.

## 11. Decisiones y beneficios

- **Ruta híbrida:** exactitud tabular y flexibilidad documental.
- **Embeddings locales:** selección semántica de contexto en español.
- **Contexto limitado:** prompts más pequeños y relevantes.
- **Caché:** evita reprocesar documentos y recargar el modelo.
- **Separación modular:** facilita sustituir componentes.
- **Administración separada:** el chatbot sigue público sin exponer documentos.

## 12. Limitaciones y evolución

Limitaciones:

- No existe historial conversacional.
- Los embeddings solo viven en memoria.
- Los archivos se almacenan localmente.
- No hay citas de fuentes.
- La administración usa una contraseña compartida.
- No hay pruebas automatizadas ni integración continua.
- Cohere es una dependencia externa.

Mejoras recomendadas:

- Persistir embeddings en una base vectorial.
- Mostrar documento, página y fragmento fuente.
- Incorporar usuarios, roles y auditoría.
- Mover documentos a Object Storage.
- Añadir pruebas y GitHub Actions.
- Empaquetar la aplicación con Docker.
- Registrar latencia, errores y calidad de recuperación.
