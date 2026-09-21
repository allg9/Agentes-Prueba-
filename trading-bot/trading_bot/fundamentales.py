"""Agente de Fundamentales: ver prompts/spec-agentes-noticias-fundamentales.md §2.

Recibe un ticker candidato del Agente de Noticias y evalúa, con marcos objetivos
(Piotroski F-Score, Altman Z-Score) y comparación de valoración frente al sector,
si sus cuentas son sólidas y si no está ya sobrevalorada. Nunca recomienda comprar
directamente: solo produce un veredicto que el orquestador combina con la noticia.
"""

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

from . import config, finnhub_datos, sec_edgar

RUTA_CACHE = Path(__file__).resolve().parent.parent / "cache"

SECTORES_SIN_ALTMAN_CLASICO = ("bank", "insurance", "real estate investment", "trust")


@dataclass
class VeredictoFundamentales:
    ticker: str
    piotroski_f_score: int | None
    altman_z_score: float | None
    altman_aplicable: bool
    valoracion: dict
    senales_alerta: list
    veredicto: str
    confianza: float
    fuentes: list
    fecha_datos: str | None
    motivo: str
    tipo: str = "veredicto_fundamentales"
    version_criterios: str = field(default_factory=lambda: config.VERSION_CRITERIOS_FUNDAMENTALES)
    fecha_analisis: str = field(default_factory=lambda: date.today().isoformat())


def _ratio(numerador, denominador):
    if numerador is None or denominador in (None, 0):
        return None
    return numerador / denominador


def _piotroski(cf: dict) -> tuple[int | None, int]:
    ni_a, ni_p = sec_edgar.dos_valores_mas_recientes(cf, "NetIncomeLoss")
    activos_a, activos_p = sec_edgar.dos_valores_mas_recientes(cf, "Assets")
    cfo_a, _ = sec_edgar.dos_valores_mas_recientes(cf, "NetCashProvidedByUsedInOperatingActivities")
    deuda_lp_a, deuda_lp_p = sec_edgar.dos_valores_mas_recientes(cf, "LongTermDebtNoncurrent")
    ac_a, ac_p = sec_edgar.dos_valores_mas_recientes(cf, "AssetsCurrent")
    pc_a, pc_p = sec_edgar.dos_valores_mas_recientes(cf, "LiabilitiesCurrent")
    acciones_a, acciones_p = sec_edgar.dos_valores_mas_recientes(cf, "CommonStockSharesOutstanding", "shares")
    bruto_a, bruto_p = sec_edgar.dos_valores_mas_recientes(cf, "GrossProfit")
    ventas_a, ventas_p = sec_edgar.dos_valores_mas_recientes(cf, "Revenues")

    roa_a = _ratio(ni_a, activos_a)
    roa_p = _ratio(ni_p, activos_p)
    apalancamiento_a = _ratio(deuda_lp_a or 0, activos_a)
    apalancamiento_p = _ratio(deuda_lp_p or 0, activos_p)
    liquidez_a = _ratio(ac_a, pc_a)
    liquidez_p = _ratio(ac_p, pc_p)
    margen_a = _ratio(bruto_a, ventas_a)
    margen_p = _ratio(bruto_p, ventas_p)
    rotacion_a = _ratio(ventas_a, activos_a)
    rotacion_p = _ratio(ventas_p, activos_p)

    tests = [
        roa_a is not None and roa_a > 0,
        cfo_a is not None and cfo_a > 0,
        roa_a is not None and roa_p is not None and roa_a > roa_p,
        cfo_a is not None and ni_a is not None and cfo_a > ni_a,
        apalancamiento_a is not None and apalancamiento_p is not None and apalancamiento_a < apalancamiento_p,
        liquidez_a is not None and liquidez_p is not None and liquidez_a > liquidez_p,
        acciones_a is not None and acciones_p is not None and acciones_a <= acciones_p,
        margen_a is not None and margen_p is not None and margen_a > margen_p,
        rotacion_a is not None and rotacion_p is not None and rotacion_a > rotacion_p,
    ]

    datos_faltantes = sum(
        1 for v in (roa_a, cfo_a, roa_p, apalancamiento_a, liquidez_a, acciones_a, margen_a, rotacion_a)
        if v is None
    )
    if datos_faltantes > 3:
        return None, datos_faltantes

    return sum(1 for t in tests if t), datos_faltantes


def _es_sector_sin_altman_clasico(companyfacts: dict) -> bool:
    descripcion = (companyfacts.get("sicDescription") or "").lower()
    return any(s in descripcion for s in SECTORES_SIN_ALTMAN_CLASICO)


