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
SMA_CORTA = int(os.getenv("SMA_CORTA", 20))
SMA_LARGA = int(os.getenv("SMA_LARGA", 50))
PORCENTAJE_MAX_POR_POSICION = _float("PORCENTAJE_MAX_POR_POSICION", 0.10)
PERDIDA_MAX_DIARIA = _float("PERDIDA_MAX_DIARIA", 0.03)
