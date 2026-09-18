# Prompt: diseño técnico del entorno "Agente de Noticias → Agente de Fundamentales"

Guardado el 2026-09-18. Sustituye en alcance a `agente-noticias-investigacion.md` (que
queda como referencia histórica): en vez de un solo agente de noticias aislado, esto
diseña el **entorno completo**: uno o varios agentes que vigilan noticias, que pasan
empresas candidatas a uno o varios agentes que examinan sus cuentas, antes de que nada
llegue al gestor de riesgo (`risk.py`) que ya existe en `trading-bot/`.

Pega este prompt cuando quieras que lo ejecute.

---

Actúa con dos sombreros a la vez: **ingeniero de software senior especializado en agentes de IA para sistemas financieros**, y **analista de mercados profesional** que revisa cada decisión de diseño con ojo crítico. No escribas código todavía: este encargo es de investigación y diseño técnico completo.

## 0. Objetivo del entorno

Diseñar un pipeline de agentes especializados, inspirado en frameworks reales de investigación como [TradingAgents](https://arxiv.org/html/2412.20138) (que usa agentes separados de noticias, sentimiento, fundamentales, técnico, investigador, trader y gestor de riesgo, comunicados por informes estructurados, no por conversación libre):

1. **Agente(s) de Noticias** — vigilan noticias y fuentes de mercado (ver `agente-noticias-investigacion.md` y `revision-agente-noticias.md` para el trabajo ya hecho sobre credibilidad de fuentes) y producen una lista de **empresas candidatas a vigilar**, con el motivo.
2. **Agente(s) de Fundamentales** — reciben esa lista y estudian las cuentas de cada empresa candidata: si sus números son sólidos, están "en orden", y si razonablemente respaldan que la empresa sea fuerte financieramente y tenga potencial de crecer.
3. Solo si ambos agentes coinciden en que hay algo que merece la pena vigilar, esa conclusión combinada se convierte en una señal candidata que pasa — igual que las demás — por el gestor de riesgo (`risk.py`), que sigue teniendo la última palabra y sigue siendo el único que puede autorizar una orden.

Ninguno de estos agentes ejecuta operaciones directamente ni se salta al gestor de riesgo. Investiga primero, diseña después.

## 1. Investigación previa requerida

Además de lo ya investigado en `agente-noticias-investigacion.md` sobre agentes de noticias, investiga específicamente para el agente de fundamentales:

- Cómo estructura un **Fundamentals Analyst** un framework real como TradingAgents: qué datos recibe, qué calcula, en qué formato entrega su conclusión.
- Marcos de análisis fundamental con buena reputación y ya validados públicamente, en concreto:
  - **Piotroski F-Score**: 9 comprobaciones binarias sobre rentabilidad, apalancamiento/liquidez y eficiencia, que dan una puntuación de 0 a 9 (8-9 = fundamentales fuertes y en mejora; 0-2 = debilidad financiera).
  - **Altman Z-Score**: combina cinco ratios en una puntuación única de riesgo de quiebra (por encima de 2.99 = zona segura; por debajo de 1.81 = zona de distrés).
  - Señales de alerta contable reconocidas (earnings quality): beneficio que no viene respaldado por caja real, cuentas por cobrar creciendo más rápido que las ventas, picos de ingresos injustificados en el último trimestre del año, diferencia grande entre beneficio GAAP y "ajustado", cargos "extraordinarios" que se repiten cada año, cambios de auditor, múltiples reformulaciones de cuentas en los últimos 5 años.
- Qué fuentes de datos financieros usar en la práctica y sus límites de coste/cobertura: SEC EDGAR (informes 10-K/10-Q, gratuito, EE.UU.), APIs de datos fundamentales (ej. Financial Modeling Prep, Alpha Vantage, Finnhub — nivel gratuito limitado), y qué evitar (agregadores no verificados).

## 2. Diseño de cada agente (ficha técnica completa)

Para **cada** agente (noticias y fundamentales), el diseño entregado debe cubrir explícitamente estos apartados — no lo resumas, desarróllalo:

1. **Rol y objetivo**: una frase que describa qué es este agente y para qué existe.
2. **Entradas**: qué recibe exactamente (y de quién, si viene de otro agente).
3. **Herramientas/fuentes de datos** a las que tiene acceso, con su coste y límites.
4. **Proceso paso a paso**: qué hace internamente, en orden, antes de producir una conclusión.
5. **Formato de salida exacto** (esquema fijo tipo JSON): campos obligatorios, tipos de dato, y un ejemplo relleno. Para el agente de fundamentales debe incluir como mínimo: ticker, Piotroski F-Score calculado, Altman Z-Score calculado, lista de señales de alerta detectadas (si hay), veredicto (sólida / dudosa / débil), nivel de confianza, y las fuentes concretas citadas.
6. **Reglas de decisión con números concretos**: no "si parece sólida" sino umbrales explícitos (ej. qué F-Score mínimo, qué Z-Score mínimo, cuántas señales de alerta detectadas bastan para descartar una empresa aunque el resto puntúe bien).
7. **Qué nunca debe hacer** (guardrails): por ejemplo, el agente de fundamentales nunca debe emitir un veredicto "sólida" si hay una señal de alerta contable grave, por muy bien que puntúen los ratios; nunca debe recomendar comprar directamente; nunca debe basarse en un solo trimestre de datos.
8. **Casos límite** a los que debe saber responder: empresas que acaban de salir a bolsa (sin histórico suficiente), sectores con contabilidad especial (bancos, aseguradoras, REITs, donde los ratios estándar no aplican igual), datos contradictorios entre dos fuentes.
9. **Dos ejemplos completos** (uno donde el agente concluye "sólida" y otro donde concluye "débil/dudosa"), con datos de ejemplo razonables y la salida exacta que produciría.

## 3. Comunicación entre agentes

Define el protocolo exacto: en qué formato estructurado el agente de noticias entrega su lista de empresas candidatas al agente de fundamentales, qué pasa si el agente de fundamentales necesita más tiempo o datos no disponibles, y cómo se combinan finalmente ambas conclusiones (noticia + fundamentales) en una única señal candidata que sí pueda llegar al gestor de riesgo.

## 4. Integración con lo ya existente

Explica exactamente en qué punto del flujo actual del bot (`trading-bot/trading_bot/main.py`) encajarían estos dos agentes nuevos, sin romper nada de lo que ya funciona (estrategia de medias móviles, `risk.py`, `executor.py`, `registrador.py`).

## 5. Plan de validación por fases

Extiende el plan ya acordado en `agente-noticias-investigacion.md` (modo observación sin operar, métricas de calibración, distintos regímenes de mercado, evitar look-ahead bias) para cubrir también al agente de fundamentales: por ejemplo, comprobar sus veredictos pasados contra lo que de verdad le pasó después a esas empresas (¿las que calificó "sólidas" realmente lo eran, con los datos disponibles en su momento?).

## 6. Entregable esperado

El resultado de ejecutar este prompt debe ser una especificación técnica completa y autocontenida — no un resumen de una página — que yo pueda usar directamente para pedirte después que implementes el código. Cita siempre de dónde sale cada recomendación o marco usado.
