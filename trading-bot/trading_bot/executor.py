"""Agente 'ejecutor': envía las órdenes a la cuenta de paper trading de Alpaca."""

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from . import config


def cliente_trading() -> TradingClient:
    return TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)


def posicion_abierta(cliente: TradingClient) -> bool:
    posiciones = cliente.get_all_positions()
    return any(p.symbol == config.SYMBOL for p in posiciones)


def ejecutar_compra(cliente: TradingClient, cantidad: int):
    orden = MarketOrderRequest(
        symbol=config.SYMBOL,
        qty=cantidad,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
    )
    return cliente.submit_order(orden)


def ejecutar_venta(cliente: TradingClient):
    return cliente.close_position(config.SYMBOL)
