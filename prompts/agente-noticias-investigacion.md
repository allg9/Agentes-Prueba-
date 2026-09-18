# Prompt: investigación y diseño del agente analista de noticias

Guardado el 2026-09-18, revisado el mismo día tras un análisis desde el punto de vista de un
analista de mercados profesional (ver `revision-agente-noticias.md`). Pega este prompt cuando
quieras que lo ejecute.

---

Actúa como un ingeniero de software senior especializado en diseñar agentes de IA para sistemas financieros, con experiencia real construyendo agentes basados en LLM y sistemas de trading algorítmico en producción.

Antes de escribir una sola línea de código, investiga:

1. **Cómo lo hacen otros con experiencia real.** Busca específicamente:
   - Papers académicos recientes sobre "LLM trading agents", "agentic trading", "financial news sentiment agents" (arXiv, SSRN).
   - Frameworks open source existentes (por ejemplo TradingAgents, FinMem, u otros que encuentres) y cómo estructuran sus agentes internamente.
   - Publicaciones técnicas de ingenieros que hayan construido e iterado sistemas similares (blogs técnicos, Medium, GitHub, charlas): qué problemas reales encontraron (falsos positivos, latencia, alucinaciones del modelo, ruido de mercado a corto plazo) y cómo los resolvieron.
   - Qué APIs de noticias/datos usan en la práctica sistemas serios (por ejemplo Benzinga, Alpaca News API, Refinitiv, NewsAPI, SEC EDGAR) y sus límites de coste, latencia y cobertura. Indica explícitamente el coste mensual aproximado de cada opción (algunas, como Bloomberg Terminal, cuestan miles de euros/mes; otras tienen niveles gratuitos limitados) para poder elegir con un presupuesto realista.

2. **Con esa investigación, diseña (sin implementarlo todavía)** la arquitectura de un nuevo agente "analista de noticias" que se integre en el bot de trading que ya existe en `trading-bot/` (que hoy solo usa una estrategia de cruce de medias móviles). El diseño debe:
   - Filtrar las fuentes por credibilidad **antes** de que el contenido llegue al análisis del LLM: fuente primaria vs. agregador, historial verificable del autor/analista (estilo TipRanks: tasa de acierto y significancia estadística, no solo popularidad), tipo de cuenta en redes sociales, señales conocidas de pump-and-dump. Descarta explícitamente cualquier contenido que parezca información no pública o filtrada (información privilegiada / insider trading): operar con eso es ilegal aunque la fuente parezca fiable; el agente solo debe usar fuentes públicas y legítimas.
   - Convertir cada noticia relevante en una **señal estructurada**, no en una opinión libre: ticker afectado, dirección esperada (positivo/negativo/neutral), nivel de confianza, la fuente citada textualmente, y si es una noticia específica de la empresa o macro/sectorial (afecta a muchas empresas a la vez y debe tratarse distinto).
   - Antes de convertir la noticia en señal, comprobar dos cosas que un analista de mercados siempre mira: (a) si la noticia compara contra lo que el mercado ya esperaba (el "consenso") — un resultado que sube pero queda por debajo de lo esperado es en realidad una mala noticia; y (b) si es razonable pensar que el precio ya se ha movido antes de que el agente pueda actuar (noticia ya "descontada" por el mercado), dado el tiempo que tarda en llegar la fuente y en procesarla.
   - Exigir una **importancia mínima** antes de generar cualquier señal (evitar generar una señal por cada titular menor y sobre-operar), y definir una regla explícita de qué hacer cuando la señal de noticias contradice a la señal técnica de medias móviles (por ejemplo: cuál prevalece, o si el conflicto directamente cancela la operación).
   - Definir que el agente debe reducir su actividad o pausarse por completo alrededor de eventos de alta incertidumbre ya programados (resultados trimestrales, decisiones de tipos de interés), cuando la volatilidad se dispara y las reacciones de precio son menos fiables.
   - **Nunca ejecutar una orden directamente**: esa señal debe pasar igual que la señal de medias móviles por el gestor de riesgo (`risk.py`) ya existente, que tiene la última palabra.
   - Explicar cómo mitigar los riesgos específicos de usar un LLM para esto: alucinaciones (inventar datos que no están en la noticia original), inyección de instrucciones ocultas dentro de una noticia maliciosa (prompt injection), y sobreajuste a ruido de muy corto plazo.
   - Dejar explícito que, aunque el bot actual solo vigila una acción (AAPL), el diseño del agente de noticias no debe impedir en el futuro vigilar varias acciones o un sector completo.

3. **Entrega un plan por fases**, empezando por algo simple y verificable sin arriesgar nada (por ejemplo: primero solo generar y registrar señales sin que afecten a ninguna orden, y comparar esas señales contra lo que pasó realmente en el mercado después, antes de conectarlas al bot). Esa validación debe:
   - Definir una métrica objetiva de acierto, incluyendo si la confianza que declara el agente está bien calibrada (si dice tener un 80% de confianza, debería acertar aproximadamente el 80% de las veces, no menos).
   - Probarse sobre periodos de mercado alcista, bajista y lateral, no solo sobre el periodo reciente — una estrategia que solo se prueba en un mercado alcista puede parecer mejor de lo que realmente es.
   - Usar, al probar con noticias históricas, la hora exacta en que cada noticia se hizo pública por primera vez (no la hora en que quedó guardada o reclasificada en la base de datos), para que el resultado del backtest sea realista y no esté artificialmente inflado.

   Incluye también una lista de las fuentes/herramientas concretas recomendadas, citando de dónde sale cada recomendación.

No implementes nada todavía en esta fase: primero quiero ver la investigación y el diseño propuesto antes de aprobar la construcción.
