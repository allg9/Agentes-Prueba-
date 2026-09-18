# Prompt: investigación y diseño del agente analista de noticias

Guardado el 2026-09-18. Pega este prompt cuando quieras que lo ejecute.

---

Actúa como un ingeniero de software senior especializado en diseñar agentes de IA para sistemas financieros, con experiencia real construyendo agentes basados en LLM y sistemas de trading algorítmico en producción.

Antes de escribir una sola línea de código, investiga:

1. **Cómo lo hacen otros con experiencia real.** Busca específicamente:
   - Papers académicos recientes sobre "LLM trading agents", "agentic trading", "financial news sentiment agents" (arXiv, SSRN).
   - Frameworks open source existentes (por ejemplo TradingAgents, FinMem, u otros que encuentres) y cómo estructuran sus agentes internamente.
   - Publicaciones técnicas de ingenieros que hayan construido e iterado sistemas similares (blogs técnicos, Medium, GitHub, charlas): qué problemas reales encontraron (falsos positivos, latencia, alucinaciones del modelo, ruido de mercado a corto plazo) y cómo los resolvieron.
   - Qué APIs de noticias/datos usan en la práctica sistemas serios (por ejemplo Benzinga, Alpaca News API, Refinitiv, NewsAPI, SEC EDGAR) y sus límites de coste, latencia y cobertura.

2. **Con esa investigación, diseña (sin implementarlo todavía)** la arquitectura de un nuevo agente "analista de noticias" que se integre en el bot de trading que ya existe en `trading-bot/` (que hoy solo usa una estrategia de cruce de medias móviles). El diseño debe:
   - Filtrar las fuentes por credibilidad **antes** de que el contenido llegue al análisis del LLM: fuente primaria vs. agregador, historial verificable del autor/analista (estilo TipRanks: tasa de acierto y significancia estadística, no solo popularidad), tipo de cuenta en redes sociales, señales conocidas de pump-and-dump.
   - Convertir cada noticia relevante en una **señal estructurada**, no en una opinión libre: ticker afectado, dirección esperada (positivo/negativo/neutral), nivel de confianza, y la fuente citada textualmente.
   - **Nunca ejecutar una orden directamente**: esa señal debe pasar igual que la señal de medias móviles por el gestor de riesgo (`risk.py`) ya existente, que tiene la última palabra.
   - Explicar cómo mitigar los riesgos específicos de usar un LLM para esto: alucinaciones (inventar datos que no están en la noticia original), inyección de instrucciones ocultas dentro de una noticia maliciosa (prompt injection), y sobreajuste a ruido de muy corto plazo.

3. **Entrega un plan por fases**, empezando por algo simple y verificable sin arriesgar nada (por ejemplo: primero solo generar y registrar señales sin que afecten a ninguna orden, y comparar esas señales contra lo que pasó realmente en el mercado después, antes de conectarlas al bot). Incluye una lista de las fuentes/herramientas concretas recomendadas, citando de dónde sale cada recomendación.

No implementes nada todavía en esta fase: primero quiero ver la investigación y el diseño propuesto antes de aprobar la construcción.
