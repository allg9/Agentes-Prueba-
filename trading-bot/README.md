# Bot de trading (paper trading, acciones de bolsa)

Bot que opera de forma automática pero con **dinero simulado** (paper trading), sobre una acción de bolsa, usando una estrategia clásica de cruce de medias móviles. Ningún dinero real está en riesgo.

Está organizado como una cadena de "agentes" (cada uno un módulo de código):

1. **`data.py`** (analista de mercado) — descarga los precios de la acción.
2. **`noticias.py`** (Agente de Noticias) — vigila noticias de fuentes verificadas y produce candidatas, descartando especulación y contenido con pinta de información no pública. Ver `prompts/spec-agentes-noticias-fundamentales.md`.
3. **`fundamentales.py`** (Agente de Fundamentales) — para cada candidata, estudia sus cuentas (Piotroski F-Score, Altman Z-Score, valoración frente al sector) y decide si son "sólida", "dudosa" o "débil".
4. **`combinador.py`** — combina noticias + fundamentales, y resuelve el conflicto si la señal técnica dice lo contrario.
5. **`strategy.py`** (estratega técnico) — decide, aparte, con el cruce de medias móviles: comprar, vender o esperar.
6. **`risk.py`** (gestor de riesgo) — filtra la señal final (venga de donde venga) con límites de seguridad (tamaño máximo de la posición, pérdida diaria máxima). Es el que tiene la última palabra.
7. **`executor.py`** (ejecutor) — si el gestor de riesgo lo permite, envía la orden a la cuenta de paper trading.
8. **`registrador.py`** (registrador) — guarda cada decisión, se ejecute o no, incluidas las de noticias y fundamentales, en `logs/`.

`main.py` es el orquestador: hace pasar el trabajo por todos los agentes en orden, una vez por ejecución.

El bloque de noticias + fundamentales es **opcional**: si no configuras `FINNHUB_API_KEY`, el bot sigue funcionando solo con la estrategia técnica de medias móviles, sin errores.

## Paso 1 — Crear tu cuenta de paper trading (gratis, sin dinero real)

1. Entra en https://alpaca.markets/ y crea una cuenta gratuita.
2. Una vez dentro, ve al **Paper Trading Dashboard** (no hace falta verificar identidad para el modo paper).
3. Genera tus claves de API (**API Key** y **Secret Key**) desde el dashboard de paper trading. Guárdalas, la Secret Key solo se muestra una vez.

## Paso 2 — Configurar el proyecto

Desde la carpeta `trading-bot/`:

```bash
python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Abre el archivo `.env` (nuevo, no el `.env.example`) y pega tus claves:

```
ALPACA_API_KEY=tu_api_key_real
ALPACA_SECRET_KEY=tu_secret_key_real
```

El archivo `.env` **nunca se sube a GitHub** (está excluido en `.gitignore`) porque contiene tus claves privadas.

### Opcional: activar el Agente de Noticias + Agente de Fundamentales

1. Crea una cuenta gratuita en https://finnhub.io/register y copia tu clave.
2. En tu `.env`, rellena `FINNHUB_API_KEY=tu_clave` y `SEC_USER_AGENT=Tu Nombre tu_email@ejemplo.com` (SEC EDGAR exige un contacto en cada petición, aunque no pide registro ni clave).
3. Ninguna clave se pega nunca en el chat: siempre van en tu `.env` local.

Sin este paso, el bot sigue funcionando igual, solo que sin el bloque de noticias+fundamentales.

## Paso 3 — Probar la estrategia con el pasado (backtest)

Antes de dejar el bot corriendo, comprueba cómo se habría comportado esta estrategia con datos históricos reales:

```bash
python3 backtest.py
```

Esto no toca tu cuenta de Alpaca ni ejecuta ninguna orden: solo simula. Míralo con calma antes de seguir — si el rendimiento es muy malo, prueba cambiando `SMA_CORTA` / `SMA_LARGA` en `.env`.

## Paso 4 — Ejecutar el bot (modo paper)

```bash
python3 -m trading_bot.main
```

Cada vez que lo ejecutes, el bot: mira el precio actual, decide si comprar/vender/esperar, aplica los límites de riesgo, y si procede, envía la orden simulada a Alpaca. Queda registrado en `logs/historial.csv`.

Para que corra solo, sin que tengas que lanzarlo a mano cada día, hay que **programarlo** (por ejemplo con `cron` en Linux/Mac, o el Programador de tareas en Windows) para que se ejecute una vez al día, después del cierre del mercado. Dilo cuando quieras montar esa parte y te ayudo paso a paso.

## Los límites de seguridad (no los desactives sin entenderlos)

Configurables en `.env`:

- **`PORCENTAJE_MAX_POR_POSICION`** (por defecto 10%) — nunca arriesga más de ese porcentaje del capital en una sola operación.
- **`PERDIDA_MAX_DIARIA`** (por defecto 3%) — si la cuenta pierde más de ese porcentaje en el día, el bot deja de operar hasta el día siguiente.

Esto es paper trading, así que "perder" aquí es solo un número en una cuenta de prueba — pero conviene acostumbrarse a razonar siempre en estos términos, porque son exactamente las reglas que protegerían dinero real el día que (si alguna vez) decidas dar ese paso, que requiere mucha más validación que esto.

## Qué es una simplificación en esta primera versión (v1) del Agente de Noticias + Fundamentales

Para ser honestos sobre lo que hay implementado de verdad, frente a lo que queda para
más adelante:

- La **dirección de la noticia** (positivo/negativo) se decide con una lista de
  palabras clave, no con un análisis de lenguaje más sofisticado. Funciona para casos
  claros ("beats", "misses", "lawsuit"...), pero es mejorable.
- La **comparación contra el consenso de analistas** todavía no está conectada a
  ninguna fuente de datos real: el campo `comparacion_consenso` siempre sale como
  `"no_aplica"` por ahora.
- De las señales de alerta contable de la especificación, están implementadas dos
  (flujo de caja por debajo del beneficio neto, y cuentas por cobrar creciendo mucho
  más rápido que las ventas). Cambios de auditor y reformulaciones de cuentas no están
  automatizados todavía (no hay una fuente gratuita sencilla para extraerlos).
- Los nombres exactos de los campos de valoración de Finnhub (P/E, EV/EBITDA, PEG) se
  buscan con varias variantes conocidas, pero conviene revisar una respuesta real de tu
  cuenta de Finnhub cuando tengas la clave, por si hace falta ajustar algún nombre de
  campo.

Todo esto queda registrado con su `version_criterios`, tal como pide la especificación,
así que se puede mejorar por partes sin perder el histórico de lo ya evaluado.

## Siguientes pasos posibles

- Añadir más símbolos a la vez (`WATCHLIST` ya admite varios, separados por comas; el bot hoy solo opera `SYMBOL`).
- Sustituir el filtro de palabras clave del Agente de Noticias por un análisis de lenguaje más completo.
- Conectar una fuente de datos de consenso de analistas.
- Añadir notificaciones (ej. un mensaje cuando el bot compra o vende).
- Programarlo para que corra solo todos los días.

Ninguno de estos pasos es necesario para empezar: con backtest + paper trading ya tienes un sistema completo y seguro para aprender y validar.
