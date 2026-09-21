"""Calendario de eventos de alto impacto (resultados trimestrales), vía Finnhub.

Usado para aplicar la ventana de pausa del Agente de Noticias
(prompts/spec-agentes-noticias-fundamentales.md §1.6).
"""

from datetime import datetime, timedelta

import requests

from . import config

FINNHUB_EARNINGS_URL = "https://finnhub.io/api/v1/calendar/earnings"


def proximos_resultados(ticker: str, dias_adelante: int = 14) -> list[datetime]:
    if not config.FINNHUB_API_KEY:
        return []

    hoy = datetime.now().date()
    respuesta = requests.get(
        FINNHUB_EARNINGS_URL,
        params={
            "from": hoy.isoformat(),
            "to": (hoy + timedelta(days=dias_adelante)).isoformat(),
            "symbol": ticker,
            "token": config.FINNHUB_API_KEY,
        },
        timeout=10,
    )
    respuesta.raise_for_status()
    eventos = respuesta.json().get("earningsCalendar", [])
    return [datetime.fromisoformat(e["date"]) for e in eventos if e.get("date")]


def en_ventana_de_pausa(ticker: str, ahora: datetime | None = None) -> bool:
    ahora = ahora or datetime.now()
    try:
        fechas = proximos_resultados(ticker)
    except requests.RequestException:
        return False

    for fecha_evento in fechas:
        inicio_pausa = fecha_evento - timedelta(hours=config.VENTANA_PAUSA_HORAS_ANTES)
        fin_pausa = fecha_evento + timedelta(hours=config.VENTANA_PAUSA_HORAS_DESPUES)
        if inicio_pausa <= ahora <= fin_pausa:
            return True
    return False
