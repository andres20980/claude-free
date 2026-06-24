# Free Claude Code (español)

### Use Claude Code CLI & VSCode gratis. Sin necesidad de clave de API de Anthropic.

[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python 3.14](https://img.shields.io/badge/python-3.14-3776ab.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-astral-sh-f5a623.svg?style=for-the-badge)](https://github.com/astral-sh/uv)
[![Probado con Pytest](https://img.shields.io/badge/testing-Pytest-00c0ff.svg?style=for-the-badge)](https://github.com/andres20980/claude-free/actions/workflows/tests.yml)
[![Comprobación de tipos: Ty](https://img.shields.io/badge/tipo%20comprobación-ty-ffcc00.svg?style=for-the-badge)](https://pypi.org/project/ty/)
[![Estilo de código: Ruff](https://img.shields.io/badge/formato%20de%20código-ruff-f5a623.svg?style=for-the-badge)](https://github.com/astral-sh/ruff)
[![Registro: Loguru](https://img.shields.io/badge/registro-loguru-4ecdc4.svg?style=for-the-badge)](https://github.com/Delgan/loguru)

Un proxy ligero que redirige las llamadas de API de Anthropic de Claude Code a **NVIDIA NIM** (40 req/min gratis), **OpenRouter** (cientos de modelos), **LM Studio** (totalmente local), **Google AI Studio (Gemini)** o proveedores directos compatibles con OpenAI (**Cerebras**, **Grok**, **Cohere**).

---

> [!NOTE]
> Este fork (`andres20980/claude-free`) está mantenido y optimizado para WSL, Claude Code en VSCode, enrutamiento automático multimodelo, y mitigaciones avanzadas para modelos compatibles con OpenAI de terceros.

<div align="center">
  <img src="pic.png" alt="Free Claude Code en acción" width="700">
  <p><em>Claude Code ejecutándose a través de NVIDIA NIM totalmente gratis</em></p>
</div>

---

## ⚡ Inicio Rápido (5 minutos)

### 1. Requisitos previos

- [Claude Code](https://github.com/anthropics/claude-code) instalado.
- [uv](https://github.com/astral-sh/uv) instalado (`curl -LsSf https://astral.sh/uv/install.sh | sh` o actualízalo con `uv self update`).
- Una **clave de API** de al menos uno de los proveedores soportados:
  - **NVIDIA NIM**: <https://build.nvidia.com/settings/api-keys> (40 req/min gratis ⭐).
  - **OpenRouter**: <https://openrouter.ai/keys> (cientos de modelos gratis/de pago).
  - **Google AI Studio (Gemini)**: <https://aistudio.google.com/>.
  - **Cerebras**: <https://cerebras.ai/> (inferencia ultra-rápida de Llama).
  - **Grok (x.ai)**: <https://x.ai/>.
  - **Cohere**: <https://cohere.com/>.
  - **LM Studio**: Ejecución local (sin necesidad de clave).

### 2. Clonar y configurar (2 minutos)

```bash
git clone https://github.com/andres20980/claude-free.git
cd claude-free
cp .env.example .env
```

Edita el archivo `.env` y configura el proveedor que desees utilizar:

**Opción A: NVIDIA NIM** (Recomendado, 40 req/min gratis)
```dotenv
NVIDIA_NIM_API_KEY="nvapi-tu-clave-aquí"
MODEL="nvidia_nim/meta/llama-3.3-70b-instruct"
```

**Opción B: OpenRouter** (Acceso a cientos de modelos)
```dotenv
OPENROUTER_API_KEY="sk-or-tu-clave-aquí"
MODEL="open_router/deepseek/deepseek-r1-0528:free"
```

**Opción C: LM Studio** (Totalmente local y offline)
```dotenv
MODEL="lmstudio/unsloth/GLM-4.7-Flash-GGUF"
# Asegúrate de iniciar LM Studio localmente primero en el puerto 1234
```

### 3. Ejecutar (1 minuto)

**Terminal 1:** Inicia el servidor proxy local
```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

**Terminal 2:** Ejecuta Claude Code apuntando al proxy
```bash
ANTHROPIC_AUTH_TOKEN="freecc" ANTHROPIC_BASE_URL="http://localhost:8082" claude
```

✅ **¡Listo!** Claude Code ahora utilizará tu proveedor configurado de forma gratuita.

### 4. VSCode (opcional)

Para usar la extensión de Claude Code en VSCode:

1. Abre los Ajustes (`Ctrl + ,`) → busca `claude-code.environmentVariables`.
2. Edita el JSON de configuración para añadir las siguientes variables:
```json
"claude-code.environmentVariables": [
  { "name": "ANTHROPIC_BASE_URL", "value": "http://localhost:8082" },
  { "name": "ANTHROPIC_AUTH_TOKEN", "value": "freecc" }
]
```
3. Recarga las extensiones de VSCode.
4. Si se te solicita "¿Cómo quieres iniciar sesión?", haz clic en **Consola de Anthropic** (Anthropic Console) para autorizar localmente.

---

## 📋 Características y Optimizaciones

| Característica | Descripción |
| :--- | :--- |
| **Costo cero / Free-tier** | Enrutamiento optimizado a NIM (40 req/min gratis), modelos gratuitos de OpenRouter o LM Studio local. |
| **Reemplazo directo** | Total compatibilidad definiendo 2 variables de entorno. No requiere parches a Claude Code. |
| **Enrutamiento Inteligente** | Distribuye las peticiones de Opus / Sonnet / Haiku de forma determinista según la complejidad de la tarea si usas `AUTO_MODEL_ENABLED=true`. |
| **Optimizaciones de Latencia (Fast-Path)** | Intercepción local de solicitudes triviales (probes de cuota, generación de título, sugerencias y mocks rápidos de ruta de archivos) reduciendo la latencia a <10ms y ahorrando tokens. |
| **Mock local de ping** | Intercepción local directa de comandos `"ping"` respondiendo `"pong"` de forma instantánea sin gastar cuota de API. |
| **Poda agresiva en Haiku (FinOps)** | Eliminación de bloques `<example>` en el prompt del sistema y eliminación del envío de herramientas para el tier `haiku` (ahorrando ~10k tokens de contexto y previniendo respuestas erróneas del tipo "4" o placeholders). |
| **Saneador de herramientas compatible** | Saneador recursivo del esquema de parámetros JSON (`input_schema`) para herramientas. Corrige la ausencia de propiedad `"type"` (solucionando errores como `property args must have a type` en Cohere y otros proveedores estrictos). |
| **Capping automático de max_tokens** | Control automático de tokens de respuesta ajustado a los límites máximos del modelo/proveedor seleccionado (p. ej. limitando a 4096 en Cohere) para evitar fallos de validación en la API remota. |
| **Bot de Discord / Telegram** | Agente autónomo con hilo interactivo basado en árbol de chat, persistencia de sesiones ante reinicios, y progreso en vivo. Soporta notas de voz transcritas por Whisper local u hospedado. |
| **Límite inteligente de tasa** | Control de flujo preventivo con ventana deslizante, backoff exponencial ante respuestas HTTP 429 y límite de concurrencia ajustable por proveedor. |

---

## ⚙️ Configuración Avanzada

<details>
<summary><b>Enrutamiento Multimodelo Dinámico (Opus, Sonnet y Haiku)</b></summary>

Puedes mezclar múltiples proveedores para diferentes modelos y capacidades simultáneamente en tu `.env`:

```dotenv
NVIDIA_NIM_API_KEY="nvapi-tu-clave-aquí"
OPENROUTER_API_KEY="sk-or-tu-clave-aquí"

MODEL_OPUS="nvidia_nim/z-ai/glm-5.1"
MODEL_SONNET="nvidia_nim/meta/llama-3.3-70b-instruct"
MODEL_HAIKU="nvidia_nim/meta/llama-3.2-3b-instruct"
MODEL="nvidia_nim/meta/llama-3.3-70b-instruct"  # Fallback general
```

Si habilitas `AUTO_MODEL_ENABLED=true`, la complejidad de tu entrada determinará automáticamente a qué tier de modelo dirigir la consulta:
- Prompts muy sencillos o saludos se derivan a `haiku` (bajo coste y rápido).
- Tareas de programación y llamadas a herramientas se derivan a `sonnet`.
- Prompts complejos de análisis de código, depuración profunda o migración se derivan a `opus`.

También puedes sobreescribir manualmente el tier del modelo al principio de tu prompt escribiendo:
- `#model: haiku`
- `#model: sonnet`
- `#model: opus`

*(El proxy eliminará esta directiva antes de procesar el prompt con el LLM).*

</details>

<details>
<summary><b>Selector Interactivo de Modelos con <code>claude-pick</code></b></summary>

El script interactivo `claude-pick` permite alternar de modelo y proveedor mediante `fzf` sin tener que abrir ni editar tu `.env`:

1. Instala `fzf`:
   - **macOS/Linux**: `brew install fzf` o a través del gestor de paquetes de tu distribución.
2. Añade el alias en tu archivo de configuración de terminal (`~/.zshrc` o `~/.bashrc`):
   ```bash
   alias claude-pick="/ruta/a/claude-free/claude-pick"
   ```
3. Recarga tu terminal (`source ~/.zshrc`).
4. Ejecuta `claude-pick` para seleccionar el modelo y arrancar Claude Code inmediatamente.

</details>

---

## 🔌 Proveedores Soportados

| Proveedor | Prefijo de Modelo | Variable de API Key | URL Base / Endpoint |
| :--- | :--- | :--- | :--- |
| **NVIDIA NIM** | `nvidia_nim/...` | `NVIDIA_NIM_API_KEY` | `integrate.api.nvidia.com/v1` |
| **OpenRouter** | `open_router/...` | `OPENROUTER_API_KEY` | `openrouter.ai/api/v1` |
| **LM Studio** | `lmstudio/...` | (no requiere) | `http://localhost:1234/v1` |
| **Google AI Studio** | `google_ai_studio/...` | `GEMINI_API_KEY` | Direct gRPC / REST API |
| **Cerebras** | `cerebras/...` | `CEREBRAS_API_KEY` | `api.cerebras.ai/v1` |
| **Grok (x.ai)** | `grok/...` | `GROK_API_KEY` | `api.x.ai/v1` |
| **Cohere** | `cohere/...` | `COHERE_API_KEY` | `api.cohere.ai/compatibility/v1` |

---

## 🤖 Agente Remoto (Bot de Discord / Telegram)

El bot integrado te permite enviar tareas autónomas a Claude Code de forma remota, ver la ejecución de herramientas en vivo y manejar múltiples espacios de trabajo.

### Características del Agente

- **Estructura en árbol**: Responde a un mensaje del bot en Discord o Telegram para bifurcar la sesión y explorar caminos alternativos de depuración.
- **Persistencia de sesión**: El estado de la conversación se mantiene intacto aunque se reinicie el servidor proxy.
- **Notas de voz**: Envía notas de voz y el bot las transcribirá usando Whisper para usarlas como prompts.

### Instalación y Configuración

1. **Crea un bot en Discord** desde el [Developer Portal](https://discord.com/developers/applications), actívale el **Message Content Intent** y obtén su token.
2. Configura tu `.env`:
   ```dotenv
   MESSAGING_PLATFORM="discord"
   DISCORD_BOT_TOKEN="tu-token-de-bot"
   ALLOWED_DISCORD_CHANNELS="id-de-canal-separado-por-comas"
   CLAUDE_WORKSPACE="./agent_workspace"
   ```
3. Instala los extras requeridos si vas a usar notas de voz:
   - **Whisper local** (gratis y funciona offline): `uv sync --extra voice_local`
   - **NVIDIA NIM Whisper**: `uv sync --extra voice`
4. Ejecuta el proxy e invita a tu bot al servidor. ¡Escríbele para comenzar a programar en tu espacio de trabajo remoto!

---

## 🔧 Variables de Entorno (.env)

A continuación se detallan las variables de configuración principales. Para ver la lista completa, consulta [.env.example](.env.example).

| Variable | Descripción | Valor por defecto |
| :--- | :--- | :--- |
| `MODEL` | Modelo de fallback general | `nvidia_nim/meta/llama-3.3-70b-instruct` |
| `MODEL_OPUS` | Modelo mapeado para el tier Opus | `nvidia_nim/z-ai/glm-5.1` |
| `MODEL_SONNET` | Modelo mapeado para el tier Sonnet | `nvidia_nim/meta/llama-3.3-70b-instruct` |
| `MODEL_HAIKU` | Modelo mapeado para el tier Haiku | `nvidia_nim/meta/llama-3.2-3b-instruct` |
| `AUTO_MODEL_ENABLED` | Activa el enrutamiento inteligente dinámico | `false` |
| `AUTO_MODEL_DEFAULT` | Tier por defecto para enrutamiento automático | `sonnet` |
| `PROVIDER_RATE_LIMIT` | Solicitudes máximas a la API del proveedor por ventana | `40` |
| `PROVIDER_RATE_WINDOW` | Ventana de tiempo para el limitador de tasa (en segundos) | `60` |
| `PROVIDER_MAX_CONCURRENCY` | Máximo de peticiones simultáneas activas al proveedor | `5` |
| `FAST_PREFIX_DETECTION` | Activa la detección de prefijos optimizada | `true` |
| `ENABLE_NETWORK_PROBE_MOCK` | Intercepta localmente los pings de conexión | `true` |
| `VOICE_NOTE_ENABLED` | Habilita la transcripción de notas de voz en el bot | `true` |
| `WHISPER_DEVICE` | Dispositivo de Whisper: `cpu`, `cuda` o `nvidia_nim` | `cpu` |
| `WHISPER_MODEL` | Modelo local de Whisper a descargar (ej. `base`, `large-v3-turbo`) | `base` |

---

## 🛠️ Desarrollo y Contribución

### Estructura del repositorio

```
claude-free/
├── server.py              # Punto de entrada de FastAPI
├── api/                   # Controladores de rutas, validaciones y mocks locales
├── providers/             # Adaptadores de proveedores (NIM, OpenRouter, compatibilidad general, etc.)
│   └── common/            # Utilidades comunes (Message conversion, SSE encoding, parsers, errores)
├── messaging/             # Motores de Discord y Telegram, control de hilos de chat
├── config/                # Carga de settings Pydantic y enrutador determinista
└── tests/                 # Suite completa de pytest
```

### Flujo de Verificación del Código

Antes de enviar un Pull Request o dar por terminada una tarea, es **imprescindible** que todos los checks de CI se ejecuten y pasen en tu entorno local:

```bash
# 1. Formatear código
uv run ruff format

# 2. Comprobaciones de estilo y linter
uv run ruff check

# 3. Comprobación estática de tipos
uv run ty check

# 4. Ejecutar batería de tests unitarios
uv run pytest
```

---

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.
