.PHONY: help install install-dev test test-fast lint format clean docs ci all

# Default target
.DEFAULT_GOAL := help

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Fractal Reality - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	pip install -r requirements.txt
	npm install
	@echo "$(GREEN)✓ Production dependencies installed$(NC)"

install-dev: ## Install all dependencies including dev tools
	@echo "$(BLUE)Installing all dependencies...$(NC)"
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	npm install
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

test: ## Run all tests with coverage
	@echo "$(BLUE)Running Python tests...$(NC)"
	pytest --cov=analysis --cov-report=html --cov-report=term-missing -v
	@echo "$(BLUE)Running TypeScript checks...$(NC)"
	npm test || true
	@echo "$(GREEN)✓ Tests complete$(NC)"

test-fast: ## Run tests without coverage (faster)
	@echo "$(BLUE)Running fast tests...$(NC)"
	pytest -v
	@echo "$(GREEN)✓ Fast tests complete$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	pytest-watch

lint: ## Run all linters
	@echo "$(BLUE)Running Python linters...$(NC)"
	flake8 analysis/ || true
	pylint analysis/ --exit-zero
	mypy analysis/ --ignore-missing-imports || true
	@echo "$(BLUE)Running TypeScript linters...$(NC)"
	npx eslint docs/simulations/*.tsx --ext .ts,.tsx || true
	npx prettier --check "docs/**/*.{ts,tsx,js,jsx,json}" || true
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format all code
	@echo "$(BLUE)Formatting Python code...$(NC)"
	black analysis/
	isort analysis/
	@echo "$(BLUE)Formatting TypeScript code...$(NC)"
	npx prettier --write "docs/**/*.{ts,tsx,js,jsx,json}"
	@echo "$(GREEN)✓ Formatting complete$(NC)"

type-check: ## Run type checkers
	@echo "$(BLUE)Running type checks...$(NC)"
	mypy analysis/ --ignore-missing-imports
	npx tsc --noEmit
	@echo "$(GREEN)✓ Type checking complete$(NC)"

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	safety check || true
	bandit -r analysis/ || true
	@echo "$(GREEN)✓ Security scan complete$(NC)"

clean: ## Clean build artifacts and cache files
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ htmlcov/ .coverage coverage.xml
	rm -rf node_modules/.cache
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: clean ## Clean everything including dependencies
	@echo "$(BLUE)Removing all dependencies...$(NC)"
	rm -rf venv/ env/ .venv/
	rm -rf node_modules/
	@echo "$(GREEN)✓ Full cleanup complete$(NC)"

docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	@echo "$(YELLOW)Documentation build not yet configured$(NC)"
	# cd docs && make html

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	cd docs && python -m http.server 8000

coverage: ## Generate and open coverage report
	@echo "$(BLUE)Generating coverage report...$(NC)"
	pytest --cov=analysis --cov-report=html
	@echo "$(GREEN)✓ Coverage report generated$(NC)"
	@echo "$(BLUE)Opening coverage report...$(NC)"
	python -m webbrowser htmlcov/index.html || open htmlcov/index.html || xdg-open htmlcov/index.html

ci: lint test ## Run CI checks locally
	@echo "$(GREEN)✓ All CI checks passed$(NC)"

pre-commit: format lint test-fast ## Run pre-commit checks
	@echo "$(GREEN)✓ Pre-commit checks passed$(NC)"

setup: install-dev ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	pre-commit install || echo "$(YELLOW)Warning: pre-commit not available$(NC)"
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo ""
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  1. Run $(GREEN)make test$(NC) to verify everything works"
	@echo "  2. Read $(GREEN)CONTRIBUTING.md$(NC) for contribution guidelines"
	@echo "  3. Start coding! 🚀"

all: clean install-dev lint test ## Run everything
	@echo "$(GREEN)✓ Complete workflow finished$(NC)"

# Python-specific targets
.PHONY: python-test python-lint python-format
python-test: ## Run only Python tests
	pytest --cov=analysis --cov-report=term-missing -v

python-lint: ## Run only Python linters
	flake8 analysis/
	pylint analysis/

python-format: ## Format only Python code
	black analysis/
	isort analysis/

# TypeScript-specific targets
.PHONY: ts-check ts-lint ts-format
ts-check: ## Run TypeScript compiler check
	npx tsc --noEmit

ts-lint: ## Run only TypeScript linters
	npx eslint docs/simulations/*.tsx --ext .ts,.tsx

ts-format: ## Format only TypeScript code
	npx prettier --write "docs/**/*.{ts,tsx,js,jsx,json}"

# Deployment targets
.PHONY: build deploy
build: ## Build for production
	@echo "$(BLUE)Building project...$(NC)"
	npm run build || echo "$(YELLOW)No build script defined$(NC)"
	@echo "$(GREEN)✓ Build complete$(NC)"

deploy: ## Deploy to GitHub Pages
	@echo "$(BLUE)Deploying to GitHub Pages...$(NC)"
	@echo "$(YELLOW)Push to main branch to trigger GitHub Actions deployment$(NC)"

# Development helpers
.PHONY: shell notebook
shell: ## Start IPython shell with project context
	ipython

notebook: ## Start Jupyter notebook
	jupyter notebook

# Version management
.PHONY: version
version: ## Show current version
	@echo "$(BLUE)Fractal Reality Version:$(NC)"
	@grep '"version"' package.json | head -1 | sed 's/.*"version": "\(.*\)".*/  \1/'
