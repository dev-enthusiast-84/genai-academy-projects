.PHONY: help setup dev deploy clean init-env validate-config

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Content Strategist MVP - Makefile
# Single command orchestration for setup, development, and deployment
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

help:
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║     Content Strategist MVP - Makefile Commands         ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📖  DOCUMENTATION:"
	@echo "  make docs              Generate and view architecture docs"
	@echo ""
	@echo "🚀  SETUP & INITIALIZATION:"
	@echo "  make init              Initialize project (one-time setup)"
	@echo "  make init-env          Create .env.local from template"
	@echo "  make validate-config   Verify all config is correct"
	@echo ""
	@echo "💻  DEVELOPMENT:"
	@echo "  make dev               Start local development (Docker)"
	@echo "  make dev-stop          Stop development environment"
	@echo "  make dev-clean         Stop and remove all containers"
	@echo "  make dev-logs          View application logs"
	@echo ""
	@echo "✅  TESTING & VALIDATION:"
	@echo "  make test              Run all tests"
	@echo "  make test-backend      Test backend only"
	@echo "  make test-frontend     Test frontend only"
	@echo "  make lint              Lint code (Python + JavaScript)"
	@echo ""
	@echo "📦  DATABASE:"
	@echo "  make db-init           Initialize database schema"
	@echo "  make db-seed           Seed golden dataset"
	@echo "  make db-reset          Drop and recreate database"
	@echo ""
	@echo "🌐  DEPLOYMENT:"
	@echo "  make deploy-all        Deploy backend + frontend"
	@echo "  make deploy-backend    Deploy to Replit"
	@echo "  make deploy-frontend   Deploy to Vercel"
	@echo ""
	@echo "🧹  CLEANUP:"
	@echo "  make clean             Remove build artifacts, cache"
	@echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DOCUMENTATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

docs:
	@echo "📖 Opening architecture documentation..."
	@open docs/index.html || xdg-open docs/index.html || echo "Open docs/index.html in your browser"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INITIALIZATION (One-time setup)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

init: init-env validate-config setup-backend setup-frontend create-databases
	@echo ""
	@echo "✅ Project initialization complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. make dev              Start development environment"
	@echo "  2. make db-seed          Populate with golden dataset"
	@echo "  3. Open http://localhost:3000 in browser"
	@echo ""

init-env:
	@if [ -f .env.local ]; then \
		echo "ℹ️  .env.local already exists, skipping..."; \
	else \
		echo "📝 Creating .env.local from template..."; \
		if [ -f .env.example ]; then \
			cp .env.example .env.local; \
			echo "✅ Created .env.local"; \
			echo ""; \
			echo "⚠️  IMPORTANT: Edit .env.local with your API keys:"; \
			echo "   - ANTHROPIC_API_KEY"; \
			echo "   - OPENAI_API_KEY"; \
			echo "   - PINECONE_API_KEY"; \
			echo "   - SUPABASE_URL and SUPABASE_KEY"; \
		else \
			echo "❌ .env.example not found!"; \
			exit 1; \
		fi; \
	fi

validate-config:
	@echo "🔍 Validating configuration..."
	@bash scripts/validate-config.sh || exit 1
	@echo "✅ Configuration valid!"

setup-backend:
	@echo "🔧 Setting up backend..."
	@bash scripts/setup-backend.sh

setup-frontend:
	@echo "🔧 Setting up frontend..."
	@bash scripts/setup-frontend.sh

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DEVELOPMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

dev: validate-config
	@echo "🚀 Starting development environment..."
	@docker-compose -f docker-compose.dev.yml up

dev-stop:
	@echo "⏹️  Stopping development environment..."
	@docker-compose -f docker-compose.dev.yml stop

dev-clean:
	@echo "🧹 Removing all containers and data..."
	@docker-compose -f docker-compose.dev.yml down -v
	@echo "✅ Clean!"

dev-logs:
	@docker-compose -f docker-compose.dev.yml logs -f

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATABASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

create-databases:
	@echo "🗄️  Creating databases..."
	@bash scripts/create-databases.sh

db-init:
	@echo "📊 Initializing database schema..."
	@bash scripts/db-init.sh

db-seed:
	@echo "🌱 Seeding golden dataset..."
	@python scripts/seed_golden_dataset.py

db-reset: dev-clean db-init db-seed
	@echo "✅ Database reset complete!"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTING & VALIDATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

test: test-backend test-frontend
	@echo "✅ All tests passed!"

test-backend:
	@echo "🧪 Testing backend..."
	@cd backend && pytest tests/ -v

test-frontend:
	@echo "🧪 Testing frontend..."
	@cd frontend && npm run test

lint:
	@echo "🔍 Linting code..."
	@bash scripts/lint.sh

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DEPLOYMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

deploy-all: validate-config deploy-backend deploy-frontend
	@echo ""
	@echo "✅ Deployment complete!"
	@echo ""
	@echo "Live URLs:"
	@bash scripts/print-deployment-urls.sh

deploy-backend:
	@echo "🚀 Deploying backend to Replit..."
	@bash scripts/deploy-replit.sh

deploy-frontend:
	@echo "🚀 Deploying frontend to Vercel..."
	@bash scripts/deploy-vercel.sh

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLEANUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

clean:
	@echo "🧹 Cleaning up..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name ".DS_Store" -delete
	@echo "✅ Cleaned!"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONVENIENCE TARGETS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

setup-all: init dev

# Default target
.DEFAULT_GOAL := help