def _altman(cf: dict, ticker: str) -> tuple[float | None, bool, str]:
    if _es_sector_sin_altman_clasico(cf):
        return None, False, "Sector financiero/REIT: el Altman Z-Score clásico no aplica a su estructura de balance."

    activos = sec_edgar.valor_mas_reciente(cf, "Assets")
    ac = sec_edgar.valor_mas_reciente(cf, "AssetsCurrent")
    pc = sec_edgar.valor_mas_reciente(cf, "LiabilitiesCurrent")
    beneficios_retenidos = sec_edgar.valor_mas_reciente(cf, "RetainedEarningsAccumulatedDeficit")
    ebit = sec_edgar.valor_mas_reciente(cf, "OperatingIncomeLoss")
    ventas = sec_edgar.valor_mas_reciente(cf, "Revenues")
    pasivos = sec_edgar.valor_mas_reciente(cf, "Liabilities")

    try:
        capitalizacion = finnhub_datos.perfil(ticker).get("marketCapitalization")
        capitalizacion = capitalizacion * 1_000_000 if capitalizacion else None
    except requests.RequestException:
        capitalizacion = None

    if None in (activos, ac, pc, beneficios_retenidos, ebit, ventas, pasivos, capitalizacion) or activos == 0 or pasivos == 0:
        return None, True, "Datos insuficientes en SEC EDGAR/Finnhub para calcular las 5 variables del Z-Score."

    a = (ac - pc) / activos
    b = beneficios_retenidos / activos
    c = ebit / activos
    d = capitalizacion / pasivos
    e = ventas / activos

    z = 1.2 * a + 1.4 * b + 3.3 * c + 0.6 * d + 1.0 * e
    return round(z, 2), True, ""


def _senales_alerta(cf: dict) -> list:
    alertas = []

    cfo_a, _ = sec_edgar.dos_valores_mas_recientes(cf, "NetCashProvidedByUsedInOperatingActivities")
    ni_a, _ = sec_edgar.dos_valores_mas_recientes(cf, "NetIncomeLoss")
    if cfo_a is not None and ni_a is not None and cfo_a < ni_a:
        alertas.append("flujo_de_caja_operativo_por_debajo_del_beneficio_neto")

    cxc_a, cxc_p = sec_edgar.dos_valores_mas_recientes(cf, "AccountsReceivableNetCurrent")
    ventas_a, ventas_p = sec_edgar.dos_valores_mas_recientes(cf, "Revenues")
    if None not in (cxc_a, cxc_p, ventas_a, ventas_p) and cxc_p and ventas_p:
        crecimiento_cxc = (cxc_a - cxc_p) / cxc_p
        crecimiento_ventas = (ventas_a - ventas_p) / ventas_p
        if crecimiento_cxc > 0 and crecimiento_ventas <= 0 or (
            crecimiento_ventas > 0 and crecimiento_cxc > crecimiento_ventas * 1.5
        ):
            alertas.append("cuentas_por_cobrar_crecen_mucho_mas_rapido_que_las_ventas")

    return alertas


def _valoracion(ticker: str) -> dict:
    try:
        m = finnhub_datos.metricas(ticker)
        medianas = finnhub_datos.medianas_sector(ticker)
    except requests.RequestException:
        return {"pe": None, "pe_mediana_sector": None, "peg": None,
                "ev_ebitda": None, "ev_ebitda_mediana_sector": None, "conclusion": "no_disponible"}

    pe = finnhub_datos.pe_ratio(m)
    ev = finnhub_datos.ev_ebitda(m)
    peg = finnhub_datos.peg_ratio(m)
    pe_sector = medianas["pe_mediana_sector"]
    ev_sector = medianas["ev_ebitda_mediana_sector"]

    sobrevalorada = False
    for valor, mediana in ((pe, pe_sector), (ev, ev_sector)):
        if valor is not None and mediana:
            if valor > mediana * (1 + config.SOBREVALORACION_PCT_SOBRE_SECTOR):
                if peg is None or peg > config.PEG_MAX_JUSTIFICABLE:
                    sobrevalorada = True

    conclusion = "cara" if sobrevalorada else ("razonable" if pe is not None else "no_disponible")

    return {
        "pe": pe, "pe_mediana_sector": pe_sector, "peg": peg,
        "ev_ebitda": ev, "ev_ebitda_mediana_sector": ev_sector,
        "conclusion": conclusion,
    }


def _ruta_cache(ticker: str) -> Path:
    return RUTA_CACHE / f"fundamentales_{ticker}.json"


