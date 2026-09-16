# Bot de trading (paper trading, acciones de bolsa)

Bot que opera de forma automática pero con **dinero simulado** (paper trading), sobre una acción de bolsa, usando una estrategia clásica de cruce de medias móviles. Ningún dinero real está en riesgo.

Está organizado como una cadena de "agentes" (cada uno un módulo de código):

1. **`data.py`** (analista de mercado) — descarga los precios de la acción.
2. **`strategy.py`** (estratega) — decide: comprar, vender o esperar.
3. **`risk.py`** (gestor de riesgo) — filtra esa decisión con límites de seguridad (tamaño máximo de la posición, pérdida diaria máxima). Es el que tiene la última palabra.
4. **`executor.py`** (ejecutor) — si el gestor de riesgo lo permite, envía la orden a la cuenta de paper trading.
5. **`registrador.py`** (registrador) — guarda cada decisión (se ejecute o no) en `logs/historial.csv`.

`main.py` es el orquestador: hace pasar el trabajo por los cuatro agentes en orden, una vez por ejecución.

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

## Siguientes pasos posibles

- Añadir más símbolos (operar varias acciones a la vez).
- Sustituir o complementar la estrategia de medias móviles por un agente de IA que analice noticias.
- Añadir notificaciones (ej. un mensaje cuando el bot compra o vende).
- Programarlo para que corra solo todos los días.

Ninguno de estos pasos es necesario para empezar: con backtest + paper trading ya tienes un sistema completo y seguro para aprender y validar.
