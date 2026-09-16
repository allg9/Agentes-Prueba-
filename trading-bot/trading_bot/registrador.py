"""Agente 'registrador': deja constancia en un CSV de cada decisión, se ejecute o no."""

import csv
from datetime import datetime
from pathlib import Path

RUTA_LOG = Path(__file__).resolve().parent.parent / "logs" / "historial.csv"
CABECERA = ["fecha_hora", "simbolo", "senal", "accion", "cantidad", "motivo"]


def registrar(simbolo: str, senal: str, accion: str, cantidad: int, motivo: str):
    RUTA_LOG.parent.mkdir(parents=True, exist_ok=True)
    es_nuevo = not RUTA_LOG.exists()

    with RUTA_LOG.open("a", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        if es_nuevo:
            escritor.writerow(CABECERA)
        escritor.writerow(
            [datetime.now().isoformat(timespec="seconds"), simbolo, senal, accion, cantidad, motivo]
        )
