.PHONY: help start stop llm app clean logs kill

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help:
	@echo "$(BLUE)Recall App - Available Commands$(NC)"
	@echo ""
	@echo "$(GREEN)make start$(NC)      - Start LiteLLM proxy + Recall app (recommended)"
	@echo "$(GREEN)make llm$(NC)        - Start only LiteLLM proxy"
	@echo "$(GREEN)make app$(NC)        - Start only Recall app"
	@echo "$(GREEN)make stop$(NC)       - Stop all processes"
	@echo "$(GREEN)make kill$(NC)       - Force kill all processes"
	@echo "$(GREEN)make logs$(NC)       - Show running processes"
	@echo "$(GREEN)make clean$(NC)      - Clean up runtime data and caches"
	@echo "$(GREEN)make reset$(NC)      - Reset demo data (fresh start)"
	@echo ""
	@echo "$(BLUE)URLs:$(NC)"
	@echo "  Recall Dashboard: http://127.0.0.1:8501"
	@echo "  Club Portal:      http://127.0.0.1:8101"
	@echo "  Class Booking:    http://127.0.0.1:8102"
	@echo "  Member Offers:    http://127.0.0.1:8103"
	@echo ""

start: stop llm-bg app
	@echo "$(GREEN)✓ Recall app is running!$(NC)"
	@echo "  Dashboard: http://127.0.0.1:8501"
	@sleep 2

llm-bg:
	@echo "$(BLUE)Starting LiteLLM proxy...$(NC)"
	@nohup litellm --model ollama/phi > .litellm.log 2>&1 &
	@echo "$$!" > .litellm.pid
	@sleep 2
	@echo "$(GREEN)✓ LiteLLM running on localhost:4000$(NC)"

llm:
	@echo "$(BLUE)Starting LiteLLM proxy (foreground)...$(NC)"
	@echo "$(RED)Press Ctrl+C to stop$(NC)"
	@litellm --model ollama/phi

app:
	@echo "$(BLUE)Starting Recall app...$(NC)"
	@python3 run_demo.py

stop:
	@echo "$(BLUE)Stopping all processes...$(NC)"
	@if [ -f .litellm.pid ]; then \
		kill $$(cat .litellm.pid) 2>/dev/null || true; \
		rm -f .litellm.pid; \
		echo "$(GREEN)✓ LiteLLM stopped$(NC)"; \
	fi
	@pkill -f "streamlit run app.py" 2>/dev/null || true
	@pkill -f "withdrawal.service_app" 2>/dev/null || true
	@echo "$(GREEN)✓ All processes stopped$(NC)"

kill:
	@echo "$(RED)Force killing all processes...$(NC)"
	@pkill -9 -f litellm 2>/dev/null || true
	@pkill -9 -f streamlit 2>/dev/null || true
	@pkill -9 -f withdrawal 2>/dev/null || true
	@rm -f .litellm.pid .litellm.log
	@echo "$(GREEN)✓ All processes killed$(NC)"

logs:
	@echo "$(BLUE)Running processes:$(NC)"
	@ps aux | grep -E "(litellm|streamlit|withdrawal)" | grep -v grep || echo "$(RED)No processes running$(NC)"
	@echo ""
	@if [ -f .litellm.log ]; then \
		echo "$(BLUE)LiteLLM log (last 10 lines):$(NC)"; \
		tail -10 .litellm.log; \
	fi

clean:
	@echo "$(BLUE)Cleaning up...$(NC)"
	@rm -rf .runtime __pycache__ .pytest_cache *.pyc
	@rm -f .litellm.log .litellm.pid
	@echo "$(GREEN)✓ Cleaned$(NC)"

reset:
	@echo "$(RED)Resetting demo data (fresh start)...$(NC)"
	@make kill
	@make clean
	@echo "$(GREEN)✓ Ready for fresh start$(NC)"
	@echo "Run: $(BLUE)make start$(NC)"
