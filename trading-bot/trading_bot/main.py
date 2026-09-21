"""Orquestador: hace pasar el trabajo por los agentes en cadena.

analista de mercado + [noticias -> fundamentales] -> estratega -> gestor de riesgo -> ejecutor (+ registrador)

Ver prompts/spec-agentes-noticias-fundamentales.md para el diseño del bloque
noticias -> fundamentales.
"""

import requests

from . import combinador, config, data, executor, noticias, registrador, risk, strategy


def _senal_noticias_fundamentales() -> str:
    """Devuelve 'comprar' / 'vender' / 'esperar' a partir del pipeline de noticias+fundamentales.

    Degrada con seguridad a 'esperar' si falta configuración o si alguna fuente falla:
    nunca debe tumbar el ciclo de la estrategia técnica ya existente.
    """
    if not config.FINNHUB_API_KEY:
        print("[noticias+fundamentales] FINNHUB_API_KEY no configurada: bloque desactivado por ahora.")
        return "esperar"

    try:
        candidatas = noticias.analizar_noticias([config.SYMBOL])
    except requests.RequestException as exc:
        print(f"[noticias] Fuente no disponible: {exc}")
        return "esperar"

    for candidata in candidatas:
        registrador.registrar_analisis(
            "noticias", candidata.ticker, candidata.__dict__,
            candidata.decision, candidata.motivo_decision, candidata.version_criterios,
        )

    try:
        combinadas = combinador.combinar(candidatas)
    except requests.RequestException as exc:
        print(f"[fundamentales] Fuente no disponible: {exc}")
        return "esperar"

    senal_final = "esperar"
    for señal in combinadas:
        registrador.registrar_analisis(
            "fundamentales", señal.ticker, señal.fundamentales,
            señal.fundamentales.get("veredicto", "desconocido"),
            señal.fundamentales.get("motivo", ""),
            señal.fundamentales.get("version_criterios", ""),
        )
        registrador.registrar_analisis(
            "combinado", señal.ticker, señal.__dict__,
            señal.veredicto_combinado, f"confianza={señal.confianza_combinada}", "combinado-v1",
        )
        if señal.ticker == config.SYMBOL and señal.veredicto_combinado == "candidata_para_riesgo":
            senal_final = señal.senal_risk

    return senal_final


def ejecutar_ciclo():
    precios = data.obtener_precios_diarios()
    senal_tecnica = strategy.generar_senal(precios)
    senal_noticias_fund = _senal_noticias_fundamentales()
    senal = combinador.resolver_conflicto(senal_tecnica, senal_noticias_fund)

    precio_actual = float(precios["close"].iloc[-1])

    cliente = executor.cliente_trading()
    cuenta = cliente.get_account()
    hay_posicion = executor.posicion_abierta(cliente)

    decision = risk.evaluar_orden(
        senal=senal,
        equity_actual=float(cuenta.equity),
        equity_cierre_anterior=float(cuenta.last_equity),
        precio_actual=precio_actual,
        tiene_posicion_abierta=hay_posicion,
    )

    if not decision.permitido:
        print(f"[{config.SYMBOL}] Señal técnica={senal_tecnica} noticias+fundamentales={senal_noticias_fund} -> combinada={senal} -> Sin acción. Motivo: {decision.motivo}")
        registrador.registrar(config.SYMBOL, senal, "sin_accion", 0, decision.motivo)
        return

    if senal == "comprar":
        executor.ejecutar_compra(cliente, decision.cantidad)
        print(f"[{config.SYMBOL}] COMPRA de {decision.cantidad} acciones. {decision.motivo}")
        registrador.registrar(config.SYMBOL, senal, "compra", decision.cantidad, decision.motivo)
    elif senal == "vender":
        executor.ejecutar_venta(cliente)
        print(f"[{config.SYMBOL}] VENTA (cierre de posición). {decision.motivo}")
        registrador.registrar(config.SYMBOL, senal, "venta", 0, decision.motivo)


if __name__ == "__main__":
    ejecutar_ciclo()
