"""Lista de fuentes con credibilidad verificada, usada por el Agente de Noticias.

Ver prompts/spec-agentes-noticias-fundamentales.md §1.6: solo una fuente primaria o de
agencia reconocida cuenta por defecto como confianza alta. Todo lo demás (redes
sociales, blogs sin historial) se trata como no verificado.
"""

AGENCIAS_RECONOCIDAS = {
    "reuters",
    "bloomberg",
    "dow jones",
    "the wall street journal",
    "associated press",
    "benzinga",
    "sec",
    "business wire",
    "pr newswire",
    "globe newswire",
}


def tipo_fuente(nombre_fuente: str) -> str:
    nombre = (nombre_fuente or "").strip().lower()
    if any(agencia in nombre for agencia in AGENCIAS_RECONOCIDAS):
        return "agencia"
    return "red_social_no_verificada"


def es_fuente_de_confianza_alta(nombre_fuente: str) -> bool:
    return tipo_fuente(nombre_fuente) == "agencia"
