# -*- coding: utf-8 -*-
"""
Módulo de ingesta: extracción de texto (PyMuPDF) y chunking semántico
por cláusulas contractuales, tal como se describe en la Entrega Final
(Sección 7.1, Componente 2: Chunking semántico).
"""
import re
import fitz  # PyMuPDF

# Ordinales usados típicamente en contratos públicos mexicanos para
# encabezar cada cláusula. El chunker detecta estos patrones para
# respetar los límites naturales de las estipulaciones contractuales.
ORDINALES = [
    "PRIMERA", "SEGUNDA", "TERCERA", "CUARTA", "QUINTA", "SEXTA",
    "SÉPTIMA", "SEPTIMA", "OCTAVA", "NOVENA", "DÉCIMA PRIMERA",
    "DECIMA PRIMERA", "DÉCIMA SEGUNDA", "DECIMA SEGUNDA", "DÉCIMA",
    "DECIMA",
]

CLAUSE_HEADER_RE = re.compile(
    r"(?P<ordinal>" + "|".join(sorted(ORDINALES, key=len, reverse=True)) +
    r")\.\s+(?P<titulo>[A-ZÁÉÍÓÚÑ,()/\s]{3,60}?)\.\s",
    re.UNICODE,
)


def extract_text(pdf_path: str) -> str:
    """Extrae el texto completo de un PDF nativo con PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    doc.close()
    # Normalización básica: colapsar espacios múltiples y saltos de línea sueltos
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text


def extract_metadata(text: str) -> dict:
    """Extrae metadatos básicos del encabezado del contrato."""
    meta = {}
    m = re.search(r"No\.\s*de\s*Contrato:\s*([A-Z0-9/\-]+)", text, re.IGNORECASE)
    meta["numero_contrato"] = m.group(1) if m else "N/D"
    m = re.search(r"Expediente:\s*([A-Z0-9/\-]+)", text, re.IGNORECASE)
    meta["expediente"] = m.group(1) if m else "N/D"
    # Título: primera línea larga en mayúsculas antes de "No. de Contrato"
    m = re.search(r"^(.{10,120}?)(?:\n|No\. de Contrato)", text)
    meta["titulo"] = m.group(1).strip() if m else "Contrato sin título detectado"
    m = re.search(r"monto\s+(?:total\s+)?(?:pactado\s+)?(?:por|de|es)\s+de\s+\$?([\d,]+\.\d{2})",
                  text, re.IGNORECASE)
    meta["monto"] = f"${m.group(1)} MXN" if m else "N/D"
    return meta


def chunk_by_clauses(text: str) -> list:
    """
    Segmenta el texto del contrato en cláusulas individuales usando los
    encabezados ordinales (PRIMERA, SEGUNDA, ...). Devuelve una lista de
    dicts {ordinal, titulo, texto}.
    """
    matches = list(CLAUSE_HEADER_RE.finditer(text))
    chunks = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        chunks.append({
            "ordinal": m.group("ordinal"),
            "titulo": m.group("titulo").strip(),
            "texto": body,
        })
    # Fallback: si no se detectaron cláusulas (formato atípico), usar
    # párrafos como chunks para no perder cobertura de recuperación.
    if not chunks:
        paras = [p.strip() for p in text.split("\n") if len(p.strip()) > 40]
        chunks = [{"ordinal": f"P{i+1}", "titulo": "", "texto": p} for i, p in enumerate(paras)]
    return chunks


def load_contract(pdf_path: str) -> dict:
    text = extract_text(pdf_path)
    meta = extract_metadata(text)
    chunks = chunk_by_clauses(text)
    return {"path": pdf_path, "texto_completo": text, "meta": meta, "chunks": chunks}
