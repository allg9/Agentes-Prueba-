"""Agente 'gestor de riesgo': aplica límites antes de dejar pasar cualquier orden."""

from dataclasses import dataclass

from . import config


@dataclass
class DecisionRiesgo:
    permitido: bool
    motivo: str
    cantidad: int = 0


def perdida_diaria_excedida(equity_actual: float, equity_cierre_anterior: float) -> bool:
    if equity_cierre_anterior <= 0:
        return False
    variacion = (equity_actual - equity_cierre_anterior) / equity_cierre_anterior
    return variacion <= -config.PERDIDA_MAX_DIARIA


def evaluar_orden(
    senal: str,
    equity_actual: float,
    equity_cierre_anterior: float,
    precio_actual: float,
    tiene_posicion_abierta: bool,
) -> DecisionRiesgo:
    if senal == "esperar":
        return DecisionRiesgo(False, "No hay señal de entrada o salida.")

    if perdida_diaria_excedida(equity_actual, equity_cierre_anterior):
        return DecisionRiesgo(
            False, f"Pérdida diaria supera el límite ({config.PERDIDA_MAX_DIARIA:.0%}). No se opera hoy."
        )

    if senal == "vender":
        if not tiene_posicion_abierta:
            return DecisionRiesgo(False, "Señal de venta pero no hay posición abierta.")
        return DecisionRiesgo(True, "Cerrar posición por señal bajista.")

    if senal == "comprar":
        if tiene_posicion_abierta:
            return DecisionRiesgo(False, "Ya hay una posición abierta; no se duplica.")
        capital_para_esta_operacion = equity_actual * config.PORCENTAJE_MAX_POR_POSICION
        cantidad = int(capital_para_esta_operacion // precio_actual)
        if cantidad <= 0:
            return DecisionRiesgo(False, "Capital insuficiente para comprar ni 1 acción dentro del límite.")
        return DecisionRiesgo(True, "Abrir posición por señal alcista.", cantidad)

    return DecisionRiesgo(False, f"Señal desconocida: {senal}")
