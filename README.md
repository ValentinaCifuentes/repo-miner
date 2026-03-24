# GitHub Method Miner

Sistema distribuido para analizar repositorios públicos de GitHub y extraer las palabras más frecuentes utilizadas en nombres de funciones y métodos en los lenguajes Python y Java.

Diseñado bajo la arquitectura Productor-Consumidor.

---

## Tabla de Contenidos

* [Descripción](#descripción)
* [Arquitectura](#arquitectura)
* [Tecnologías](#tecnologías)
* [Estructura del Proyecto](#estructura-del-proyecto)
* [Cómo Ejecutar](#cómo-ejecutar)
* [Configuración](#configuración)
* [Uso](#uso)
* [Detalles Técnicos](#detalles-técnicos)
* [Manejo de Errores](#manejo-de-errores)

---

## Descripción

Este proyecto implementa un sistema basado en el patrón **Productor-Consumidor** para analizar código fuente de GitHub en tiempo real. 

Este sistema garantiza el desacoplamiento total mediante una cola de mensajes en memoria:

* El **Miner** actúa como productor: obtiene repositorios por popularidad, extrae definiciones de funciones de forma avanzada y publica el flujo de datos.
* El **Visualizer** actúa como consumidor: procesa continuamente la cola de mensajes y expone los resultados dinámicamente.

El objetivo es identificar tendencias de nomenclatura (`snake_case`, `camelCase`, etc.) en la comunidad de desarrollo.

---

## Arquitectura

```
  GitHub API
      ↓
    Miner   ──────Push──────▶   Redis Queue
 (Productor)                         │
                                     │ Pull (Loop)
                                     ▼
                                Visualizer
                               (Consumidor)
```

### Características clave

* Desacoplamiento total mediante Message Broker (Redis).
* Tolerancia a latencias: el productor no bloquea al consumidor y viceversa.
* Procesamiento continuo y dinámico.
* Contenedorización integral con Docker.

---

## Tecnologías

* Python 3.11
* Redis 5.0 (Gestor de colas en memoria)
* Streamlit (Interfaz gráfica reactiva)
* AST (Abstract Syntax Tree para parsing de Python)
* Docker y Docker Compose

---

## Estructura del Proyecto

```text
repo-miner/
├── docker-compose.yml
├── .env.example
├── miner/
│   ├── main.py
│   ├── github_client.py
│   ├── code_parser.py
│   ├── text_processor.py
│   ├── publisher.py
│   ├── requirements.txt
│   └── Dockerfile
└── visualizer/
    ├── app.py
    ├── requirements.txt
    └── Dockerfile
```

---

## Cómo Ejecutar

### 1. Preparar el entorno

```bash
git clone <url-del-repositorio>
cd repo-miner
```

Generar el archivo de configuración de variables de entorno (ver sección [Configuración](#configuración)).

### 2. Ejecutar servicios

```bash
docker-compose up --build
```

### 3. Acceder a los resultados

El panel de visualización en tiempo real estará disponible en:
```text
http://localhost:8501
```

---

## Configuración

Se recomienda configurar un token de acceso personal para evitar las restricciones de la API pública de GitHub (límite de 60 peticiones/hora).

Crear un archivo `.env` en la raíz del proyecto:

```properties
GITHUB_TOKEN=tu_token_aqui_ghp_xxxxxxxxxxx
```

---

## Uso

Una vez iniciados los contenedores, el flujo es automático:

1. El Miner consulta los repositorios más populares de Python y Java.
2. Extrae las palabras contenidas en las firmas de los métodos.
3. El Visualizer actualiza los gráficos estadísticos cada 2 segundos.
4. Mediante la barra lateral, el usuario puede parametrizar dinámicamente el límite del Top N a visualizar.

---

## Detalles Técnicos

### 1. Extracción de Código Especializada (AST vs Regex)

Para el análisis de código Python, se descartó el uso de Expresiones Regulares en favor de la librería estándar `ast` (Abstract Syntax Tree). 

**Ventajas del enfoque AST:**
* Ignora automáticamente definiciones dentro de bloques de texto (strings) o comentarios, evitando falsos positivos.
* Distingue con precisión funciones estándar (`def`) de funciones asíncronas (`async def`).
* Permite el filtrado controlado de "métodos mágicos" (`__init__`, `__str__`) para evitar ruido estadístico en la visualización final.

Para Java, debido a restricciones de entorno, se mantuvo una compilación avanzada de expresiones regulares tolerante a modificadores de acceso compuestos.

### 2. Comunicación Asíncrona (Message Queue)

Se implementó **Redis** como intermediario en lugar de llamadas HTTP (REST) directas.

**Ventajas del enfoque Queue:**
* Si el Visualizer experimenta alta demanda de renderizado, el Miner puede continuar procesando y acumulando hallazgos sin verse ralentizado (Backpressure control).
* Al ser Redis una estructura de datos en memoria, la latencia de ingestión de millones de palabras es virtualmente cero.

---

## Manejo de Errores

El sistema incorpora tolerancia a fallos en el Productor:

* **Manejo Dinámico de Cuotas (Rate-Limits)**: Intercepta las cabeceras `X-RateLimit-Reset` de GitHub y suspende la ejecución (`time.sleep`) el tiempo matemáticamente exacto para recuperar la cuota.
* Tolerancia a repositorios sin código fuente analizable o malformados.
* Recuperación automática ante desconexiones transitorias de la cola Redis.
