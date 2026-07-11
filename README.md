# Dashboard RAG — Detección de Irregularidades Contractuales
Prototipo funcional (MVP) · Seminario de Innovación · Maestría en IA (UNIR)

## ¿Qué es esto?

Una aplicación web (Streamlit) que:
1. Recibe contratos en PDF.
2. Los compara automáticamente contra las 12 fracciones del Art. 61 de la
   Ley de Adquisiciones del Estado de Veracruz (motor RAG: recuperación +
   generación de justificación).
3. Muestra un dashboard con semáforo de riesgo, % de cumplimiento y
   justificación citando la fracción legal.
4. Incluye un módulo opcional de similitud entre contratos.

**Es 100% gratuito**: no usa ninguna API de pago (no requiere OpenAI ni
ninguna llave/API key). La "recuperación semántica" se implementa con
TF-IDF + similitud coseno (scikit-learn), que corre localmente sin costo.

## Archivos del proyecto

```
app.py              -> interfaz Streamlit (el dashboard)
ingest.py           -> extracción de texto y chunking por cláusulas
rag_engine.py        -> el motor RAG (recuperación + scoring + justificación)
articulo_61.py       -> base de conocimiento legal (12 fracciones, pesos)
requirements.txt     -> dependencias a instalar
```

## Opción A — Probarlo tú mismo AHORA MISMO (sin instalar nada)

Puedes correrlo en tu computadora si tienes Python instalado:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abrirá en tu navegador en `http://localhost:8501`. Ahí arrastras los
PDF de los contratos y ves los resultados.

## Opción B — Desplegarlo en internet GRATIS (para que el evaluador lo use)

Vas a usar **Streamlit Community Cloud**, que es gratuito y no pide
tarjeta de crédito. Sigue estos pasos exactamente:

### Paso 1 — Crear una cuenta de GitHub (si no tienes)
1. Ve a https://github.com/signup
2. Crea una cuenta gratuita con tu correo.

### Paso 2 — Crear un repositorio nuevo
1. Ya con sesión iniciada en GitHub, ve a https://github.com/new
2. En "Repository name" escribe: `dashboard-rag-veracruz`
3. Déjalo en "Public" (público).
4. Dale clic en "Create repository".

### Paso 3 — Subir los archivos del proyecto
1. En la página del repositorio recién creado, verás un enlace que dice
   "uploading an existing file". Dale clic (o ve a la pestaña
   "Add file" → "Upload files").
2. Arrastra estos 5 archivos que te entregué:
   - `app.py`
   - `ingest.py`
   - `rag_engine.py`
   - `articulo_61.py`
   - `requirements.txt`
3. Baja hasta el final de la página y dale clic en "Commit changes".

### Paso 4 — Conectar con Streamlit Community Cloud
1. Ve a https://share.streamlit.io/
2. Dale clic en "Sign in" y elige "Continue with GitHub" (usa la misma
   cuenta del Paso 1).
3. Autoriza el acceso cuando te lo pida.
4. Dale clic en "Create app" (o "New app").
5. Selecciona:
   - Repository: `tu-usuario/dashboard-rag-veracruz`
   - Branch: `main`
   - Main file path: `app.py`
6. Dale clic en "Deploy".

### Paso 5 — Esperar y compartir
1. Espera 1–3 minutos mientras Streamlit instala las dependencias.
2. Cuando termine, te dará una URL pública como:
   `https://dashboard-rag-veracruz-xxxxx.streamlit.app`
3. **Esa es la URL que compartes con tu evaluador.** Cualquiera con el
   enlace puede subir los 4 contratos PDF y ver los resultados en vivo.

### Notas importantes
- Cada vez que subas un cambio a GitHub, Streamlit Cloud actualiza la app
  automáticamente en 1-2 minutos.
- Si la app "se duerme" por inactividad (pasa tras varios días sin uso),
  basta con abrir la URL y darle clic en "Wake up app" (tarda ~30 seg).
- No necesitas dar de alta ninguna tarjeta de crédito ni API key para
  esta versión del prototipo.

## ¿Cómo interpretar los resultados?

| % Cumplimiento | Semáforo      | Nivel de riesgo |
|-----------------|---------------|------------------|
| 0% – 40%        | 🔴 ALTO       | Irregularidades críticas |
| 41% – 65%       | 🟡 MEDIO      | Irregularidades significativas |
| 66% – 85%       | 🟠 BAJO       | Irregularidades menores |
| 86% – 100%      | 🟢 CONFORME   | Cumplimiento adecuado |

## Limitaciones honestas de este prototipo (para mencionar en el video)

- Usa **TF-IDF** en lugar de embeddings de OpenAI (como se describe en la
  arquitectura de producción de la Entrega Final) para que el despliegue
  sea 100% gratuito. Es una simplificación técnica legítima de un MVP,
  no una arquitectura de producción final.
- El chunking por cláusulas asume el formato típico de contratos públicos
  mexicanos (cláusulas numeradas con ordinales: PRIMERA, SEGUNDA…). Un
  contrato con formato muy distinto podría no segmentarse correctamente.
- La detección de colusión (similitud entre contratos) es orientativa;
  un umbral de 0.92 es el mismo que se documentó en la Entrega Final,
  pero no ha sido validado estadísticamente con un corpus más amplio.
- Los resultados que arroja esta versión sobre tus 4 contratos reales
  **son reales, calculados en el momento**, no los valores de ejemplo
  (Faithfulness=0.89, Kappa=0.78, etc.) que aparecen en el documento de
  la Entrega Final, los cuales son ilustrativos del diseño de evaluación
  propuesto, no mediciones de este prototipo específico.
