.PHONY: install dev test clean run serve example help

# Default target
help:
	@echo "📚 BookForge - Available commands:"
	@echo ""
	@echo "🛠️  Setup:"
	@echo "  make install     Install dependencies"
	@echo "  make dev         Install in development mode"
	@echo ""
	@echo "🚀 Running:"
	@echo "  make serve       Start the API server"
	@echo "  make run         Run the CLI (same as serve)"
	@echo "  make example     Generate example EPUB"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test        Run tests"
	@echo "  make format      Format code"
	@echo "  make lint        Run linting"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean       Clean generated files"

# Installation
install:
	pip install -r requirements.txt

dev:
	pip install -e ".[dev]"

# Running
serve:
	python -m bookforge.main

run: serve

# Example generation
example:
	python -m bookforge.cli generate examples/sample_book \
		--title "The Digital Revolution" \
		--author "BookForge Team" \
		--theme modern \
		--output example.epub
	@echo "✅ Example EPUB generated: example.epub"

# Testing and quality
test:
	pytest tests/ -v

format:
	black bookforge/
	isort bookforge/

lint:
	flake8 bookforge/
	mypy bookforge/

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.epub" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf temp_books/
	rm -rf generated_epubs/

# Development helpers
docs:
	@echo "📖 Starting server for API docs..."
	@echo "Visit: http://localhost:8000/docs"
	python -m bookforge.main

# Build distribution
build:
	python -m build

# Install from local build
install-local: build
	pip install dist/*.whl

# Quick development setup
setup: install example
	@echo "🎉 BookForge is ready!"
	@echo "Try: make serve"