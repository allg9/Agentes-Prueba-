"""Agente de Noticias: ver prompts/spec-agentes-noticias-fundamentales.md §1.

Vigila noticias de los tickers en watchlist y produce candidatas estructuradas,
filtrando por credibilidad de la fuente y descartando lo que no sea suficientemente
material. Nunca ejecuta ni ordena una operación.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest

from . import config, eventos, fuentes_confiables

PALABRAS_MATERIALIDAD_ALTA = (
    "earnings", "results", "guidance", "revenue", "profit", "merger", "acquisition",
    "acquire", "acquires", "lawsuit", "investigation", "recall", "bankruptcy",
    "dividend", "ceo resign", "sec charges", "regulatory",
)
PALABRAS_MATERIALIDAD_MEDIA = ("upgrade", "downgrade", "price target", "analyst")

PALABRAS_POSITIVAS = ("beat", "beats", "surge", "soars", "raises guidance", "upgrade", "record")
PALABRAS_NEGATIVAS = ("miss", "misses", "plunge", "downgrade", "cuts", "lawsuit", "investigation", "recall")


@dataclass
class CandidataNoticia:
    ticker: str
    ambito: str
    direccion: str
    confianza: float
    fuente: dict
    cita_textual: str
    comparacion_consenso: str
    timestamp_publicacion_original: str
    probablemente_descontada: bool
    materialidad: str
    en_ventana_pausa: bool
    decision: str
    motivo_decision: str
    tipo: str = "candidata_noticia"
    version_criterios: str = field(default_factory=lambda: config.VERSION_CRITERIOS_NOTICIAS)


def _materialidad(texto: str) -> str:
    texto = texto.lower()
    if any(p in texto for p in PALABRAS_MATERIALIDAD_ALTA):
        return "alta"
    if any(p in texto for p in PALABRAS_MATERIALIDAD_MEDIA):
        return "media"
    return "baja"


def _direccion(texto: str) -> str:
    texto = texto.lower()
    positiva = any(p in texto for p in PALABRAS_POSITIVAS)
    negativa = any(p in texto for p in PALABRAS_NEGATIVAS)
    if positiva and not negativa:
        return "positivo"
    if negativa and not positiva:
        return "negativo"
    return "neutral"


def _probablemente_descontada(publicado_en: datetime) -> bool:
    antiguedad = datetime.now(timezone.utc) - publicado_en
    return antiguedad > timedelta(minutes=config.VENTANA_DESCONTADA_MINUTOS)


def _evaluar_articulo(articulo, ticker: str) -> CandidataNoticia:
    texto = f"{articulo.headline} {articulo.summary or ''}"
    fuente_nombre = articulo.source or articulo.author or "desconocida"
    tipo_fuente = fuentes_confiables.tipo_fuente(fuente_nombre)
    confianza_alta = fuentes_confiables.es_fuente_de_confianza_alta(fuente_nombre)

    materialidad = _materialidad(texto)
    direccion = _direccion(texto)
    descontada = _probablemente_descontada(articulo.created_at)
    en_pausa = eventos.en_ventana_de_pausa(ticker)

    fuente = {
        "nombre": fuente_nombre,
        "url": articulo.url,
        "tipo": tipo_fuente,
        "historial_verificado": confianza_alta,
    }

    if not confianza_alta:
        confianza = 0.0
        decision = "descartada"
        motivo = "Fuente sin historial verificado (no es agencia/fuente primaria reconocida)."
    elif materialidad == "baja":
        confianza = 0.2
        decision = "descartada"
        motivo = "Por debajo del umbral mínimo de materialidad."
    elif en_pausa:
        confianza = 0.5
        decision = "descartada"
        motivo = "Ticker en ventana de pausa por evento de alta incertidumbre programado."
    else:
        confianza = 0.85 if materialidad == "alta" else 0.55
        if descontada:
            confianza *= 0.7
        decision = "candidata_generada"
        motivo = f"Fuente verificada, materialidad {materialidad}, dirección {direccion}."

    return CandidataNoticia(
        ticker=ticker,
        ambito="empresa",
        direccion=direccion,
        confianza=round(confianza, 2),
        fuente=fuente,
        cita_textual=(articulo.headline or "")[:280],
        comparacion_consenso="no_aplica",
        timestamp_publicacion_original=articulo.created_at.isoformat(),
        probablemente_descontada=descontada,
        materialidad=materialidad,
        en_ventana_pausa=en_pausa,
        decision=decision,
        motivo_decision=motivo,
    )


def analizar_noticias(tickers: list[str] | None = None) -> list[CandidataNoticia]:
    tickers = tickers or config.WATCHLIST
    cliente = NewsClient(config.API_KEY, config.SECRET_KEY)

    desde = datetime.now(timezone.utc) - timedelta(minutes=config.NOTICIAS_VENTANA_MINUTOS)
    peticion = NewsRequest(symbols=",".join(tickers), start=desde, limit=50)
    resultado = cliente.get_news(peticion)
    articulos = resultado.data.get("news", [])

    candidatas = []
    for articulo in articulos:
        for ticker in articulo.symbols or []:
            if ticker in tickers:
                candidatas.append(_evaluar_articulo(articulo, ticker))
    return candidatas
