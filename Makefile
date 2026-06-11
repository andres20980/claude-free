# Makefile sencillo para tareas comunes de free-claude-code
.PHONY: help install run test lint fmt clean

help:
	@echo "Objetivos disponibles:"
	@echo "  make help    - Muestra esta ayuda"
	@echo "  make install - Instala dependencias con uv"
	@echo "  make run     - Inicia el servidor proxy (uvicorn)"
	@echo "  make test    - Ejecuta la suite de pruebas con pytest"
	@echo "  make lint    - Revisa estilo de código con ruff"
	@echo "  make fmt     - Formatea el código con ruff"
	@echo "  make clean   - Elimina archivos temporales y caché"

install:
	uv sync

run:
	uv run uvicorn server:app --host 0.0.0.0 --port 8082

test:
	uv run pytest

lint:
	uv run ruff check

fmt:
	uv run ruff format

clean:
	rm -rf .venv __pycache__ */__pycache__ */*/__pycache__ .pytest_cache .ruff_cache .coverage htmlcov
	find . -type f -name "*.pyc" -delete