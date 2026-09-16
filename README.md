# Agentes Prueba

Este proyecto es un espacio para crear **equipos de agentes de IA que se pasan trabajo entre sí**, usando Claude Code. No hace falta saber programar: cada agente se define con un archivo de texto sencillo donde explicas, en lenguaje natural, qué hace ese agente.

## ¿Dónde vive todo esto?

- **Carpeta del proyecto:** esta misma carpeta (`Agentes-Prueba-`).
- **En la nube:** esta carpeta está conectada a un repositorio de GitHub (`allg9/agentes-prueba-`). Cada vez que se suben (push) los cambios, quedan guardados ahí, accesibles desde cualquier sesión de Claude Code (web, escritorio o terminal).
- **Los agentes:** viven dentro de la carpeta `.claude/agents/`. Cada archivo `.md` de esa carpeta es un agente distinto.

## Ejemplo incluido: investigador → redactor → revisor

Como ejemplo, hay tres agentes que se pasan el trabajo en cadena:

1. **`investigador`** — busca información sobre un tema y la organiza en puntos clave.
2. **`redactor`** — coge esos puntos clave y escribe un texto ordenado y claro.
3. **`revisor`** — revisa ese texto, corrige errores y explica qué cambió.

### Cómo probarlo

Simplemente pídele a Claude, en tu propio lenguaje, algo como:

> "Investiga sobre el reciclaje de plásticos, escribe un artículo corto sobre ello y revísalo antes de dármelo."

Claude entenderá que hay que usar primero el agente `investigador`, pasarle el resultado al `redactor`, y luego al `revisor`, y te devolverá el texto final ya corregido, junto con la explicación de los cambios.

También puedes pedir que se use un agente concreto, por ejemplo:

> "Usa el agente investigador para buscar información sobre la energía solar."

## Cómo crear tus propios agentes

1. Crea un archivo nuevo dentro de `.claude/agents/`, por ejemplo `atencion-cliente.md`.
2. Ponle esta estructura (cambia el contenido por el tuyo):

```markdown
---
name: nombre-del-agente
description: Explica en una frase cuándo debe usarse este agente.
tools: Read, Write
model: sonnet
---

Aquí describes, como si le explicaras el trabajo a una persona nueva,
qué debe hacer este agente, cómo debe comportarse y qué debe entregar
al terminar.
```

3. Guarda el archivo. Ya está: la próxima vez que hables con Claude en este proyecto, podrá usar ese agente.

No hace falta "instalar" nada más ni programar código: basta con crear el archivo y describir el trabajo en español.

## Guardar los cambios en la nube (GitHub)

Cuando quieras que tus cambios queden respaldados en GitHub, simplemente pídele a Claude: "guarda los cambios y súbelos" (commit y push). Así el equipo de agentes queda disponible para futuras sesiones, sin depender de esta carpeta local.
