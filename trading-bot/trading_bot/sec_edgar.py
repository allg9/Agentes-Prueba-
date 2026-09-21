"""Acceso a datos de SEC EDGAR (gratis, sin clave, 10 peticiones/segundo).

Fuente de verdad para los estados financieros del Agente de Fundamentales
(prompts/spec-agentes-noticias-fundamentales.md §2.3).
"""

import json
import time
from pathlib import Path

import requests

from . import config

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
CACHE_TICKERS = Path(__file__).resolve().parent.parent / "cache" / "sec_tickers.json"


def _cabeceras() -> dict:
    contacto = config.SEC_USER_AGENT or "Agentes-Prueba- contacto@ejemplo.com"
    return {"User-Agent": contacto}


def _mapa_ticker_a_cik() -> dict:
    if CACHE_TICKERS.exists():
        edad_segundos = time.time() - CACHE_TICKERS.stat().st_mtime
        if edad_segundos < 30 * 24 * 3600:
            return json.loads(CACHE_TICKERS.read_text())

    respuesta = requests.get(TICKERS_URL, headers=_cabeceras(), timeout=15)
    respuesta.raise_for_status()
    datos = respuesta.json()
    mapa = {fila["ticker"].upper(): fila["cik_str"] for fila in datos.values()}

    CACHE_TICKERS.parent.mkdir(parents=True, exist_ok=True)
    CACHE_TICKERS.write_text(json.dumps(mapa))
    return mapa


def cik_de_ticker(ticker: str) -> int | None:
    return _mapa_ticker_a_cik().get(ticker.upper())


def obtener_companyfacts(ticker: str) -> dict | None:
    cik = cik_de_ticker(ticker)
    if cik is None:
        return None

    respuesta = requests.get(COMPANYFACTS_URL.format(cik=cik), headers=_cabeceras(), timeout=15)
    if respuesta.status_code == 404:
        return None
    respuesta.raise_for_status()
    return respuesta.json()


def serie_anual(companyfacts: dict, concepto: str, unidad: str = "USD") -> list[dict]:
    """Devuelve los valores anuales (10-K, FY) de un concepto US-GAAP, más recientes primero."""
    try:
        entradas = companyfacts["facts"]["us-gaap"][concepto]["units"][unidad]
    except KeyError:
        return []

    anuales = [e for e in entradas if e.get("form") == "10-K" and e.get("fp") == "FY"]
    anuales.sort(key=lambda e: e["end"], reverse=True)

    vistos = set()
    resultado = []
    for entrada in anuales:
        if entrada["end"] not in vistos:
            vistos.add(entrada["end"])
            resultado.append(entrada)
    return resultado


def valor_mas_reciente(companyfacts: dict, concepto: str, unidad: str = "USD") -> float | None:
    serie = serie_anual(companyfacts, concepto, unidad)
    return serie[0]["val"] if serie else None


def dos_valores_mas_recientes(companyfacts: dict, concepto: str, unidad: str = "USD") -> tuple:
    serie = serie_anual(companyfacts, concepto, unidad)
    actual = serie[0]["val"] if len(serie) >= 1 else None
    anterior = serie[1]["val"] if len(serie) >= 2 else None
    return actual, anterior


def ultima_presentacion_periodica(ticker: str) -> str | None:
    """Fecha (YYYY-MM-DD) del 10-K/10-Q más reciente, para saber si la caché sigue vigente."""
    cik = cik_de_ticker(ticker)
    if cik is None:
        return None

    respuesta = requests.get(SUBMISSIONS_URL.format(cik=cik), headers=_cabeceras(), timeout=15)
    if respuesta.status_code == 404:
        return None
    respuesta.raise_for_status()
    recientes = respuesta.json().get("filings", {}).get("recent", {})

    formularios = recientes.get("form", [])
    fechas = recientes.get("filingDate", [])
    periodicas = [f for form, f in zip(formularios, fechas) if form in ("10-K", "10-Q")]
    return max(periodicas) if periodicas else None
