# Informe: revisión del prompt del agente de noticias (visión de analista de mercados)

Guardado el 2026-09-18.

## Lo que el prompt ya hacía bien

- Exigía filtrar por credibilidad de la fuente antes de analizar el contenido.
- Convertía cada noticia en una señal estructurada, no en una opinión libre.
- Obligaba a pasar siempre por el gestor de riesgo antes de operar.
- Pedía empezar en modo "solo observar", sin arriesgar nada.

Esa base es sólida. Pero le faltaban varias cosas que cualquier analista de mercados con experiencia consideraría imprescindibles.

## Errores y puntos débiles encontrados

**1. No distingue entre una noticia nueva y una que "el mercado ya sabe".**
Cuando una noticia importante sale por una fuente rápida (Bloomberg, Benzinga), el precio ya se mueve en segundos o minutos. Para cuando un modelo de IA la lee y decide algo, es muy probable que ese movimiento ya haya pasado. El prompt no obligaba a comprobar esto, así que el agente podría "descubrir" algo que el mercado ya llevaba rato reflejando en el precio.

**2. No compara la noticia contra lo que el mercado esperaba.**
Un resultado de "beneficios suben 5%" es en realidad una mala noticia si los analistas esperaban un 10%. Sin comparar contra esa expectativa (el "consenso"), el agente puede interpretar la dirección al revés de como reaccionará realmente el mercado.

**3. Riesgo legal no mencionado: información privilegiada.**
Si en algún momento el agente accede a información filtrada o no pública sobre una empresa, operar con eso es ilegal (se llama "información privilegiada" o insider trading), aunque la fuente parezca fiable. El prompt no dejaba explícito que el agente solo debe usar fuentes públicas y legítimas.

## Cosas que faltaban

**4. Qué pasa si la noticia dice una cosa y las medias móviles dicen la contraria.**
El prompt no definía ninguna regla para cuando las dos señales del bot (la técnica y la de noticias) no están de acuerdo. Sin esa regla, el sistema podría comportarse de forma imprevisible.

**5. No hay pausa en momentos de máxima incertidumbre.**
Alrededor de eventos programados importantes (resultados trimestrales, decisiones de tipos de interés) la volatilidad se dispara y los precios se vuelven más erráticos. Un profesional reduce o pausa la operativa en esas ventanas; el prompt no lo contemplaba.

**6. No define cómo medir si el agente realmente "acierta".**
Pedía comparar señales con lo que pasó después, pero no fijaba una forma objetiva de medirlo (por ejemplo: si el agente dice tener un 80% de confianza, ¿acierta realmente el 80% de las veces?). Sin esta medida, es fácil engañarse pensando que funciona cuando no es así.

**7. Faltaba exigir probarlo en distintos tipos de mercado.**
Una estrategia puede parecer genial probada solo en un periodo alcista reciente y fallar en cuanto el mercado cambia de tendencia. Había que exigir explícitamente probarla en periodos alcistas, bajistas y de mercado lateral, no solo en el más reciente.

**8. Trampa técnica en el backtest: usar la fecha equivocada de la noticia.**
Al probar con noticias históricas hay que usar la hora exacta en que esa noticia se hizo pública por primera vez, no la hora en que aparece guardada en alguna base de datos (a veces se corrige o reclasifica después). Si no se tiene cuidado, el backtest parece mejor de lo que sería en la realidad.

## Oportunidades que no se habían mencionado

**9. Pensar más allá de una sola acción.**
El diseño actual (y el bot base) solo vigila una acción (AAPL). Vale para empezar, pero el diseño del agente de noticias debería dejar la puerta abierta a vigilar varias acciones o un sector completo, no obligar a rehacerlo todo después.

**10. Evitar operar por cada titular.**
Sin un filtro de "importancia mínima", el agente podría generar una señal por cualquier noticia menor y sobre-operar. Había que exigir que solo cuente como señal una noticia con impacto potencial relevante, no cualquier mención de la empresa.

**11. Coste real de las fuentes de calidad.**
Herramientas como Bloomberg Terminal cuestan miles de euros al mes; otras (Benzinga, NewsAPI) tienen niveles gratuitos limitados. El prompt no pedía dejar claro el presupuesto disponible para elegir fuentes realistas desde el principio.

## Qué se ha corregido

He añadido estos 11 puntos al prompt original, integrados en sus mismas tres secciones (investigación, diseño, plan por fases), para que cuando lo ejecute no se me escape ninguno. El archivo actualizado está en `prompts/agente-noticias-investigacion.md`.
