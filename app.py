# -*- coding: utf-8 -*-
"""
Dashboard RAG — Detección automática de irregularidades contractuales
Prototipo funcional MVP | Seminario de Innovación | Maestría en IA — UNIR

Equipo: Méndez Sánchez, A. · Ramírez Ríos, R. · Torres Tejada, F. A. · Hernández Montiel, E.
"""
import json
import os
import tempfile
from datetime import datetime

import streamlit as st

from ingest import load_contract
from rag_engine import evaluate_contract, compute_collusion_matrix
from articulo_61 import ARTICULO_61_CLAUSULAS

st.set_page_config(
    page_title="Dashboard RAG · Irregularidades Contractuales",
    page_icon="🚦",
    layout="wide",
)

FEEDBACK_FILE = "feedback.json"

# ----------------------------------------------------------------------
# Estilos
# ----------------------------------------------------------------------
st.markdown("""
<style>
.big-badge { font-size: 2.2rem; font-weight: 700; }
.metric-card {
    background: #f2f6fb; border-radius: 10px; padding: 1rem 1.2rem;
    border: 1px solid #d8e3f0;
}
.clause-row { padding: 6px 0; border-bottom: 1px solid #eee; }
</style>
""", unsafe_allow_html=True)

st.title("🚦 Dashboard RAG — Detección de Irregularidades Contractuales")
st.caption(
    "Prototipo funcional (MVP) · Contraste automático de contratos contra el "
    "Capítulo VII, Artículo 61 de la Ley de Adquisiciones del Estado de Veracruz "
    "· Seminario de Innovación, Maestría en Inteligencia Artificial (UNIR)"
)

with st.expander("ℹ️ Cómo funciona este prototipo (léeme antes de evaluar)", expanded=False):
    st.markdown("""
Este prototipo implementa el pipeline **RAG (Retrieval-Augmented Generation)** descrito en la
Entrega Final del proyecto, en una versión **100% gratuita y sin necesidad de API key**:

1. **Ingesta**: se extrae el texto del PDF con PyMuPDF y se segmenta en cláusulas
   (chunking semántico por encabezados PRIMERA, SEGUNDA, TERCERA…).
2. **Recuperación (Retriever)**: para cada una de las 12 fracciones del Art. 61 se busca,
   primero por coincidencia literal de términos clave y, si no la hay, por **similitud
   semántica TF-IDF/coseno** — el equivalente ligero de una base vectorial de embeddings.
3. **Generación aumentada**: con la cláusula recuperada se redacta una justificación
   citando la fracción del Art. 61 correspondiente.
4. **Cálculo de cumplimiento**: se pondera cada fracción según su relevancia legal y se
   asigna un semáforo de riesgo.

*Nota: esta versión usa TF-IDF en lugar de embeddings de OpenAI para que el despliegue sea
gratuito. La arquitectura de producción descrita en el documento de la Entrega Final
(MongoDB Atlas Vector Search + GPT-4o-mini) sigue el mismo principio con mayor capacidad
semántica.*
""")

# ----------------------------------------------------------------------
# Carga de contratos
# ----------------------------------------------------------------------
st.subheader("1. Panel de carga")
uploaded_files = st.file_uploader(
    "Arrastra o selecciona los contratos en PDF a evaluar",
    type=["pdf"],
    accept_multiple_files=True,
)

if "resultados" not in st.session_state:
    st.session_state["resultados"] = {}
    st.session_state["contratos_cargados"] = {}

if uploaded_files:
    with st.spinner("Procesando contratos (extracción, chunking y evaluación RAG)..."):
        for f in uploaded_files:
            if f.name in st.session_state["resultados"]:
                continue
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(f.read())
                tmp_path = tmp.name
            contract = load_contract(tmp_path)
            result = evaluate_contract(contract)
            st.session_state["contratos_cargados"][f.name] = contract
            st.session_state["resultados"][f.name] = result
            os.unlink(tmp_path)
    st.success(f"{len(uploaded_files)} contrato(s) procesado(s).")

resultados = st.session_state["resultados"]

if not resultados:
    st.info("Carga uno o más contratos en PDF para iniciar el análisis.")
    st.stop()

# ----------------------------------------------------------------------
# Panel de resultados (tabla)
# ----------------------------------------------------------------------
st.subheader("2. Panel de resultados")

