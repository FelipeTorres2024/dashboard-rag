# -*- coding: utf-8 -*-
"""
Motor RAG (Retrieval-Augmented Generation) del sistema.

Componente de RECUPERACIÓN (retriever):
  Para cada fracción del Art. 61, se recupera la cláusula del contrato
  semánticamente más cercana usando similitud TF-IDF/coseno sobre los
  chunks generados por `ingest.chunk_by_clauses`. Este es el mismo
  principio que un retriever de embeddings sobre una base vectorial
  (MongoDB Atlas Vector Search en la arquitectura de producción descrita
  en la Entrega Final): aquí se implementa con TF-IDF para que el
  prototipo funcione sin necesidad de una API key de pago, permitiendo
  un despliegue 100% gratuito.

Componente de GENERACIÓN AUMENTADA (generator):
  Con el chunk recuperado y su score de similitud, se genera una
  justificación textual estructurada que cita la fracción del Art. 61 y
  la cláusula (o ausencia de ella) en el contrato — el equivalente
  simplificado del agente LangChain + LLM descrito en la arquitectura de
  producción.

Si se define la variable de entorno OPENAI_API_KEY, el motor puede
opcionalmente delegar la redacción de la justificación a un LLM real
(ver `llm_backend.py`); si no está definida, usa generación basada en
plantillas (100% gratuita, sin llamadas externas).
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from articulo_61 import ARTICULO_61_CLAUSULAS, clasificar_semaforo

# Umbral de similitud semántica (fallback) por debajo del cual, sin
# coincidencia literal de palabras clave, se considera que la cláusula
# NO está presente en el contrato. Se calibró empíricamente sobre el
# corpus de 4 contratos reales de Veracruz para evitar falsos positivos
# entre cláusulas temáticamente cercanas (p. ej. "Anticipo" vs.
# "Modificación del precio").
SIM_THRESHOLD = 0.50


def _find_keyword_chunk(contract_chunks: list, keywords: list):
    """Busca en TODOS los chunks del contrato una coincidencia literal de
    alguna palabra/frase clave. Devuelve el primer chunk que la contenga,
    priorizando coincidencias en el título de la cláusula."""
    kws = [k.lower() for k in keywords]
    # 1) Prioridad: coincidencia en el título de la cláusula
    for ch in contract_chunks:
        title_low = ch["titulo"].lower()
        if any(kw in title_low for kw in kws):
            return ch
    # 2) Coincidencia en el cuerpo de la cláusula
    for ch in contract_chunks:
        body_low = ch["texto"].lower()
        if any(kw in body_low for kw in kws):
            return ch
    return None


def retrieve_best_match(clause_def: dict, contract_chunks: list, vectorizer, chunk_vectors):
    """Recupera el chunk del contrato más similar semánticamente a una fracción del Art. 61
    (usado únicamente como respaldo cuando no hay coincidencia literal de palabras clave)."""
    query_vec = vectorizer.transform([clause_def["descripcion"] + " " + " ".join(clause_def["keywords"])])
    sims = cosine_similarity(query_vec, chunk_vectors)[0]
    best_idx = int(np.argmax(sims)) if len(sims) else -1
    best_score = float(sims[best_idx]) if best_idx >= 0 else 0.0
    best_chunk = contract_chunks[best_idx] if best_idx >= 0 else None
    return best_chunk, best_score


def evaluate_contract(contract: dict) -> dict:
    """
    Ejecuta el pipeline RAG completo sobre un contrato ya cargado
    (ver ingest.load_contract) y devuelve el reporte de cumplimiento
    del Art. 61: cláusulas presentes/faltantes, porcentaje ponderado,
    semáforo de riesgo y justificaciones citando la fracción legal.
    """
    chunks = contract["chunks"]
    chunk_texts = [c["texto"] for c in chunks]

    if not chunk_texts:
        chunk_texts = [""]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        min_df=1,
    )
    chunk_vectors = vectorizer.fit_transform(chunk_texts)

    detalle = []
    peso_presente = 0
    for clause_def in ARTICULO_61_CLAUSULAS:
        kw_chunk = _find_keyword_chunk(chunks, clause_def["keywords"])
        if kw_chunk is not None:
            presente = True
            match_chunk = kw_chunk
            score = 1.0  # coincidencia literal: confianza máxima
            metodo = "coincidencia literal"
        else:
            best_chunk, score = retrieve_best_match(clause_def, chunks, vectorizer, chunk_vectors)
            presente = score >= SIM_THRESHOLD
            match_chunk = best_chunk
            metodo = "similitud semántica"

        if presente:
            peso_presente += clause_def["peso"]
            justificacion = (
                f"Se localizó la fracción {clause_def['fraccion']} "
                f"({clause_def['nombre']}) en la cláusula "
                f"\"{match_chunk['ordinal']}. {match_chunk['titulo']}\" del contrato "
                f"({metodo}, score = {score:.2f})."
            )
        else:
            justificacion = (
                f"El contrato no acredita de forma explícita la fracción "
                f"{clause_def['fraccion']} del Art. 61 ({clause_def['nombre']}). "
                f"La coincidencia más cercana fue "
                f"\"{match_chunk['ordinal']}. {match_chunk['titulo']}\" "
                f"(similitud = {score:.2f}), insuficiente para considerarla acreditada."
                if match_chunk else
                f"El contrato no acredita la fracción {clause_def['fraccion']} "
                f"del Art. 61 ({clause_def['nombre']}); no se encontró ninguna "
                f"cláusula relacionada."
            )

        detalle.append({
            "fraccion": clause_def["fraccion"],
            "nombre": clause_def["nombre"],
            "peso": clause_def["peso"],
            "presente": presente,
            "similitud": round(score, 3),
            "cláusula_contrato": f"{match_chunk['ordinal']}. {match_chunk['titulo']}" if match_chunk else "N/D",
            "justificacion": justificacion,
        })

    porcentaje = round(peso_presente, 1)
    semaforo = clasificar_semaforo(porcentaje)
    faltantes = [d for d in detalle if not d["presente"]]

    if faltantes:
        resumen = (
            f"El contrato omite {len(faltantes)} de {len(detalle)} fracciones "
            f"obligatorias del Art. 61, incluyendo: " +
            ", ".join(f"\"{d['nombre']}\" (fracción {d['fraccion']})" for d in faltantes[:3]) +
            (f", entre otras." if len(faltantes) > 3 else ".")
        )
    else:
        resumen = "El contrato acredita la totalidad de las fracciones obligatorias del Art. 61."

    return {
        "meta": contract["meta"],
        "porcentaje_cumplimiento": porcentaje,
        "semaforo": semaforo,
        "num_presentes": len(detalle) - len(faltantes),
        "num_total": len(detalle),
        "detalle_clausulas": detalle,
        "faltantes": faltantes,
        "resumen": resumen,
    }


def compute_collusion_matrix(contracts: list) -> list:
    """
    Módulo de detección de similitud anómala entre proveedores (opcional
    en el MVP): calcula la similitud coseno TF-IDF entre el texto
    completo de cada par de contratos. Pares con similitud > 0.92 se
    marcan como sospechosos de posible colusión (bid rigging).
    """
    texts = [c["texto_completo"] for c in contracts]
    names = [c["meta"]["numero_contrato"] for c in contracts]
    if len(texts) < 2:
        return []
    vectorizer = TfidfVectorizer(lowercase=True, strip_accents="unicode", ngram_range=(1, 2))
    vectors = vectorizer.fit_transform(texts)
    sim_matrix = cosine_similarity(vectors)

    pairs = []
    n = len(texts)
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append({
                "contrato_a": names[i],
                "contrato_b": names[j],
                "similitud": round(float(sim_matrix[i][j]), 3),
                "sospechoso": bool(sim_matrix[i][j] > 0.92),
            })
    return pairs
