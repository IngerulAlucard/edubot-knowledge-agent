# 📚 EduBot Knowledge Agent

EduBot Knowledge Agent es una aplicación web desarrollada en Python para responder preguntas sobre la documentación interna de una plataforma educativa ficticia llamada **EduNova Academy**.

El sistema combina recuperación semántica sobre documentos PDF con consultas estructuradas sobre un catálogo de cursos en CSV. La interfaz pública permite realizar preguntas sin registro, mientras que las funciones para subir, eliminar y recargar documentos están protegidas mediante una contraseña administrativa.

---

## 🎯 Objetivo

Desarrollar un agente de inteligencia artificial capaz de consultar documentos educativos y responder preguntas frecuentes de estudiantes de forma clara, rápida y basada en información documentada.

---

## 📌 Descripción general del proyecto

EduNova Academy maneja información distribuida en políticas, reglamentos, manuales, guías y catálogos. Buscar respuestas manualmente en estos archivos puede resultar lento y poco práctico.

EduBot centraliza esa información y permite consultarla mediante lenguaje natural. El agente puede responder preguntas relacionadas con:

- Cursos disponibles.
- Precio, duración, nivel, categoría y modalidad.
- Certificados y constancias.
- Becas.
- Reembolsos y cambios de curso.
- Pagos y facturación.
- Evaluaciones y proyectos finales.
- Soporte técnico.
- Reglamento académico.

La base de conocimiento se almacena en `data/uploads/` y está compuesta por documentos PDF y un catálogo de cursos en formato CSV.

---

## 🧠 Arquitectura de la solución implementada

EduBot utiliza una arquitectura híbrida con dos rutas principales de procesamiento.

### 1. Consultas estructuradas del catálogo

Las preguntas relacionadas con cursos se procesan directamente con Pandas. El sistema identifica filtros como nombre, nivel, categoría, modalidad, costo, requisitos, tipo de certificado y estado.

Ejemplos:

- ¿Cuánto cuesta Python Básico?
- ¿Qué cursos son de nivel principiante?
- ¿Qué cursos pertenecen a Cloud Computing?
- ¿Cuál es el curso más barato?
- ¿Hay cursos sincrónicos?

Estas consultas se resuelven mediante filtros sobre `catalogo_cursos.csv`, sin depender del modelo generativo para calcular o enumerar los resultados.

### 2. Consultas documentales

Las preguntas relacionadas con políticas, procedimientos, soporte, becas, pagos, certificados o reglamentos utilizan recuperación semántica.

```text
Usuario
   ↓
Interfaz Streamlit
   ↓
Pregunta en lenguaje natural
   ↓
Clasificación de la consulta
   ├── Consulta de catálogo
   │      ↓
   │   Filtros con Pandas
   │      ↓
   │   Respuesta estructurada
   │
   └── Consulta documental
          ↓
       Normalización de texto
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

### 3. Recuperación semántica

El proyecto utiliza el modelo:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Este modelo transforma preguntas y fragmentos documentales en vectores numéricos. Después, NumPy calcula la similitud para recuperar el contenido más relacionado con la consulta.

Por ejemplo, la pregunta:

```text
¿Cómo recupero el dinero que pagué?
```

![alt text](/screenshots/contexto.png)


puede relacionarse con la política de reembolsos aunque no incluya literalmente la palabra `reembolso`.

Tolera faltas ortográficas

Por ejemplo, la pregunta:

```text
me explicas el rglameento
``` 

![alt text](/screenshots/falta-ortografica.png)

### 4. Despliegue en OCI

![alt text](/screenshots/config-oci.png)

```text
Usuario
   ↓
IP pública de OCI:8501
   ↓
Security List de la VCN
   ↓
Regla de firewall del sistema
   ↓
Servicio systemd
   ↓
Streamlit
   ↓
EduBot Knowledge Agent
   ↓
