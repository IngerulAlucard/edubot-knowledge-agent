# Evidencia de Deploy en OCI

Este documento presenta la evidencia del despliegue de **EduBot Knowledge Agent** en Oracle Cloud Infrastructure.

## Aplicación desplegada

EduBot Knowledge Agent fue desplegado en una instancia de OCI Compute utilizando Ubuntu Server.

La aplicación se ejecuta mediante Streamlit y permite consultar documentos PDF y CSV cargados como base de conocimiento.

## URL pública de la aplicación

```text

http://129.80.83.231:8501/ 

```

## Evidencia visual

La siguiente imagen muestra la aplicación funcionando correctamente:

## Funcionalidades verificadas

* La aplicación inicia correctamente en Streamlit.

* El agente puede consultar la base de conocimiento.
* EduBot responde preguntas sobre cursos, certificados, becas, pagos, reembolsos, evaluaciones y soporte técnico.
* La aplicación se encuentra disponible desde una dirección pública en OCI.

![alt text](/screenshots/edubot-funcionando.png)

* La interfaz permite subir documentos PDF y CSV.
* La interfaz permite eliminar documentos cargados.
* La modificación de documentos solo puedee realizarlo un administrador.

![alt text](/screenshots/admin.png)

