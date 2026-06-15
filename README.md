# Free Claude Code (español)

### Use Claude Code CLI & VSCode gratis. Sin necesidad de clave de API de Anthropic.

[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python 3.14](https://img.shields.io/badge/python-3.14-3776ab.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-astral-sh-f5a623.svg?style=for-the-badge)](https://github.com/astral-sh/uv)
[![Probado con Pytest](https://img.shields.io/badge/testing-Pytest-00c0ff.svg?style=for-the-badge)](https://github.com/Alishahryar1/free-claude-code/actions/workflows/tests.yml)
[![Comprobación de tipos: Ty](https://img.shields.io/badge/tipo%20comprobación-ty-ffcc00.svg?style=for-the-badge)](https://pypi.org/project/ty/)
[![Estilo de código: Ruff](https://img.shields.io/badge/formato%20de%20código-ruff-f5a623.svg?style=for-the-badge)](https://github.com/astral-sh/ruff)
[![Registro: Loguru](https://img.shields.io/badge/registro-loguru-4ecdc4.svg?style=for-the-badge)](https://github.com/Delgan/loguru)

Un proxy ligero que redirige las llamadas de API de Anthropic de Claude Code a **NVIDIA NIM** (40 req/min gratis), **OpenRouter** (cientos de modelos) o **LM Studio** (totalmente local).

---

## ⚡ Inicio Rápido (5 minutos)

### 1. Requisitos previos

- [Claude Code](https://github.com/anthropics/claude-code) instalado
- [uv](https://github.com/astral-sh/uv) instalado (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Una **clave de API** de al menos uno:
  - **NVIDIA NIM**: <https://build.nvidia.com/settings/api-keys> (40 req/min gratis ⭐)
  - **OpenRouter**: <https://openrouter.ai/keys> (cientos de modelos)
  - **LM Studio**: Ejecutar localmente (sin clave)

### 2. Clonar y configurar (2 minutos)

```bash
git clone https://github.com/andres20980/claude-free.git
cd claude-free
cp .env.example .env
```

Edita `.env` y elige **una** de estas opciones:

**Option A: NVIDIA NIM** (recomendado, 40 req/min gratis)
```dotenv
NVIDIA_NIM_API_KEY="nvapi-tu-clave-aquí"
MODEL="nvidia_nim/meta/llama-3.3-70b-instruct"
```

**Option B: OpenRouter** (cientos de modelos)
```dotenv
OPENROUTER_API_KEY="sk-or-tu-clave-aquí"
MODEL="open_router/deepseek/deepseek-r1-0528:free"
```

**Option C: LM Studio** (totalmente local, sin clave)
```dotenv
MODEL="lmstudio/unsloth/GLM-4.7-Flash-GGUF"
# Primero, ejecuta LM Studio localmente: https://lmstudio.ai
```

### 3. Ejecutar (1 minuto)

**Terminal 1:** Inicia el servidor proxy
```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

**Terminal 2:** Ejecuta Claude Code
```bash
ANTHROPIC_AUTH_TOKEN="freecc" ANTHROPIC_BASE_URL="http://localhost:8082" claude
```

✅ **¡Listo!** Claude Code ahora usa tu proveedor de forma **gratuita**.

### 4. VSCode (opcional)

Para usar la extensión de Claude Code en VSCode:

1. Abre Ajustes (`Ctrl + ,`) → busca `claude-code.environmentVariables`
2. Edita el JSON y añade:
```json
"claude-code.environmentVariables": [
  { "name": "ANTHROPIC_BASE_URL", "value": "http://localhost:8082" },
  { "name": "ANTHROPIC_AUTH_TOKEN", "value": "freecc" }
]
```
3. Recarga las extensiones
4. Si ves "¿Cómo quieres iniciar sesión?" → haz clic en **Consola de Anthropic** → autoriza

---

## 📋 Características

| Característica                    | Descripción                                                                                                          |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Costo cero**                    | 40 req/min gratis en NVIDIA NIM. Modelos gratis en OpenRouter. Totalmente local con LM Studio                        |
| **Reemplazo directo**             | Define 2 variables de entorno. No se necesita modificar Claude Code CLI ni la extensión de VSCode                     |
| **3 proveedores**                 | NVIDIA NIM, OpenRouter (cientos de modelos), LM Studio (local y offline)                                             |
| **Mapeo por modelo**              | Ruta las peticiones de Opus / Sonnet / Haiku a distintos modelos y proveedores. Mezcla proveedores libremente por modelo |
| **Soporte de tokens de pensamiento** | Analiza los tags `\` y `reasoning_content` para convertirlos en bloques de pensamiento nativos de Claude               |
| **Parser heurístico de herramientas** | Los modelos que generan llamadas a herramientas como texto se convierten automáticamente en uso estructurado de herramientas |
| **Optimización de peticiones**    | 5 categorías de llamadas API triviales se interceptan localmente, ahorrando cuota y latencia                         |
| **Bot de Discord**                | Codificación autónoma remota con hilado basado en árboles, persistencia de sesiones y progreso en vivo (Telegram también soportado) |
| **Límite inteligente de tasa**    | Throttle proactivo de ventana deslizante + backoff exponencial reactivo 429 + límite opcional de concurrencia entre todos los proveedores |
| **Control de subagentes**         | Intercepción de la herramienta Task fuerza `run_in_background=False`. No hay subagentes fuera de control               |
| **Extensible**                    | ABCs limpios `BaseProvider` y `MessagingPlatform`. Añade nuevos proveedores o plataformas fácilmente                  |

### Configuración avanzada (multimodelo, mezclar proveedores, etc.)

<details>
<summary><b>Ver opciones avanzadas</b></summary>

#### Multimodelo (Opus, Sonnet, Haiku con diferentes proveedores)

```dotenv
NVIDIA_NIM_API_KEY="nvapi-tu-clave-aquí"
OPENROUTER_API_KEY="sk-or-tu-clave-aquí"

MODEL_OPUS="nvidia_nim/z-ai/glm-5.1"
MODEL_SONNET="nvidia_nim/meta/llama-3.3-70b-instruct"
MODEL_HAIKU="nvidia_nim/meta/llama-3.2-3b-instruct"
MODEL="nvidia_nim/meta/llama-3.3-70b-instruct"  # fallback
```

#### Selector de modelos con `claude-pick`

`claude-pick` permite elegir modelo interactivamente sin editar `.env`:

```bash
# 1. Instala fzf
brew install fzf  # macOS/Linux

# 2. Añade alias a ~/.zshrc o ~/.bashrc
alias claude-pick="/ruta/a/claude-free/claude-pick"

# 3. Recarga shell
source ~/.zshrc

# 4. Ejecuta
claude-pick  # elige modelo → lanza Claude
```

</details>

---

## 🔄 Cómo funciona

```
┌─────────────────┐        ┌──────────────────────┐        ┌──────────────────┐
│  Claude Code    │───────>│  Free Claude Code    │───────>│  Proveedor LLM   │
│  CLI / VSCode   │<───────│  Proxy (:8082)       │<───────│  NIM / OR / LMS  │
└─────────────────┘        └──────────────────────┘        └──────────────────┘
   Anthropic API                     │                       Formato OpenAI‑compatible
   formato (SSE)              ┌───────┴────────┐                formato (SSE)
                             │ Optimizaciones  │
                             ├────────────────┤
                             │ Quota probes   │
                             │ Título gen skip│
                             │ Detección pref │
                             │ Sugerencia skip│
                             │ Mock ruta arch │
                             └────────────────┘
```

- **Proxy transparente**: Claude Code envía peticiones estándar de la API de Anthropic al servidor proxy.
- **Enrutamiento por modelo**: Las peticiones de Opus / Sonnet / Haiku se resuelven a su backend y proveedor específicos, con `MODEL` como fallback.
- **Optimización de peticiones**: Cinco categorías de peticiones triviales (probes de cuota, generación de título, detección de prefijo, modo sugerencia, extracción de ruta de archivo) se interceptan y responden al instante sin consumir cuota.
- **Traducción de formato**: Las peticiones reales se traducen del formato Anthropic al formato OpenAI‑compatible del proveedor y se devuelven en streaming.
- **Tokens de pensamiento**: Los tags `\` y el campo `reasoning_content` se convierten en bloques de pensamiento nativos de Claude para que Claude Code los renderice correctamente.

---

## 🔌 Proveedores

| Proveedor     | Costo        | Límite de tasa | Modelos                                  | Más adecuado para                     |
| ------------- | ------------ | -------------- | ---------------------------------------- | ------------------------------------- |
| **NVIDIA NIM**| Gratis       | 40 req/min     | Kimi K2, GLM5, Devstral, MiniMax         | Conductor diario, nivel gratuito generoso |
| **OpenRouter**| Gratis / Pago| Variable       | 200+ (GPT-4o, Claude, Step, etc.)        | Variedad de modelos, opciones de fallback |
| **LM Studio** | Gratis (local)| Ilimitado    | Cualquier modelo GGUF                    | Privacidad, uso offline, sin límites de tasa |

Cambia de proveedor modificando `MODEL` en `.env`. Usa el prefijo `provider/model/nombre`. Un prefijo inválido provoca un error.

| Proveedor   | Prefijo MODEL       | Variable de API Key       | URL Base                     |
| ----------- | ------------------- | ------------------------ | ---------------------------- |
| NVIDIA NIM  | `nvidia_nim/...`    | `NVIDIA_NIM_API_KEY`     | `integrate.api.nvidia.com/v1`|
| OpenRouter  | `open_router/...`   | `OPENROUTER_API_KEY`     | `openrouter.ai/api/v1`       |
| LM Studio   | `lmstudio/...`      | (ninguna)                | `localhost:1234/v1`          |

LM Studio se ejecuta localmente. Inicia el servidor en la pestaña **Developer** o mediante `lms server start`, carga un modelo y establece `MODEL` en su identificador.

---

## Bot de Discord

Controla Claude Code remotamente desde Discord. Envía tareas, observa el progreso en vivo y gestiona múltiples sesiones concurrentes. Telegram también está soportado.

### Capacidades

- Hilado de mensajes basado en árbol: responde a un mensaje para bifurcar la conversación.
- Persistencia de sesiones entre reinicios del servidor.
- Transmisión en vivo de tokens de pensamiento, llamadas a herramientas y resultados.
- Sesiones simultáneasIlimitadas de Claude CLI (la concurrencia del proveedor se controla con `PROVIDER_MAX_CONCURRENCY`).
- **Notas de voz**: envía mensajes de voz; se transcriben y se procesan como prompts normales (ver [Notas de voz](#notas-de-voz)).
- Comandos: `/stop` (cancelar tareas; responde a un mensaje para detener solo esa tarea), `/clear` (autónomo: reinicia todas las sesiones; respuesta a un mensaje: elimina esa rama hacia abajo), `/stats`.

### Instalación

1. **Crea un Bot de Discord**: ve al [Portal de Desarrolladores de Discord](https://discord.com/developers/applications), crea una aplicación, añade un bot y copia el token. Activa **Message Content Intent** en la configuración del bot.
2. **Edita `.env`**:

```dotenv
MESSAGING_PLATFORM="discord"
DISCORD_BOT_TOKEN="tu_token_de_bot_de_discord"
ALLOWED_DISCORD_CHANNELS="123456789,987654321"
```

> Activa el Modo de Desarrollador en Discord (Ajustes → Avanzado), luego haz clic derecho en un canal y "Copiar ID" para obtener los IDs de canal. Separa múltiples canales con comas. Si está vacío, ningún canal está permitido.

3. **Configura el espacio de trabajo** (donde Claude operará):

```dotenv
CLAUDE_WORKSPACE="./agent_workspace"
ALLOWED_DIR="C:/Users/tu_nombre/proyectos"
```

4. **Inicia el servidor**:

```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

5. **Invita al bot** (Generador de URL de OAuth2, alcances: `bot`, permisos: Leer Mensajes, Enviar Mensajes, Gestionar Mensajes, Leer Historial de Mensajes). Envía una tarea a un canal permitido y Claude responderá con tokens de pensamiento y llamadas a herramientas en vivo. Usa los comandos anteriores para cancelar o limpiar.

### Telegram (alternativa)

Para usar Telegram en su lugar, establece `MESSAGING_PLATFORM=telegram` y configura:

```dotenv
TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
ALLOWED_TELEGRAM_USER_ID="tu_id_de_usuario_de_telegram"
```

Obtén un token de [@BotFather](https://t.me/BotFather); encuentra tu ID de usuario mediante [@userinfobot](https://t.me/userinfobot).

### Notas de voz

Envía mensajes de voz en Telegram o Discord; se transcriben a texto y se procesan como prompts normales. Dos backends de transcripción están disponibles:

- **Whisper local** (predeterminado): usa [Hugging Face Transformers Whisper](https://huggingface.co/openai/whisper-large-v3-turbo) — gratuito, sin clave de API, funciona offline, compatible con CUDA. No se requiere ffmpeg.
- **NVIDIA NIM**: usa modelos Whisper/Parkeet de NVIDIA NIM mediante gRPC — necesita `NVIDIA_NIM_API_KEY`.

Instala los extras opcionales de voz:

```bash
# Para Whisper local (cpu/cuda)
uv sync --extra voice_local

# Para transcripción de NVIDIA NIM
uv sync --extra voice

# Ambos
uv sync --extra voice --extra voice_local
```

#### Configuración

| Variable               | Descripción                                                          | Valor por defecto |
| ---------------------- | -------------------------------------------------------------------- | ----------------- |
| `VOICE_NOTE_ENABLED`   | Habilita el manejo de notas de voz                                   | `true`            |
| `WHISPER_DEVICE`       | `cpu` \| `cuda` \| `nvidia_nim`                                      | `cpu`             |
| `WHISPER_MODEL`        | Ver modelos soportados abajo                                         | `base`            |
| `HF_TOKEN`             | Token de Hugging Face para descargas más rápidas (opcional, solo local Whisper) | — |
| `NVIDIA_NIM_API_KEY`   | API key para NVIDIA NIM (requerido para dispositivo `nvidia_nim`)    | —                 |

#### Valores soportados de `WHISPER_MODEL`

| Modelo                                                            | Dispositivo         | Descripción                           |
| ----------------------------------------------------------------- | ------------------- | ------------------------------------- |
| `tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3`, `large-v3-turbo` | `cpu` / `cuda`      | Whisper local (Hugging Face)          |
| `openai/whisper-large-v3`                                         | `nvidia_nim`        | Detección automática de idioma (mejor global) |
| `nvidia/parakeet-ctc-1.1b-asr`                                    | `nvidia_nim`        | Solo inglés                           |
| `nvidia/parakeet-ctc-0.6b-asr`                                    | `nvidia_nim`        | Solo inglés                           |
| `nvidia/parakeet-ctc-0.6b-zh-cn`                                  | `nvidia_nim`        | Chino mandarín                        |
| `nvidia/parakeet-ctc-0.6b-zh-tw`                                  | `nvidia_nim`        | Chino tradicional                     |
| `nvidia/parakeet-ctc-0.6b-es`                                     | `nvidia_nim`        | Español                               |
| `nvidia/parakeet-ctc-0.6b-vi`                                     | `nvidia_nim`        | Vietnamita                            |
| `nvidia/parakeet-1.1b-rnnt-multilingual-asr`                      | `nvidia_nim`        | Multilingüe RNNT                      |

---

## Modelos

<details>
<summary><b>NVIDIA NIM</b></summary>

Lista completa en [`nvidia_nim_models.json`](nvidia_nim_models.json).

Modelos populares:

- `nvidia_nim/minimaxai/minimax-m2.5`
- `nvidia_nim/qwen/qwen3.5-397b-a17b`
- `nvidia_nim/z-ai/glm5`
- `nvidia_nim/stepfun-ai/step-3.5-flash`
- `nvidia_nim/moonshotai/kimi-k2.5`

Explora: [build.nvidia.com](https://build.nvidia.com/explore/discover)

Actualiza la lista de modelos:

```bash
curl "https://integrate.api.nvidia.com/v1/models" > nvidia_nim_models.json
```
</details>

<details>
<summary><b>OpenRouter</b></summary>

Cientos de modelos de StepFun, OpenAI, Anthropic, Google y más.

Modelos populares:

- `open_router/stepfun/step-3.5-flash:free`
- `open_router/deepseek/deepseek-r1-0528:free`
- `open_router/openai/gpt-oss-120b:free`

Explora: [openrouter.ai/models](https://openrouter.ai/models)

Explora modelos gratuitos: [https://openrouter.ai/collections/free-models](https://openrouter.ai/collections/free-models)
</details>

<details>
<summary><b>LM Studio</b></summary>

Ejecuta modelos localmente con [LM Studio](https://lmstudio.ai). Carga un modelo en la pestaña Chat o Developer, luego establece `MODEL` en su identificador.

Ejemplos (soporte nativo de uso de herramientas):

- `LiquidAI/LFM2-24B-A2B-GGUF`
- `unsloth/MiniMax-M2.5-GGUF`
- `unsloth/GLM-4.7-Flash-GGUF`
- `unsloth/Qwen3.5-35B-A3B-GGUF`
- `LocoreMind/LocoOperator-4B`

Explora: [model.lmstudio.ai](https://model.lmstudio.ai)
</details>

---

## Configuración

| Variable                          | Descripción                                                                        | Valor por defecto                                           |
| --------------------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| `MODEL`                           | Modelo de fallback (formato de prefijo: `provider/model/nombre`; prefijo inválido causa error) | `nvidia_nim/meta/llama-3.3-70b-instruct`            |
| `MODEL_OPUS`                      | Modelo para peticiones de Claude Opus (opcional, recurre a `MODEL`)                | `nvidia_nim/z-ai/glm-5.1`                          |
| `MODEL_SONNET`                    | Modelo para peticiones de Claude Sonnet (opcional, recurre a `MODEL`)              | `nvidia_nim/meta/llama-3.3-70b-instruct` |
| `MODEL_HAIKU`                     | Modelo para peticiones de Claude Haiku (opcional, recurre a `MODEL`)               | `nvidia_nim/meta/llama-3.2-3b-instruct`         |
| `NVIDIA_NIM_API_KEY`              | Clave de API de NVIDIA (proveedor NIM)                                             | requerida                                         |
| `OPENROUTER_API_KEY`              | Clave de API de OpenRouter (proveedor OpenRouter)                                  | requerida                                         |
| `LM_STUDIO_BASE_URL`              | URL del servidor de LM Studio                                                      | `http://localhost:1234/v1`                        |
| `PROVIDER_RATE_LIMIT`             | Solicitudes de API del proveedor por ventana                                       | `40`                                              |
| `PROVIDER_RATE_WINDOW`            | Ventana de límite de tasa (segundos)                                               | `60`                                              |
| `PROVIDER_MAX_CONCURRENCY`        | Máximo de flujos simultáneos abiertos del proveedor                                | `5`                                               |
| `HTTP_READ_TIMEOUT`               | Timeout de lectura para peticiones API del proveedor (segundos)                    | `120`                                             |
| `HTTP_WRITE_TIMEOUT`              | Timeout de escritura para peticiones API del proveedor (segundos)                  | `10`                                              |
| `HTTP_CONNECT_TIMEOUT`            | Timeout de conexión para peticiones API del proveedor (segundos)                   | `2`                                               |
| `FAST_PREFIX_DETECTION`           | Habilita detección rápida de prefijo                                               | `true`                                            |
| `ENABLE_NETWORK_PROBE_MOCK`       | Habilita mock de probe de red                                                      | `true`                                            |
| `ENABLE_TITLE_GENERATION_SKIP`    | Omite la generación de título                                                      | `true`                                            |
| `ENABLE_SUGGESTION_MODE_SKIP`     | Omite el modo sugerencia                                                           | `true`                                            |
| `ENABLE_FILEPATH_EXTRACTION_MOCK` | Habilita mock de extracción de ruta de archivo                                     | `true`                                            |
| `MESSAGING_PLATFORM`              | Plataforma de mensajería: `discord` o `telegram`                                   | `discord`                                         |
| `DISCORD_BOT_TOKEN`               | Token de Bot de Discord                                                            | `""`                                              |
| `ALLOWED_DISCORD_CHANNELS`        | IDs de canales de Discord separados por comas (vacío = ninguno permitido)          | `""`                                              |
| `TELEGRAM_BOT_TOKEN`              | Token de Bot de Telegram                                                           | `""`                                              |
| `ALLOWED_TELEGRAM_USER_ID`        | ID de usuario de Telegram permitido                                                | `""`                                              |
| `VOICE_NOTE_ENABLED`              | Habilita manejo de notas de voz                                                    | `true`                                            |
| `WHISPER_MODEL`                   | Tamaño del modelo Whisper local                                                    | `base`                                            |
| `WHISPER_DEVICE`                  | `cpu` \| `cuda`                                                                    | `cpu`                                             |
| `MESSAGING_RATE_LIMIT`            | Mensajes de mensajería por ventana                                                 | `1`                                               |
| `MESSAGING_RATE_WINDOW`           | Ventana de mensajería (segundos)                                                   | `1`                                               |
| `CLAUDE_WORKSPACE`                | Directorio para el espacio de trabajo del agente                                   | `./agent_workspace`                               |
| `ALLOWED_DIR`                     | Directorios permitidos para el agente                                              | `""`                                              |

Consulta [`.env.example`](.env.example) para todos los parámetros soportados.

---

## Desarrollo

### Estructura del proyecto

```
free-claude-code/
├── server.py              # Punto de entrada
├── api/                   # Rutas FastAPI, detección de peticiones, handlers de optimización
├── providers/             # BaseProvider, OpenAICompatibleProvider, NIM, OpenRouter, LM Studio
│   └── common/            # Utils compartidos (constructor SSE, conversor de mensajes, parsers, mapeo de errores)
├── messaging/             # ABC MessagingPlatform + bots de Discord/Telegram, gestión de sesiones
├── config/                # Ajustes, configuración NIM, registro
├── cli/                   # Gestión de sesiones y procesos de CLI
└── tests/                 # Suite de pruebas pytest
```

### Comandos

```bash
uv run ruff format     # Formatea código
uv run ruff check      # Revisa estilo de código
uv run ty check        # Comprobación de tipos
uv run pytest          # Ejecuta tests
```

---

## Extensión

### Añadir un proveedor

Para **APIs compatibles con OpenAI** (Groq, Together AI, etc.), extiende `OpenAICompatibleProvider`:

```python
from providers.openai_compat import OpenAICompatibleProvider
from providers.base import ProviderConfig

class MyProvider(OpenAICompatibleProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config, provider_name="MYPROVIDER",
                         base_url="https://api.example.com/v1", api_key=config.api_key)

    def _build_request_body(self, request):
        return build_request_body(request)  # Tu constructor de petición
```

Para **APIs totalmente personalizadas**, extiende `BaseProvider` directamente:

```python
from providers.base import BaseProvider, ProviderConfig

class MyProvider(BaseProvider):
    async def stream_response(self, request, input_tokens=0, *, request_id=None):
        # Genera eventos SSE con formato Anthropic
        ...
```

### Añadir una plataforma de mensajería

Extiende `MessagingPlatform` en `messaging/` para agregar Slack u otras plataformas:

```python
from messaging.base import MessagingPlatform

class MyPlatform(MessagingPlatform):
    async def start(self):
        # Inicializa la conexión
        ...

    async def stop(self):
        # Limpieza
        ...

    async def send_message(self, chat_id, text, reply_to=None, parse_mode=None, message_thread_id=None):
        # Envía un mensaje
        ...

    async def edit_message(self, chat_id, message_id, text, parse_mode=None):
        # Edita un mensaje existente
        ...

    def on_message(self, handler):
        # Registra callback para mensajes entrantes
        ...
```

---

## Contribuye

- Informa de errores o sugiere características mediante [Issues](https://github.com/andres20980/claude-free/issues).
- Añade nuevos proveedores de LLM (Groq, Together AI, etc.).
- Añade nuevas plataformas de mensajería (Slack, etc.).
- Mejora la cobertura de pruebas.
- ¡No se acepta integración de Docker por ahora (pendiente de revisión)!
- Nuevas y interesantes características.

```bash
# Haz un fork del repo, luego:
git checkout -b mi-feature
# Haz tus cambios
uv run ruff format && uv run ruff check && uv run ty check && uv run pytest
# Abre un pull request
```

---

## Licencia

Este proyecto está licenciado bajo la **Licencia MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

Creado con [FastAPI](https://fastapi.tiangolo.com/), [OpenAI Python SDK](https://github.com/openai/openai-python), [discord.py](https://github.com/Rapptz/discord.py), y [python-telegram-bot](https://python-telegram-bot.org/).
