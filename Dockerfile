# Dockerfile oficial para free-claude-code
# Usa la imagen slim de Python 3.14 y uv para gestionar dependencias
FROM python:3.14-slim

# Instalar uv (gestor de paquetes rápido de Astral)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Directorio de trabajo
WORKDIR /app

# Copiar solo los archivos de bloqueo de dependencias primero para aprovechar la caché de Docker
COPY pyproject.toml uv.lock ./
# Instalar dependencias del proyecto (sin el proyecto mismo) para crear el entorno
RUN uv sync --frozen --no-install-project --active

# Copiar el código fuente
COPY . .

# Instalar el proyecto en el entorno virtual
RUN uv sync --active

# Exponer el puerto donde escucha el proxy
EXPOSE 8082

# Variables de entorno por defecto (pueden ser sobrescritas en tiempo de ejecución)
# Ejemplo: -e NVIDIA_NIM_API_KEY=... -e OPENROUTER_API_KEY=...
# Si se usa LM Studio, asegúrese de que el host pueda alcanzarlo (por ejemplo, usando host.docker.internal en Docker Desktop o conectando a una red personalizada)

# Comando por defecto: iniciar el servidor proxy
CMD ["uv", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8082"]