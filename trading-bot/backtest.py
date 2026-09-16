"""Simula la estrategia sobre precios históricos, sin tocar la cuenta de Alpaca.

Ejecútalo antes de lanzar el bot en real (paper) para ver cómo se habría
comportado la estrategia en el pasado.
"""

from trading_bot import config, data, strategy

CAPITAL_INICIAL = 10_000.0


def backtest():
    precios = data.obtener_precios_diarios(dias=400)

    efectivo = CAPITAL_INICIAL
    acciones = 0
    operaciones = 0

    for i in range(config.SMA_LARGA + 1, len(precios)):
        ventana = precios.iloc[: i + 1]
        senal = strategy.generar_senal(ventana)
        precio = float(ventana["close"].iloc[-1])

        if senal == "comprar" and acciones == 0:
            capital_operacion = efectivo * config.PORCENTAJE_MAX_POR_POSICION
            cantidad = int(capital_operacion // precio)
            if cantidad > 0:
                acciones = cantidad
                efectivo -= cantidad * precio
                operaciones += 1

        elif senal == "vender" and acciones > 0:
            efectivo += acciones * precio
            acciones = 0
            operaciones += 1

    valor_final = efectivo + acciones * float(precios["close"].iloc[-1])
    rendimiento = (valor_final - CAPITAL_INICIAL) / CAPITAL_INICIAL

    print(f"Símbolo: {config.SYMBOL}")
    print(f"Capital inicial: {CAPITAL_INICIAL:,.2f}")
    print(f"Valor final simulado: {valor_final:,.2f}")
    print(f"Rendimiento: {rendimiento:.2%}")
    print(f"Operaciones realizadas: {operaciones}")


if __name__ == "__main__":
    backtest()