def _cache_valida(ticker: str) -> dict | None:
    ruta = _ruta_cache(ticker)
    if not ruta.exists():
        return None

    cacheado = json.loads(ruta.read_text())
    fecha_analisis = datetime.fromisoformat(cacheado["fecha_analisis"])
    if datetime.now() - fecha_analisis > timedelta(days=config.CACHE_FUNDAMENTALES_DIAS):
        return None

    try:
        ultima_presentacion = sec_edgar.ultima_presentacion_periodica(ticker)
    except requests.RequestException:
        return cacheado

    if ultima_presentacion and ultima_presentacion > cacheado.get("fecha_datos", ""):
        return None

    return cacheado


def _guardar_cache(ticker: str, resultado: dict):
    RUTA_CACHE.mkdir(parents=True, exist_ok=True)
    _ruta_cache(ticker).write_text(json.dumps(resultado, default=str))


def analizar_empresa(ticker: str) -> VeredictoFundamentales:
    cacheado = _cache_valida(ticker)
    if cacheado:
        cacheado["motivo"] = cacheado.get("motivo", "") + " (resultado de caché)"
        return VeredictoFundamentales(**cacheado)

    try:
        cf = sec_edgar.obtener_companyfacts(ticker)
    except requests.RequestException as exc:
        return VeredictoFundamentales(
            ticker=ticker, piotroski_f_score=None, altman_z_score=None, altman_aplicable=False,
            valoracion={}, senales_alerta=[], veredicto="datos_insuficientes", confianza=0.0,
            fuentes=[], fecha_datos=None, motivo=f"Error consultando SEC EDGAR: {exc}",
        )

    if cf is None:
        return VeredictoFundamentales(
            ticker=ticker, piotroski_f_score=None, altman_z_score=None, altman_aplicable=False,
            valoracion={}, senales_alerta=[], veredicto="datos_insuficientes", confianza=0.0,
            fuentes=["SEC EDGAR"], fecha_datos=None,
            motivo="Empresa no encontrada en SEC EDGAR (o recién salida a bolsa, sin histórico suficiente).",
        )

    f_score, datos_faltantes_piotroski = _piotroski(cf)
    z_score, z_aplicable_por_datos, motivo_altman = _altman(cf, ticker)
    altman_aplicable = z_aplicable_por_datos and not _es_sector_sin_altman_clasico(cf)
    alertas = _senales_alerta(cf)
    valoracion = _valoracion(ticker)

    fecha_datos_serie = sec_edgar.serie_anual(cf, "Assets")
    fecha_datos = fecha_datos_serie[0]["end"] if fecha_datos_serie else None

    if f_score is None:
        veredicto, confianza, motivo = "datos_insuficientes", 0.0, "Menos de 2 años de historial financiero disponible en SEC EDGAR."
    else:
        if f_score >= config.PIOTROSKI_SOLIDA_MIN and (not altman_aplicable or (z_score or 0) > config.ALTMAN_SOLIDA_MIN):
            veredicto, motivo = "solida", "Piotroski F-Score y Altman Z-Score dentro de los umbrales de solidez."
        elif f_score <= config.PIOTROSKI_DEBIL_MAX or (altman_aplicable and z_score is not None and z_score < config.ALTMAN_DEBIL_MAX):
            veredicto, motivo = "debil", "Piotroski F-Score y/o Altman Z-Score en zona de debilidad/distrés."
        else:
            veredicto, motivo = "dudosa", "Ratios en zona intermedia, sin solidez ni debilidad claras."
        confianza = 0.8 if datos_faltantes_piotroski == 0 else 0.5

        if alertas and veredicto == "solida":
            veredicto = "dudosa"
            motivo = f"Ratios de solidez fuertes, pero señal(es) de alerta detectada(s) ({', '.join(alertas)}) impiden el veredicto 'sólida'."
            confianza = min(confianza, 0.6)

        if veredicto == "solida" and valoracion.get("conclusion") == "cara":
            veredicto = "dudosa"
            motivo = "Fundamentales sólidos, pero la acción cotiza muy por encima de la mediana del sector sin que el PEG lo justifique (posible sobrevaloración)."

    resultado = VeredictoFundamentales(
        ticker=ticker,
        piotroski_f_score=f_score,
        altman_z_score=z_score if altman_aplicable else None,
        altman_aplicable=altman_aplicable,
        valoracion=valoracion,
        senales_alerta=alertas,
        veredicto=veredicto,
        confianza=round(confianza, 2),
        fuentes=[f"SEC EDGAR companyfacts ({ticker})", f"Finnhub metric/peers ({ticker})"],
        fecha_datos=fecha_datos,
        motivo=motivo if altman_aplicable else f"{motivo} {motivo_altman}".strip(),
    )

    _guardar_cache(ticker, resultado.__dict__)
    return resultado
