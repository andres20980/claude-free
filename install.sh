#!/usr/bin/env bash
# install.sh - Instalador sencillo para free-claude-code
# Requisitos: git, curl, y permisos de escritura en $HOME

set -euo pipefail

REPO_URL="https://github.com/andres20980/claude-free.git"
INSTALL_DIR="$HOME/claude-free"

echo "🚀 Instalando free-claude-code..."

# 1. Verificar dependencias
command -v git >/dev/null 2>&1 || { echo "❌ git no está instalado. Abortando."; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "❌ curl no está instalado. Abortando."; exit 1; }

# 2. Clonar o actualizar repositorio
if [ -d "$INSTALL_DIR" ]; then
    echo "🔄 Actualizando repositorio existente en $INSTALL_DIR"
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo "📥 Clonando repositorio en $INSTALL_DIR"
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 3. Instalar uv si no está presente
if ! command -v uv >/dev/null 2>&1; then
    echo "📦 Instalando uv (gestor de paquetes de Python)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Añadir uv al PATH de esta sesión
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# 4. Sincronizar dependencias del proyecto
echo "📦 Instalando dependencias de Python con uv..."
uv sync --active

# 5. Preparar .env si no existe
if [ ! -f .env ]; then
    echo "🧩 Copiando .env.example a .env"
    cp .env.example .env
    echo "✏️  Por favor edita .env para añadir tus claves de API (NVIDIA_NIM_API_KEY, OPENROUTER_API_KEY) o configurar LM Studio."
else
    echo "💾 .env ya existe, se deja sin modificar."
fi

# 6. Mensaje final
echo ""
echo "✅ Instalación completada."
echo ""
echo "📝 Próximos pasos:"
echo "   1. Edita .env y configura al menos un proveedor (NVIDIA NIM, OpenRouter o LM Studio)."
echo "   2. Inicia el proxy:"
echo "      uv run uvicorn server:app --host 0.0.0.0 --port 8082"
echo "   3. En otra terminal, ejecuta Claude Code:"
echo "      ANTHROPIC_AUTH_TOKEN=\"freecc\" ANTHROPIC_BASE_URL=\"http://localhost:8082\" claude"
echo ""
echo "💡 Para usar el selector de modelos, instala fzf y añade el alias:"
echo "      alias claude-pick=\"$INSTALL_DIR/claude-pick\""
echo ""
echo "📖 Lee README.es.md para documentación completa en español."
echo ""