PDF + CSV + Sentence Transformers + Cohere
```

La documentación técnica ampliada se encuentra en:

```text
docs/arquitectura.md
```

---

## 🔐 Acceso público y administración

El chatbot es público y no requiere inicio de sesión.

Cualquier visitante puede:

- Escribir preguntas.
- Consultar la base de conocimiento.
- Ver respuestas generadas por EduBot.

El panel administrativo está protegido mediante contraseña. Solo el administrador puede:

- Subir documentos PDF o CSV.
- Eliminar documentos.
- Recargar la base de conocimiento.
- Consultar la vista previa completa del catálogo.

La contraseña se configura con:

```env
ADMIN_PASSWORD=tu_contraseña_administrativa
```

![alt text](/screenshots/admin.png)

---

## 🛠️ Tecnologías y herramientas utilizadas

| Tecnología | Uso |
|---|---|
| Python | Lenguaje principal |
| Streamlit | Interfaz web |
| Pandas | Procesamiento estructurado del catálogo |
| PyPDF | Extracción de texto desde archivos PDF |
| Sentence Transformers | Generación de embeddings |
| NumPy | Comparación de vectores y similitud |
| Cohere | Generación de respuestas |
| python-dotenv | Carga de variables de entorno |
| Git | Control de versiones |
| GitHub | Repositorio y colaboración |
| Oracle Cloud Infrastructure | Despliegue en la nube |
| Ubuntu 24.04 | Sistema operativo del servidor |
| systemd | Ejecución persistente del servicio |
| iptables | Control de acceso al puerto de la aplicación |

Dependencias declaradas en `requirements.txt`:

```text
streamlit
pandas
pypdf
python-dotenv
cohere
sentence-transformers
numpy
torchvision
```

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
│   ├── __pycache__
│   ├── document_loader.py
│   ├── knowledge_base.py
│   └── chatbot.py
├── docs/
│   ├── arquitectura.md
│   ├── ejemplos_preguntas.md
│   └── evidencia_deploy.md
├── assets/
│   └── nox_edubot.png
└── screenshots/
│   ├── admin.png
│   ├── config-oci.png
│   ├── contexto.png
│   ├── edubot-funcionando.png
│   ├── falta_ortografica.png
│   └── saludo.png
```

---

## 📄 Componentes principales

### `app.py`

Contiene la interfaz Streamlit y coordina el flujo general de la aplicación:

- Presenta el chatbot.
- Recibe preguntas.
- Gestiona el acceso administrativo.
- Permite subir y eliminar archivos.
- Recarga la base de conocimiento.
- Muestra respuestas y errores controlados.

### `src/document_loader.py`

- Lee archivos PDF.
- Extrae texto.
- Carga archivos CSV.
- Convierte el catálogo en contenido utilizable.

### `src/knowledge_base.py`

- Divide documentos en fragmentos.
- Normaliza texto.
- Genera embeddings.
- Busca fragmentos relevantes.
- Resuelve consultas estructuradas del catálogo.

### `src/chatbot.py`

- Detecta saludos.
- Construye el contexto.
- Valida la configuración de Cohere.
- Genera respuestas basadas en la documentación recuperada.

---

## ✅ Requisitos previos

Para ejecutar el proyecto se necesita:

- Python 3.10 o superior.
- Git.
- Una clave válida de Cohere.
- Conexión a internet.
- 4 GB de RAM recomendados para cargar Sentence Transformers con mayor estabilidad.

---

# 🚀 Ejecución local

## 1. Clonar el repositorio

```bash
git clone https://github.com/IngerulAlucard/edubot-knowledge-agent.git
cd edubot-knowledge-agent
```

## 2. Crear un entorno virtual

En Linux o macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3. Instalar dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Crear el archivo `.env`

En la raíz del proyecto crea un archivo llamado `.env`:

```env
COHERE_API_KEY=tu_clave_de_cohere
ADMIN_PASSWORD=tu_contraseña_administrativa
```

El archivo `.env` contiene secretos y no debe subirse a GitHub.

## 5. Verificar la base de conocimiento

Los archivos deben encontrarse dentro de:

```text
data/uploads/
```

## 6. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación estará disponible en:

```text
http://localhost:8501
```

---

# ☁️ Despliegue en Oracle Cloud Infrastructure

La implementación probada utiliza la siguiente configuración:

- Sistema operativo: Canonical Ubuntu 24.04.
- Shape: `VM.Standard.E5.Flex`.
- Arquitectura: AMD x86_64.
- Procesador: 1 OCPU.
- Memoria RAM: 4 GB.
- Ancho de banda: hasta 1 Gbps.
- Puerto de aplicación: `8501`.
- Servicio persistente: `systemd`.

> `VM.Standard.E5.Flex` puede generar costos según la región, la cuenta y los recursos asignados. Conviene revisar el panel de costos de OCI.

## 1. Crear la instancia

