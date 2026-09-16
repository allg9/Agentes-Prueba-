"""Agente 'analista de mercado': obtiene precios históricos de la acción."""

from datetime import datetime, timedelta

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from . import config


def obtener_precios_diarios(dias: int = 200) -> pd.DataFrame:
    cliente = StockHistoricalDataClient(config.API_KEY, config.SECRET_KEY)

    peticion = StockBarsRequest(
        symbol_or_symbols=config.SYMBOL,
        timeframe=TimeFrame.Day,
        start=datetime.now() - timedelta(days=dias),
    )
    barras = cliente.get_stock_bars(peticion).df
    barras = barras.reset_index()
    return barras[["timestamp", "open", "high", "low", "close", "volume"]]
