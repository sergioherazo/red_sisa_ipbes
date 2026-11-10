# Mapa IPBES · Red SISA

Página para que cada semillero se identifique y ubique su trabajo en el marco IPBES: una categoría principal y hasta tres secundarias. Un QR en la lona lleva a la página; la pestaña "Mapa de la red" muestra lo que van respondiendo, como la lona pero actualizado.

Cómo está armado (todo gratuito):

- **Página**: HTML estático en GitHub Pages (`index.html`, `datos.js`, `config.js`).
- **Respuestas**: una tabla en Supabase. Quien abre el QR solo puede enviar; no puede leer, editar ni borrar. Nombre y correo de contacto no se muestran públicamente.
- **Python**: `exportar_respuestas.py` baja todo a un Excel plano; `generar_qr.py` crea el QR.

## Paso a paso

**1. Crear la base de datos.** Entra a supabase.com, crea un proyecto y abre *SQL Editor*. Pega el contenido de `supabase.sql` y ejecútalo.

**2. Conectar la página.** En Supabase ve a *Project Settings > API*. Copia el *Project URL* y la clave *anon public* en `config.js`. Esa clave es pública por diseño: las reglas del paso 1 solo le permiten enviar respuestas.

**3. Publicar en GitHub.** Crea un repositorio (por ejemplo `red-sisa-ipbes`) y sube estos archivos. En *Settings > Pages* elige *Deploy from a branch*, rama `main`, carpeta `/ (root)`. En un par de minutos la página queda en `https://TU-USUARIO.github.io/red-sisa-ipbes/`.

**4. Probar.** Abre la página, envía una respuesta de prueba y mira la pestaña "Mapa de la red". Luego borra la fila de prueba en Supabase (*Table Editor > respuestas*).

**5. Generar el QR.**
```
pip install "qrcode[pil]"
python generar_qr.py https://TU-USUARIO.github.io/red-sisa-ipbes/
```
Sale `qr_red_sisa.png`, en alta resolución, listo para la lona.

**6. Exportar a Excel.** Las claves se leen desde variables de entorno. Usa la clave `service_role` (*Project Settings > API*). Es secreta: no la pongas en ningún archivo del repositorio.
```
export SUPABASE_URL="https://xxxx.supabase.co"
export SUPABASE_SERVICE_KEY="..."
python exportar_respuestas.py
```
El Excel trae tres hojas: *Respuestas actuales* (la última de cada semillero, con contacto y comparación con la asignación previa), *Pendientes* e *Historial*.

## Cómo funciona

- **Lista de semilleros**: 42 semilleros que presentaron, asistieron a las sesiones o se inscribieron al Diplomado, sin los 6 retirados. Está en `datos.js`; edítala para sumar o quitar. Quien no aparezca puede escribir su nombre y queda marcado "Fuera de la lista base".
- **Una respuesta por semillero**: si vuelve a responder, la última reemplaza la anterior en el mapa. El historial queda en Supabase.
- **Asignación previa**: viene de la base de facultades (categoría y complementaria). La pestaña de resultados la compara con lo que eligió cada semillero: Sí, Parcial o No.
- **Categorías**: son las de la lona. Las descripciones de la pantalla son redacción propia y se ajustan en `datos.js`.

## Tener en cuenta

- Cualquiera con el enlace puede enviar una respuesta, y el sistema no verifica quién es. Si un semillero se equivoca o alguien responde por otro, basta con que se vuelva a enviar.
- Los comentarios del paso 3 se muestran en la tabla de resultados.
- En el plan gratuito, Supabase pausa los proyectos tras una semana sin actividad. Se reactivan con un clic desde su panel.
- Sin configurar `config.js`, la página funciona en modo de prueba: las respuestas quedan solo en el navegador.
