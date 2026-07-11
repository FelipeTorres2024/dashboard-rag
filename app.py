# -*- coding: utf-8 -*-
"""
Dashboard RAG — Detección automática de irregularidades contractuales
Prototipo funcional MVP | Seminario de Innovación | Maestría en IA — UNIR

Equipo: Méndez Sánchez, A. · Ramírez Ríos, R. · Torres Tejada, F. A. · Hernández Montiel, E.
"""
import json
import os
import tempfile
import logging
from datetime import datetime

import streamlit as st

from ingest import load_contract
from rag_engine import evaluate_contract, compute_collusion_matrix
from articulo_61 import ARTICULO_61_CLAUSULAS

# REQUISITO STREAMLIT: Debe ser la primera instrucción ejecutable
st.set_page_config(
    page_title="Dashboard RAG · Irregularidades Contractuales",
    page_icon="🚦",
    layout="wide",
)

FEEDBACK_FILE = "feedback.json"

# ======================================================================
# CONTROL DE ACCESO Y SISTEMA DE LOGS
# ======================================================================
logging.basicConfig(
    filename="registro_uso.txt", 
    level=logging.INFO, 
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

USUARIOS_VALIDOS = {
    "admin": "RAG_Admin_2026",
    "evaluador1": "EvalPassword123",
    "profesor": "DemoClase456"
}

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = ""

def verificar_credenciales():
    user = st.session_state["input_user"].strip()
    password = st.session_state["input_pass"].strip()
    
    if user in USUARIOS_VALIDOS and USUARIOS_VALIDOS[user] == password:
        st.session_state["autenticado"] = True
        st.session_state["usuario_actual"] = user
        logging.info(f"LOGIN EXITOSO - Usuario: '{user}' ingresó al sistema.")
    else:
        st.session_state["autenticado"] = False
        if user:
            logging.warning(f"INTENTO FALLIDO - Alguien intentó ingresar con el usuario: '{user}'.")
        st.error("⚠️ Usuario o contraseña incorrectos")

# ======================================================================
# LÓGICA DE RENDERIZADO (LOGIN O DASHBOARD)
# ======================================================================
if not st.session_state["autenticado"]:
    # --- PANTALLA DE LOGIN ---
    st.title("🔒 Acceso Protegido — Dashboard RAG")
    st.subheader("Por favor, inicia sesión para continuar con la evaluación.")
    
    st.text_input("Nombre de Usuario", key="input_user")
    st.text_input("Contraseña", type="password", key="input_pass")
    st.button("Ingresar", on_click=verificar_credenciales)

else:
    # --- DASHBOARD DE TU PROYECTO ORIGINAL (IDENTADO CORRECTAMENTE) ---
    
    # Barra lateral de navegación / sesión
    with st.sidebar:
        st.write(f"👤 Conectado como: **{st.session_state['usuario_actual']}**")
        if st.button("Cerrar Sesión"):
            logging.info(f"LOGOUT - Usuario: '{st.session_state['usuario_actual']}' cerró sesión.")
            st.session_state["autenticado"] = False
            st.session_state["usuario_actual"] = ""
            st.rerun()

    # Estilos
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
        
        1. **Ingesta**: se extrae el texto del PDF con PyMuPDF y se segmenta en cláusulas (chunking semántico por encabezados PRIMERA, SEGUNDA, TERCERA…).
        2. **Recuperación (Retriever)**: para cada una de las 12 fracciones del Art. 61 se busca, primero por coincidencia literal de términos clave y, si no la hay, por **similitud semántica TF-IDF/coseno** — el equivalente ligero de una base vectorial de embeddings.
        3. **Generación aumentada**: con la cláusula recuperada se redacta una justificación citando la fracción del Art. 61 correspondiente.
        4. **Cálculo de cumplimiento**: se pondera cada fracción según su relevancia legal y se asigna un semáforo de riesgo.
        
        *Nota: esta versión usa TF-IDF en lugar de embeddings de OpenAI para que el despliegue sea gratuito. La arquitectura de producción descrita en el documento de la Entrega Final (MongoDB Atlas Vector Search + GPT-4o-mini) sigue el mismo principio con mayor capacidad semántica.*
        """)

    # Carga de contratos
    st.subheader("1. Panel de carga")
    uploaded_files = st.file_uploader(
        "Arrastra o selecciona los contratos en PDF a evaluar",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if "resultados" not in st.session_state:
        st.session_state["resultados"] = {}
    if "contratos_cargados" not in st.session_state:
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
                logging.info(f"PROCESAMIENTO - Usuario '{st.session_state['usuario_actual']}' procesó el archivo: {f.name}")
            st.success(f"{len(uploaded_files)} contrato(s) procesado(s).")

    resultados = st.session_state["resultados"]

    if not resultados:
        st.info("Carga uno o más contratos en PDF para iniciar el análisis.")
        st.stop()

    # Panel de resultados (tabla)
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

    # Detalle del contrato seleccionado
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

    st.markdown(f"**Expediente:** {r['meta']['expediente']} | **Monto detectado:** {r['meta']['monto']}")
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

    # Mecanismo de feedback del experto
    st.markdown("#### 4. Mecanismo de feedback del experto")
    colf1, colf2 = st.columns([3, 1])
    with colf1:
        st.write("¿Es correcta esta detección? Tu respuesta alimenta el ciclo de mejora continua (Kaizen).")
    with colf2:
        fb_col1, fb_col2 = st.columns(2)
        if fb_col1.button("✅ Sí, correcta", key=f"ok_{nombre_sel}"):
            entry = {"contrato": r["meta"]["numero_contrato"], "veredicto": "correcta", "timestamp": datetime.utcnow().isoformat()}
            data = json.load(open(FEEDBACK_FILE)) if os.path.exists(FEEDBACK_FILE) else []
            data.append(entry)
            json.dump(data, open(FEEDBACK_FILE, "w"), ensure_ascii=False, indent=2)
            logging.info(f"FEEDBACK - Usuario '{st.session_state['usuario_actual']}' aprobó la detección del contrato: {r['meta']['numero_contrato']}")
            st.success("Feedback registrado. ¡Gracias!")
        if fb_col2.button("❌ No, corregir", key=f"bad_{nombre_sel}"):
            entry = {"contrato": r["meta"]["numero_contrato"], "veredicto": "incorrecta", "timestamp": datetime.utcnow().isoformat()}
            data = json.load(open(FEEDBACK_FILE)) if os.path.exists(FEEDBACK_FILE) else []
            data.append(entry)
            json.dump(data, open(FEEDBACK_FILE, "w"), ensure_ascii=False, indent=2)

