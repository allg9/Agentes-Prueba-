"""Agente 'registrador': deja constancia en CSV de cada decisión, se ejecute o no."""

import csv
import json
from datetime import datetime
from pathlib import Path

RUTA_LOGS = Path(__file__).resolve().parent.parent / "logs"
RUTA_LOG = RUTA_LOGS / "historial.csv"
CABECERA = ["fecha_hora", "simbolo", "senal", "accion", "cantidad", "motivo"]

CABECERA_ANALISIS = ["fecha_hora", "ticker", "decision_o_veredicto", "motivo", "version_criterios", "payload_json"]


def registrar(simbolo: str, senal: str, accion: str, cantidad: int, motivo: str):
    RUTA_LOGS.mkdir(parents=True, exist_ok=True)
    es_nuevo = not RUTA_LOG.exists()

    with RUTA_LOG.open("a", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        if es_nuevo:
            escritor.writerow(CABECERA)
        escritor.writerow(
            [datetime.now().isoformat(timespec="seconds"), simbolo, senal, accion, cantidad, motivo]
        )


def registrar_analisis(tipo: str, ticker: str, payload: dict, decision_o_veredicto: str, motivo: str, version_criterios: str):
    """Registro obligatorio de cada veredicto (aprobado o descartado) de noticias/fundamentales.

    Ver prompts/spec-agentes-noticias-fundamentales.md §1.9 / §2.9 / §6.
    """
    RUTA_LOGS.mkdir(parents=True, exist_ok=True)
    ruta = RUTA_LOGS / f"analisis_{tipo}.csv"
    es_nuevo = not ruta.exists()

    with ruta.open("a", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        if es_nuevo:
            escritor.writerow(CABECERA_ANALISIS)
        escritor.writerow([
            datetime.now().isoformat(timespec="seconds"),
            ticker,
            decision_o_veredicto,
            motivo,
            version_criterios,
            json.dumps(payload, default=str, ensure_ascii=False),
        ])
