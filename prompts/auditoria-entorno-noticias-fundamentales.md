# Auditoría: `entorno-noticias-fundamentales.md` (v1)

Generado el 2026-09-18 ejecutando `meta-prompt-auditoria.md` sobre `entorno-noticias-fundamentales.md`.
Puntuación: 0 = ausente, 1 = parcial, 2 = completo.

## Bloque A — Calidad de especificación

| Criterio | Puntos | Justificación |
|---|---|---|
| Completitud | 1/2 | El esquema de salida exacto (§2.5) solo se exige para el agente de fundamentales; el del agente de noticias queda remitido a otro archivo sin resolverlo aquí. No se define el universo de empresas candidatas ni la cadencia de ejecución. |
| Corrección | 2/2 | Piotroski F-Score, Altman Z-Score y SEC EDGAR son marcos reales, correctamente descritos y viables con APIs gratuitas/de bajo coste. |
| Ausencia de ambigüedad | 1/2 | "Solo si ambos agentes coinciden" (§0.3) no define qué combinación exacta de veredictos cuenta como "coincidir". |
| Consistencia | 2/2 | No se detectan contradicciones internas entre secciones. |
| Verificabilidad | 1/2 | §5 pide validar pero no fija un umbral de éxito cuantificado (precisión mínima, tamaño de muestra, significancia estadística). |
| Trazabilidad | 2/2 | Referencia de forma consistente a archivos y decisiones previas del proyecto. |

**Subtotal Bloque A: 9/12**

## Bloque B — Estructura de prompt de agente en producción

| Criterio | Puntos | Justificación |
|---|---|---|
| Rol y objetivo | 2/2 | Explícitos desde el encabezado y §0. |
| Contexto y herramientas | 1/2 | No indica qué credenciales/API nuevas necesitará el usuario ni recuerda la norma del proyecto de no pegar claves en el chat. |
| Proceso paso a paso | 2/2 | §2 exige 9 apartados ordenados por agente. |
| Esquema de salida + ejemplo | 1/2 | Falta el esquema de la **señal combinada final** que debe encajar con `risk.py`, que es el punto de integración más importante. |
| Reglas de decisión con números | 1/2 | Pide "definir umbrales" pero no ancla ningún valor por defecto pese a que la propia investigación citada ya los da (F-Score, Z-Score). |
| Guardrails explícitos | 1/2 | Los guardrails de seguridad (información privilegiada, inyección de instrucciones) solo existen por referencia a un archivo marcado como "histórico", no como texto vinculante aquí. |
| Casos límite | 2/2 | Cubiertos razonablemente en §2.8 y §3. |
| Ejemplos few-shot | 1/2 | Los dos ejemplos pedidos (sólida/débil) no obligan a cubrir el caso más importante: ratios buenos pero con una señal de alerta grave (el caso que prueba si el guardrail realmente se respeta). |

**Subtotal Bloque B: 11/16**

## Bloque C — Rigor de dominio financiero

| Criterio | Puntos | Justificación |
|---|---|---|
| Incorpora los 11 hallazgos de `revision-agente-noticias.md` | 1/2 | Solo se referencian ("ver... para el trabajo ya hecho"); el propio archivo los llama "referencia histórica", lo que crea el riesgo real de que no se traten como requisitos obligatorios al ejecutar. |
| Principios adicionales no cubiertos | 0/2 | Falta valoración (¿está la acción ya cara para lo que vale, aunque sea sólida?), comparación de ratios contra el sector (un Z-Score "malo" puede ser normal en ciertos sectores), y la asimetría de velocidad entre noticias (rápidas) y fundamentales (lentos, trimestrales). |

**Subtotal Bloque C: 1/4**

## Bloque D — Rigor de ingeniería del propio agente

| Criterio | Puntos | Justificación |
|---|---|---|
| Manejo de errores | 1/2 | Solo cubre datos de fundamentales no disponibles; no cubre caídas de la fuente de noticias ni límites de tasa de las APIs. |
| Observabilidad | 0/2 | No exige registrar los veredictos intermedios (incluidos los descartados) con su motivo — sin esto, el plan de validación de §5 no se puede ejecutar en la práctica. |
| Versionado | 0/2 | No se menciona en ningún punto: si se ajustan los umbrales más adelante, no hay forma de saber qué versión de criterios generó qué resultado. |
| Seguridad (inyección de instrucciones) | 0/2 | No se exige como requisito propio del documento (solo por referencia, mismo problema que en Bloque C). |
| Coste/latencia | 1/2 | Cubre coste de datos, pero no un presupuesto de tiempo máximo aceptable para todo el pipeline junto. |

**Subtotal Bloque D: 2/10**

## Puntuación total: 23/42

## Carencias priorizadas (mayor a menor impacto)

1. Los 11 hallazgos ya corregidos y los guardrails de seguridad quedan solo referenciados a un archivo marcado como histórico, no como requisitos vinculantes de este prompt.
2. No exige registrar los veredictos intermedios (aprobados y descartados) — sin eso, la validación prometida en §5 es irrealizable.
3. Falta el contexto de valoración y comparación sectorial: una empresa sana puede ser una mala compra si ya está sobrevalorada, y un ratio "malo" puede ser normal según el sector.
4. No define el esquema exacto de la señal combinada que debe encajar con `risk.py`, ni el esquema de salida del agente de noticias con el mismo detalle que el de fundamentales.
5. No exige versionar los criterios/umbrales usados.
6. No define qué significa "coincidir" entre agentes, ni ancla umbrales por defecto ya disponibles en la propia investigación citada.
7. No indica qué credenciales nuevas hará falta pedir, ni recuerda la norma de no compartir claves en el chat.
8. Manejo de errores limitado y sin presupuesto de latencia para todo el pipeline.

## Registro de cambios aplicados en v2

| # | Cambio | Carencia que corrige |
|---|---|---|
| 1 | Nueva sección "Requisitos heredados y no negociables" con los 11 puntos y los guardrails de seguridad transcritos, no solo referenciados | 1 |
| 2 | Nuevo campo obligatorio: registro de cada veredicto (aprobado o descartado) con motivo y versión de criterios | 2, 5 |
| 3 | Nuevos apartados de valoración y comparación sectorial en el análisis de fundamentales | 3 |
| 4 | Esquema de salida exigido también para el agente de noticias, y esquema explícito de la señal combinada mapeada a la función `evaluar_orden` de `risk.py` | 4 |
| 5 | Umbrales por defecto anclados a la investigación ya citada (F-Score, Z-Score), a corregir solo si se justifica por qué | 6 |
| 6 | Definición operativa exacta de "coincidir" entre agentes | 6 |
| 7 | Apartado de credenciales necesarias por agente + recordatorio explícito de no compartir claves en el chat | 7 |
| 8 | Nueva sección "Manejo de errores y seguridad" con fallos de fuente, límites de tasa, protección contra inyección de instrucciones y presupuesto de latencia del pipeline completo | 8 |

El prompt corregido está en `entorno-noticias-fundamentales.md` (v2).
