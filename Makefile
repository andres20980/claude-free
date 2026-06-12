# Makefile para tareas comunes de free-claude-code
.PHONY: help install run test lint fmt ty-check precommit docs clean

help:
	@echo "Objetivos disponibles:"
	@echo "  make help        - Muestra esta ayuda"
	@echo "  make install     - Instala dependencias con uv"
	@echo "  make run         - Inicia el servidor proxy (uvicorn)"
	@echo "  make test        - Ejecuta la suite de pruebas con pytest"
	@echo "  make lint        - Revisa estilo de código con ruff"
	@echo "  make fmt         - Formatea el código con ruff"
	@echo "  make ty-check    - Revisa tipos con ty"
	@echo "  make precommit   - Ejecuta pre-commit en todos los archivos"
	@echo "  make docs        - Genera documentación con MkDocs (si está instalado)"
	@echo "  make clean       - Elimina archivos temporales y caché"

install:
	uv sync

run:
	uv run uvicorn server:app --host 0.0.0.0 --port 8082

test:
	uv run pytest -v

lint:
	uv run ruff check

fmt:
	uv run ruff format

ty-check:
	uv run ty check

precommit:
	pre-commit run --all-files

docs:
	mkdocs build

clean:
	rm -rf .venv __pycache__ */__pycache__ */*/__pycache__ .pytest_cache .ruff_cache .coverage htmlcov
	find . -type f -name "*.pyc" -delete
