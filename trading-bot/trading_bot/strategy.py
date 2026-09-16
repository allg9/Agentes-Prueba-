"""Agente 'estratega': decide comprar, vender o esperar según el cruce de medias móviles."""

import pandas as pd

from . import config


def generar_senal(precios: pd.DataFrame) -> str:
    """Devuelve 'comprar', 'vender' o 'esperar' según el cruce de las dos medias."""
    cierres = precios["close"]

    if len(cierres) < config.SMA_LARGA + 1:
        return "esperar"

    media_corta = cierres.rolling(config.SMA_CORTA).mean()
    media_larga = cierres.rolling(config.SMA_LARGA).mean()

    corta_hoy, corta_ayer = media_corta.iloc[-1], media_corta.iloc[-2]
    larga_hoy, larga_ayer = media_larga.iloc[-1], media_larga.iloc[-2]

    cruce_alcista = corta_ayer <= larga_ayer and corta_hoy > larga_hoy
    cruce_bajista = corta_ayer >= larga_ayer and corta_hoy < larga_hoy

    if cruce_alcista:
        return "comprar"
    if cruce_bajista:
        return "vender"
    return "esperar"
