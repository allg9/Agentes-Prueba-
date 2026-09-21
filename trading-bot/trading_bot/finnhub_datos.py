"""Acceso a datos de Finnhub (nivel gratuito: 60 llamadas/minuto).

Usado por el Agente de Fundamentales para valoración y comparación sectorial
(prompts/spec-agentes-noticias-fundamentales.md §2.3).
"""

import statistics

import requests

from . import config

BASE_URL = "https://finnhub.io/api/v1"


def _get(ruta: str, **parametros) -> dict:
    parametros["token"] = config.FINNHUB_API_KEY
    respuesta = requests.get(f"{BASE_URL}{ruta}", params=parametros, timeout=10)
    respuesta.raise_for_status()
    return respuesta.json()


def perfil(ticker: str) -> dict:
    return _get("/stock/profile2", symbol=ticker)


def metricas(ticker: str) -> dict:
    return _get("/stock/metric", symbol=ticker, metric="all").get("metric", {})


def pares_sectoriales(ticker: str) -> list[str]:
    pares = _get("/stock/peers", symbol=ticker)
    return [p for p in pares if p != ticker][:8]


def _primero_disponible(metricas_dict: dict, *claves) -> float | None:
    for clave in claves:
        valor = metricas_dict.get(clave)
        if valor is not None:
            return valor
    return None


def pe_ratio(metricas_dict: dict) -> float | None:
    return _primero_disponible(metricas_dict, "peTTM", "peBasicExclExtraTTM", "peExclExtraTTM")


def ev_ebitda(metricas_dict: dict) -> float | None:
    return _primero_disponible(metricas_dict, "evEbitdaTTM", "currentEv/EbitdaTTM")


def peg_ratio(metricas_dict: dict) -> float | None:
    return _primero_disponible(metricas_dict, "pegRatio", "pegTTM")


def medianas_sector(ticker: str) -> dict:
    try:
        pares = pares_sectoriales(ticker)
    except requests.RequestException:
        return {"pe_mediana_sector": None, "ev_ebitda_mediana_sector": None}

    pes, ev_ebitdas = [], []
    for par in pares:
        try:
            m = metricas(par)
        except requests.RequestException:
            continue
        pe = pe_ratio(m)
        ev = ev_ebitda(m)
        if pe is not None and pe > 0:
            pes.append(pe)
        if ev is not None and ev > 0:
            ev_ebitdas.append(ev)

    return {
        "pe_mediana_sector": statistics.median(pes) if pes else None,
        "ev_ebitda_mediana_sector": statistics.median(ev_ebitdas) if ev_ebitdas else None,
    }