En OCI crea una instancia de Compute con Ubuntu 24.04 y una dirección IPv4 pública.

## 2. Conectarse por SSH

Desde PowerShell:

```powershell
ssh -i .\ssh-key.key ubuntu@IP_PUBLICA
```

## 3. Instalar paquetes del sistema

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git python3 python3-pip python3-venv build-essential
```

## 4. Clonar el repositorio

```bash
cd /home/ubuntu
git clone https://github.com/IngerulAlucard/edubot-knowledge-agent.git
cd edubot-knowledge-agent
```

## 5. Crear el entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## 6. Configurar variables de entorno

```bash
nano .env
```

Contenido:

```env
COHERE_API_KEY=tu_clave_de_cohere
ADMIN_PASSWORD=tu_contraseña_administrativa
```

Proteger el archivo:

```bash
chmod 600 .env
```

## 7. Abrir el puerto 8501 en OCI

En la Security List asociada a la subnet agrega una regla de ingreso:

```text
Source Type: CIDR
Source CIDR: 0.0.0.0/0
IP Protocol: TCP
Source Port Range: All
Destination Port Range: 8501
Description: Streamlit EduBot
```

Para mayor seguridad, en un entorno real se recomienda restringir el origen o colocar Nginx con HTTPS delante de Streamlit.

## 8. Permitir el puerto en Ubuntu

En la imagen utilizada, `ufw` no estaba instalado. La regla se agregó con `iptables`:

```bash
sudo iptables -I INPUT 1 -p tcp --dport 8501 -j ACCEPT
```

Verificar:

```bash
sudo iptables -L INPUT -n -v --line-numbers | grep 8501
```

Guardar la regla para que sobreviva reinicios:

```bash
sudo apt install -y iptables-persistent
sudo netfilter-persistent save
sudo netfilter-persistent reload
```

## 9. Probar Streamlit manualmente

```bash
streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.headless true
```

Verificar desde la VM:

```bash
curl -I http://localhost:8501
```

La respuesta esperada contiene:

```text
HTTP/1.1 200 OK
```

## 10. Crear el servicio `systemd`

```bash
sudo nano /etc/systemd/system/edubot.service
```

Contenido:

```ini
[Unit]
Description=EduBot Knowledge Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/edubot-knowledge-agent
EnvironmentFile=/home/ubuntu/edubot-knowledge-agent/.env
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/ubuntu/edubot-knowledge-agent/venv/bin/streamlit run /home/ubuntu/edubot-knowledge-agent/app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activar e iniciar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now edubot
```

Comprobar el servicio:

```bash
sudo systemctl status edubot
sudo systemctl is-enabled edubot
sudo ss -lntp | grep 8501
curl -I http://localhost:8501
```

La aplicación queda disponible en:

```text
http://IP_PUBLICA:8501
```

## 11. Consultar registros

```bash
sudo journalctl -u edubot -n 100 --no-pager
```

Registros en tiempo real:

```bash
sudo journalctl -u edubot -f
```

## 12. Actualizar el despliegue

```bash
cd /home/ubuntu/edubot-knowledge-agent
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart edubot
sudo systemctl status edubot
```

---

## 📥 Uso de la aplicación

### Uso público

1. Abrir EduBot en el navegador.
2. Escribir una pregunta.
3. Presionar **Consultar**.
4. Revisar la respuesta y las fuentes mostradas por la aplicación.

![alt text](/screenshots/edubot-funcionando.png)

### Uso administrativo

1. Abrir la sección **Acceso administrativo**.
2. Escribir la contraseña configurada.
3. Subir, eliminar o recargar documentos.
4. Cerrar la sesión administrativa al terminar.

![alt text](/screenshots/admin.png)


---

## 💬 Ejemplos de preguntas que el agente puede responder

### Certificados

```text
¿Cómo puedo obtener mi certificado?
¿Cuánto tarda en aparecer mi certificado?
¿Dónde descargo mi certificado?
```

### Reembolsos

```text
¿Cuánto tiempo tengo para pedir un reembolso?
¿Cómo recupero el dinero que pagué?
¿Puedo pedir reembolso si avancé más del 20%?
```

### Becas

```text
¿Qué requisitos necesito para solicitar una beca?
¿Cuánto cubre una beca?
¿La beca puede cubrir el 100% del curso?
```

### Soporte técnico

```text
¿Qué hago si no puedo iniciar sesión?
¿Cómo contacto a soporte técnico?
¿Cuánto tarda soporte en responder?
```

### Evaluaciones

```text
¿Qué calificación necesito para aprobar?
¿Cuántos intentos tengo en una evaluación?
¿Qué pasa si repruebo los tres intentos?
```

### Cursos

```text
¿Qué cursos son de nivel principiante?
¿Cuánto cuesta Python Básico?
¿Qué cursos pertenecen a Cloud Computing?
¿Cuál es el curso más barato?
¿Hay cursos sincrónicos?
```

---

## 🤖 Ejemplos de respuestas generadas por el agente

### Ejemplo 1: certificado

**Pregunta**

```text
¿Cómo puedo obtener mi certificado?
```

**Respuesta de ejemplo**

Para obtener tu certificado debes completar el 100% del contenido obligatorio, aprobar las evaluaciones con una calificación mínima de 80 sobre 100, entregar el proyecto final si aplica, no tener pagos pendientes, cumplir el reglamento y mantener actualizados tus datos personales.

### Ejemplo 2: reembolso

**Pregunta**

```text
¿Cuánto tiempo tengo para pedir un reembolso?
```

**Respuesta de ejemplo**

Puedes solicitar un reembolso dentro de los primeros 7 días naturales posteriores a la compra. Para que proceda, no debes haber completado más del 20% del curso, descargado materiales restringidos ni recibido certificado o constancia.

### Ejemplo 3: beca

**Pregunta**

```text
¿Qué requisitos necesito para solicitar una beca?
```

**Respuesta de ejemplo**

Debes proporcionar tu nombre completo, correo registrado, curso de interés, motivo de la solicitud, objetivo de aprendizaje y comprobante de estudios o situación laboral si aplica. Las becas son parciales y pueden cubrir entre el 20% y el 70% del costo del curso.

### Ejemplo 4: curso

**Pregunta**

```text
¿Cuánto cuesta Python Básico?
```

**Respuesta de ejemplo**

El curso Python Básico cuesta 999 MXN, tiene una duración de 40 horas, modalidad asincrónica y nivel principiante.

### Ejemplo 5: modalidad

**Pregunta**

```text
¿Hay cursos sincrónicos?
```

**Respuesta de ejemplo**

Según el catálogo actual, no hay cursos con modalidad sincrónica disponibles.

### Ejemplo 6: soporte

**Pregunta**

```text
¿Cuánto tarda soporte en responder?
```

**Respuesta de ejemplo**

El tiempo promedio de respuesta de soporte técnico es de 24 a 48 horas hábiles. Los canales oficiales son el correo de soporte, el formulario de contacto y el chat de ayuda del panel del estudiante.

---

## ✔️ Validaciones implementadas

La aplicación valida:

- Que existan documentos en la base de conocimiento.
- Que la pregunta no esté vacía.
- Que los archivos sean PDF o CSV.
- Que el catálogo tenga las columnas necesarias.
- Que exista `COHERE_API_KEY`.
- Que exista `ADMIN_PASSWORD`.
- Que la contraseña administrativa sea correcta.
- Que los archivos se almacenen dentro de `data/uploads/`.
- Que existan fragmentos relevantes para responder.
- Que los errores se presenten de forma controlada.

---

## ⚠️ Limitaciones actuales

- No mantiene historial persistente de conversación.
- No utiliza una base vectorial persistente.
- Los embeddings se almacenan en memoria.
- Los documentos se guardan localmente en la VM.
- Solo existe una contraseña administrativa compartida.
- No incluye pruebas automatizadas.
- Cohere y la descarga inicial de modelos requieren conexión a internet.
- El despliegue actual usa HTTP directo en el puerto 8501, sin dominio ni certificado TLS.

---

## 🔮 Posibles mejoras

- Agregar Nginx como proxy inverso.
- Configurar dominio y HTTPS con Let's Encrypt.
- Implementar autenticación por usuarios y roles.
- Guardar conversaciones en una base de datos.
- Usar una base vectorial persistente.
- Añadir pruebas automatizadas.
- Crear un flujo de CI/CD con GitHub Actions.
- Respaldar automáticamente los documentos subidos.

---


## 👤 Autor

**ANGELICA JAZMIN FLORES PACHECO (Îngerul Alucard/Noctis)**

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para conocer los términos de uso.
