"""Combina las señales del Agente de Noticias y el Agente de Fundamentales.

Ver prompts/spec-agentes-noticias-fundamentales.md §3: define qué significa
"coincidir" entre ambos agentes, y traduce el resultado al formato simple
('comprar' / 'vender' / 'esperar') que ya consume risk.evaluar_orden().
"""

from dataclasses import asdict, dataclass
from datetime import datetime

from . import fundamentales as fundamentales_mod
from .noticias import CandidataNoticia


@dataclass
class SenalCombinada:
    ticker: str
    veredicto_combinado: str
    noticia: dict
    fundamentales: dict
    confianza_combinada: float
    senal_risk: str
    timestamp: str


def _decidir(noticia: CandidataNoticia, veredicto_fund) -> tuple[str, str]:
    if noticia.direccion == "positivo" and veredicto_fund.veredicto == "solida":
        return "candidata_para_riesgo", "comprar"
    if noticia.direccion == "negativo" and veredicto_fund.veredicto == "debil":
        return "candidata_para_riesgo", "vender"
    if veredicto_fund.veredicto == "dudosa":
        return "revision_humana", "esperar"
    return "descartada", "esperar"


def combinar(candidatas_noticias: list[CandidataNoticia]) -> list[SenalCombinada]:
    resultado = []
    for noticia in candidatas_noticias:
        if noticia.decision != "candidata_generada":
            continue

        veredicto_fund = fundamentales_mod.analizar_empresa(noticia.ticker)
        veredicto_combinado, senal_risk = _decidir(noticia, veredicto_fund)
        confianza_combinada = round((noticia.confianza + veredicto_fund.confianza) / 2, 2)

        resultado.append(SenalCombinada(
            ticker=noticia.ticker,
            veredicto_combinado=veredicto_combinado,
            noticia=asdict(noticia),
            fundamentales=veredicto_fund.__dict__,
            confianza_combinada=confianza_combinada,
            senal_risk=senal_risk,
            timestamp=datetime.now().isoformat(timespec="seconds"),
        ))
    return resultado


def resolver_conflicto(senal_tecnica: str, senal_combinada: str) -> str:
    """Requisito heredado: si técnica y noticias+fundamentales se contradicen, no operar."""
    if senal_combinada == "esperar" or senal_tecnica == "esperar":
        return senal_tecnica if senal_combinada == "esperar" else senal_combinada
    if senal_tecnica == senal_combinada:
        return senal_tecnica
    return "esperar"
