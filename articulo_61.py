# -*- coding: utf-8 -*-
"""
Base de conocimiento legal: Capítulo VII, Artículo 61
Ley de Adquisiciones, Arrendamientos, Administración y Enajenación de
Bienes Muebles del Estado de Veracruz de Ignacio de la Llave.

Cada entrada representa una fracción del Art. 61 que todo contrato de
adquisición pública debe formalizar. Esta lista funciona como la "base
vectorial legal" contra la que se compara cada contrato cargado.

NOTA METODOLÓGICA: la ponderación (peso) de cada fracción refleja su
relevancia relativa para el cálculo del semáforo de riesgo, tal como se
describe en el Diagrama RAG del proyecto (Anexo A/B de la Entrega Final):
las cláusulas con mayor impacto legal/económico (p. ej. Causas de
Rescisión) tienen mayor peso que las administrativas (p. ej. Datos de
Facturación).
"""

ARTICULO_61_CLAUSULAS = [
    {
        "fraccion": "I",
        "clave": "objeto_monto",
        "nombre": "Objeto del contrato y monto",
        "peso": 12,
        "descripcion": (
            "El contrato debe definir con precisión el objeto de la prestación "
            "(bienes, obra o servicios contratados) y el monto total u honorarios "
            "pactados, incluyendo el desglose del Impuesto al Valor Agregado (IVA)."
        ),
        "keywords": [
            "objeto y monto", "objeto del contrato", "honorarios", "monto total",
            "prestará servicios", "realizará", "diagnóstico integral", "más el i.v.a",
        ],
    },
    {
        "fraccion": "II",
        "clave": "plazos_entrega",
        "nombre": "Plazos y lugar de entrega",
        "peso": 10,
        "descripcion": (
            "El contrato debe establecer el lugar y la fecha límite de entrega de "
            "los bienes, obra o servicios, así como el domicilio donde se recibirán "
            "los entregables."
        ),
        "keywords": [
            "lugar y fecha de entrega", "fecha límite", "entregará", "a más tardar",
            "se llevará a cabo", "informe final", "fecha de finalización",
        ],
    },
    {
        "fraccion": "III",
        "clave": "forma_pago",
        "nombre": "Forma y lugar de pago",
        "peso": 8,
        "descripcion": (
            "El contrato debe especificar la forma de pago (transferencia, cheque, "
            "exhibiciones), el lugar donde se realizará y las condiciones o "
            "porcentajes de cada pago."
        ),
        "keywords": [
            "forma y lugar de pago", "transferencia bancaria", "clabe", "exhibición",
            "cheque nominativo", "pagos mensuales", "tesorería",
        ],
    },
    {
        "fraccion": "IV",
        "clave": "anticipo",
        "nombre": "Anticipo",
        "peso": 6,
        "descripcion": (
            "El contrato debe indicar si se otorga un anticipo, su porcentaje sobre "
            "el monto total y el momento en que se entrega."
        ),
        "keywords": [
            "anticipo", "por ciento del monto", "para el inicio de los trabajos",
            "a la firma del presente instrumento",
        ],
    },
    {
        "fraccion": "V",
        "clave": "garantias",
        "nombre": "Garantías de cumplimiento",
        "peso": 10,
        "descripcion": (
            "El contrato debe constituir garantías de cumplimiento (póliza de "
            "fianza, carta de crédito) por un porcentaje del monto total, indicando "
            "la institución afianzadora y el número de póliza."
        ),
        "keywords": [
            "garantías", "póliza de fianza", "fianza de cumplimiento",
            "carta de crédito", "afianzadora", "seguros y fianzas",
        ],
    },
    {
        "fraccion": "VI",
        "clave": "modificacion_precio",
        "nombre": "Modificación del precio",
        "peso": 6,
        "descripcion": (
            "El contrato debe prever el mecanismo para ajustar el precio pactado "
            "ante variaciones relevantes (inflación, INPC, cambios normativos)."
        ),
        "keywords": [
            "modificación del precio", "índice nacional de precios al consumidor",
            "inpc", "convenio modificatorio", "ajuste trimestral", "precio firme",
        ],
    },
    {
        "fraccion": "VII",
        "clave": "clausula_penal",
        "nombre": "Cláusula penal (penalizaciones)",
        "peso": 10,
        "descripcion": (
            "El contrato debe fijar una pena convencional o multa aplicable en caso "
            "de retraso o incumplimiento, expresada como porcentaje del monto total."
        ),
        "keywords": [
            "cláusula penal", "pena convencional", "multa", "por cada día de retraso",
            "por cada semana de retraso", "sin perjuicio de la rescisión",
        ],
    },
    {
        "fraccion": "VIII",
        "clave": "derechos_autor",
        "nombre": "Derechos de autor / propiedad intelectual",
        "peso": 8,
        "descripcion": (
            "El contrato debe definir a quién corresponden los derechos de autor y "
            "la propiedad intelectual de los productos, metodologías o desarrollos "
            "generados durante su ejecución."
        ),
        "keywords": [
            "derechos de autor", "propiedad intelectual", "derechos patrimoniales",
            "licencia de uso", "código fuente",
        ],
    },
    {
        "fraccion": "IX",
        "clave": "datos_facturacion",
        "nombre": "Datos de facturación",
        "peso": 4,
        "descripcion": (
            "El contrato debe indicar el nombre y RFC exactos a los que deberán "
            "expedirse los comprobantes fiscales digitales (CFDI)."
        ),
        "keywords": [
            "datos de facturación", "comprobantes fiscales", "cfdi", "rfc:",
            "se expedirán a nombre de",
        ],
    },
    {
        "fraccion": "X",
        "clave": "capacitacion",
        "nombre": "Capacitación / transferencia de conocimientos",
        "peso": 6,
        "descripcion": (
            "El contrato debe prever, cuando aplique, la transferencia de "
            "conocimientos o capacitación al personal de la dependencia contratante."
        ),
        "keywords": [
            "capacitación", "transferencia de conocimientos", "horas de capacitación",
            "manuales de usuario", "personal técnico",
        ],
    },
    {
        "fraccion": "XI",
        "clave": "causas_rescision",
        "nombre": "Causas de rescisión",
        "peso": 12,
        "descripcion": (
            "El contrato debe enumerar las causas que permiten su rescisión "
            "administrativa (incumplimiento, mala fe, quiebra, violación de "
            "confidencialidad, entre otras)."
        ),
        "keywords": [
            "causas de rescisión", "rescisión administrativa", "terminación anticipada",
            "podrá ser rescindido",
        ],
    },
    {
        "fraccion": "XII",
        "clave": "fundamentacion_legal",
        "nombre": "Fundamentación legal y jurisdicción",
        "peso": 8,
        "descripcion": (
            "El contrato debe citar el fundamento legal aplicable (Ley de "
            "Adquisiciones del Estado de Veracruz, artículos 60 y 61) y, en su caso, "
            "la jurisdicción a la que se someten las partes."
        ),
        "keywords": [
            "fundamentación legal", "ley de adquisiciones", "artículos 60 y 61",
            "artículo 61", "jurisdicción", "se someten",
        ],
    },
]

PESO_TOTAL = sum(c["peso"] for c in ARTICULO_61_CLAUSULAS)
assert PESO_TOTAL == 100, f"Los pesos deben sumar 100 (actual: {PESO_TOTAL})"

# Umbrales del semáforo de riesgo (definidos en la Entrega Final, Sección 7.1)
SEMAFORO_RANGOS = [
    (0, 40, "ALTO", "🔴", "Irregularidades críticas"),
    (41, 65, "MEDIO", "🟡", "Irregularidades significativas"),
    (66, 85, "BAJO", "🟠", "Irregularidades menores"),
    (86, 100, "CONFORME", "🟢", "Cumplimiento adecuado"),
]


def clasificar_semaforo(porcentaje: float):
    for lo, hi, nivel, icono, desc in SEMAFORO_RANGOS:
        if lo <= porcentaje <= hi:
            return {"nivel": nivel, "icono": icono, "descripcion": desc}
    return {"nivel": "DESCONOCIDO", "icono": "⚪", "descripcion": "Sin clasificar"}
