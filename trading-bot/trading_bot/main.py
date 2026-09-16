"""Orquestador: en cada ejecución, hace pasar el trabajo por los cuatro agentes en cadena.

analista de mercado -> estratega -> gestor de riesgo -> ejecutor (+ registrador)
"""

from . import config, data, executor, registrador, risk, strategy


def ejecutar_ciclo():
    precios = data.obtener_precios_diarios()
    senal = strategy.generar_senal(precios)
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
        print(f"[{config.SYMBOL}] Señal: {senal} -> Sin acción. Motivo: {decision.motivo}")
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