tabla_rows = []
for fname, r in resultados.items():
    tabla_rows.append({
        "Archivo": fname,
        "Contrato": r["meta"]["numero_contrato"],
        "Semáforo": f"{r['semaforo']['icono']} {r['semaforo']['nivel']}",
        "% Cumplimiento": r["porcentaje_cumplimiento"],
        "Cláusulas": f"{r['num_presentes']}/{r['num_total']}",
    })
st.dataframe(tabla_rows, use_container_width=True, hide_index=True)

nombre_sel = st.selectbox("Selecciona un contrato para ver el detalle:", list(resultados.keys()))
r = resultados[nombre_sel]

# ----------------------------------------------------------------------
# Detalle del contrato seleccionado
# ----------------------------------------------------------------------
st.subheader(f"3. Detalle — {r['meta']['numero_contrato']}")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='metric-card'><span class='big-badge'>{r['semaforo']['icono']}</span><br>"
                f"<b>{r['semaforo']['nivel']}</b><br>{r['semaforo']['descripcion']}</div>",
                unsafe_allow_html=True)
with col2:
    st.metric("Porcentaje de cumplimiento", f"{r['porcentaje_cumplimiento']}%")
with col3:
    st.metric("Cláusulas acreditadas", f"{r['num_presentes']} / {r['num_total']}")

st.markdown(f"**Expediente:** {r['meta']['expediente']}  |  **Monto detectado:** {r['meta']['monto']}")
st.markdown(f"**Resumen:** {r['resumen']}")

st.markdown("#### Reporte del Artículo 61 (cláusula por cláusula)")
for d in r["detalle_clausulas"]:
    icon = "✅" if d["presente"] else "❌"
    with st.container():
        st.markdown(
            f"<div class='clause-row'>{icon} <b>Fracción {d['fraccion']}</b> — "
            f"{d['nombre']} (peso {d['peso']}) &nbsp;|&nbsp; "
            f"cláusula del contrato: <i>{d['cláusula_contrato']}</i></div>",
            unsafe_allow_html=True,
        )
        st.caption(f"Justificación RAG: {d['justificacion']}")

# ----------------------------------------------------------------------
# Mecanismo de feedback del experto
# ----------------------------------------------------------------------
st.markdown("#### 4. Mecanismo de feedback del experto")
colf1, colf2 = st.columns([3, 1])
with colf1:
    st.write("¿Es correcta esta detección? Tu respuesta alimenta el ciclo de mejora continua (Kaizen).")
with colf2:
    fb_col1, fb_col2 = st.columns(2)
    if fb_col1.button("✅ Sí, correcta", key=f"ok_{nombre_sel}"):
        entry = {"contrato": r["meta"]["numero_contrato"], "veredicto": "correcta",
                 "timestamp": datetime.utcnow().isoformat()}
        data = json.load(open(FEEDBACK_FILE)) if os.path.exists(FEEDBACK_FILE) else []
        data.append(entry)
        json.dump(data, open(FEEDBACK_FILE, "w"), ensure_ascii=False, indent=2)
        st.success("Feedback registrado. ¡Gracias!")
    if fb_col2.button("❌ No, corregir", key=f"bad_{nombre_sel}"):
        entry = {"contrato": r["meta"]["numero_contrato"], "veredicto": "incorrecta",
                 "timestamp": datetime.utcnow().isoformat()}
        data = json.load(open(FEEDBACK_FILE)) if os.path.exists(FEEDBACK_FILE) else []
        data.append(entry)
        json.dump(data, open(FEEDBACK_FILE, "w"), ensure_ascii=False, indent=2)
        st.warning("Feedback registrado como desacuerdo. Se revisará en la Sprint Retrospective.")

# ----------------------------------------------------------------------
# Módulo de similitud entre contratos (opcional en el MVP)
# ----------------------------------------------------------------------
if len(resultados) >= 2:
    st.subheader("5. Módulo de similitud entre contratos (opcional en el MVP)")
    st.caption("Similitud coseno TF-IDF entre el texto completo de cada par de contratos cargados. "
               "Pares con similitud > 0.92 se marcan como posibles indicios de colusión (bid rigging).")
    contratos_list = list(st.session_state["contratos_cargados"].values())
    pares = compute_collusion_matrix(contratos_list)
    st.dataframe(pares, use_container_width=True, hide_index=True)

st.divider()
st.caption(
    "Prototipo desarrollado como parte del Trabajo de Innovación — Seminario de Innovación, "
    "Maestría en Inteligencia Artificial, UNIR. Este sistema es una herramienta de apoyo a la "
    "decisión humana y no sustituye el criterio de un auditor o abogado especializado."
)
