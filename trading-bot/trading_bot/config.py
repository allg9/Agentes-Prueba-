import os
from dotenv import load_dotenv

load_dotenv()


def _float(nombre: str, valor_defecto: float) -> float:
    return float(os.getenv(nombre, valor_defecto))


API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

if not API_KEY or not SECRET_KEY:
    raise RuntimeError(
        "Faltan ALPACA_API_KEY / ALPACA_SECRET_KEY. "
        "Copia .env.example como .env y rellena tus claves de paper trading."
    )

SYMBOL = os.getenv("SYMBOL", "AAPL")
WATCHLIST = [s.strip().upper() for s in os.getenv("WATCHLIST", SYMBOL).split(",") if s.strip()]

SMA_CORTA = int(os.getenv("SMA_CORTA", 20))
SMA_LARGA = int(os.getenv("SMA_LARGA", 50))
PORCENTAJE_MAX_POR_POSICION = _float("PORCENTAJE_MAX_POR_POSICION", 0.10)
PERDIDA_MAX_DIARIA = _float("PERDIDA_MAX_DIARIA", 0.03)

# Agente de Noticias y Agente de Fundamentales (ver prompts/spec-agentes-noticias-fundamentales.md)
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "")

VERSION_CRITERIOS_NOTICIAS = "noticias-v1"
VERSION_CRITERIOS_FUNDAMENTALES = "fundamentales-v1"

NOTICIAS_VENTANA_MINUTOS = int(os.getenv("NOTICIAS_VENTANA_MINUTOS", 60))
VENTANA_DESCONTADA_MINUTOS = int(os.getenv("VENTANA_DESCONTADA_MINUTOS", 15))
VENTANA_PAUSA_HORAS_ANTES = _float("VENTANA_PAUSA_HORAS_ANTES", 24)
VENTANA_PAUSA_HORAS_DESPUES = _float("VENTANA_PAUSA_HORAS_DESPUES", 4)

PIOTROSKI_SOLIDA_MIN = int(os.getenv("PIOTROSKI_SOLIDA_MIN", 8))
PIOTROSKI_DEBIL_MAX = int(os.getenv("PIOTROSKI_DEBIL_MAX", 2))
ALTMAN_SOLIDA_MIN = _float("ALTMAN_SOLIDA_MIN", 2.99)
ALTMAN_DEBIL_MAX = _float("ALTMAN_DEBIL_MAX", 1.81)
SOBREVALORACION_PCT_SOBRE_SECTOR = _float("SOBREVALORACION_PCT_SOBRE_SECTOR", 0.50)
PEG_MAX_JUSTIFICABLE = _float("PEG_MAX_JUSTIFICABLE", 2.0)
CACHE_FUNDAMENTALES_DIAS = int(os.getenv("CACHE_FUNDAMENTALES_DIAS", 7))
